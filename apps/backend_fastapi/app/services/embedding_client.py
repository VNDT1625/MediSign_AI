from __future__ import annotations

import asyncio
import concurrent.futures
import math
from collections.abc import Sequence
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.cloud_models import KBEmbedding

VALID_KINDS = {"disease", "symptom", "evidence"}


class EmbeddingUnavailableError(RuntimeError):
    """Raised when dense retrieval cannot be used."""

    def __init__(self, reason: str = "embedding_unavailable") -> None:
        super().__init__(reason)
        self.metadata = {"degraded": True, "reason": reason}


class EmbeddingClient:
    """Dense retrieval wrapper for sentence-transformers and pgvector.

    The transformer is loaded lazily so importing the FastAPI app does not pull a
    large model into memory unless dense retrieval is actually used.
    """

    model_name = "intfloat/multilingual-e5-small"
    dimensions = 384

    def __init__(
        self,
        db: Session | None = None,
        model: Any | None = None,
        timeout_seconds: float = 5.0,
    ) -> None:
        self.db = db
        self._model = model
        self.timeout_seconds = timeout_seconds
        self.last_degradation: dict[str, Any] | None = None
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="embedding-client",
        )

    @property
    def model(self) -> Any:
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except Exception as exc:  # pragma: no cover - depends on optional runtime package
                raise EmbeddingUnavailableError("embedding_unavailable") from exc
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, text: str) -> list[float]:
        if not text.strip():
            raise EmbeddingUnavailableError("embedding_unavailable")

        future = self._executor.submit(self.model.encode, text, normalize_embeddings=True)
        try:
            vector = future.result(timeout=self.timeout_seconds)
        except concurrent.futures.TimeoutError as exc:
            future.cancel()
            raise EmbeddingUnavailableError("embedding_unavailable") from exc
        except Exception as exc:
            raise EmbeddingUnavailableError("embedding_unavailable") from exc

        values = vector.tolist() if hasattr(vector, "tolist") else list(vector)
        if len(values) != self.dimensions:
            raise EmbeddingUnavailableError("embedding_dimension_mismatch")
        return [float(value) for value in values]

    def close(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)

    async def search(self, query: str, top_k: int, kind: str = "disease") -> list[dict[str, Any]]:
        if kind not in VALID_KINDS:
            raise ValueError(f"kind must be one of {sorted(VALID_KINDS)}")
        if not query.strip():
            return []
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self._search_sync, query, top_k, kind),
                timeout=self.timeout_seconds,
            )
        except asyncio.TimeoutError as exc:
            raise EmbeddingUnavailableError("embedding_unavailable") from exc

    def _search_sync(self, query: str, top_k: int, kind: str) -> list[dict[str, Any]]:
        embedding = self.encode(query)
        if self.db is None:
            raise EmbeddingUnavailableError("pgvector_unavailable")

        try:
            self.last_degradation = None
            self._set_statement_timeout()
            distance = KBEmbedding.embedding.cosine_distance(embedding)
            rows = self.db.execute(
                select(KBEmbedding.record_id, KBEmbedding.kind, distance.label("distance"))
                .where(KBEmbedding.kind == kind)
                .order_by(distance)
                .limit(max(1, top_k))
            ).all()
        except SQLAlchemyError as exc:
            if not self._is_pgvector_unavailable(exc):
                raise EmbeddingUnavailableError("embedding_unavailable") from exc
            self._rollback_after_failed_statement()
            self.last_degradation = {"degraded": True, "reason": "pgvector_unavailable"}
            return self._search_in_process(embedding, top_k, kind)

        return [
            {
                "record_id": row.record_id,
                "kind": row.kind,
                "score": max(0.0, 1.0 - float(row.distance or 0.0)),
            }
            for row in rows
        ]

    def _search_in_process(
        self,
        query_embedding: list[float],
        top_k: int,
        kind: str,
    ) -> list[dict[str, Any]]:
        if self.db is None:
            raise EmbeddingUnavailableError("pgvector_unavailable")
        try:
            rows = self.db.execute(
                select(KBEmbedding.record_id, KBEmbedding.kind, KBEmbedding.embedding).where(
                    KBEmbedding.kind == kind
                )
            ).all()
        except SQLAlchemyError as exc:
            raise EmbeddingUnavailableError("pgvector_unavailable") from exc

        metadata = {"degraded": True, "reason": "pgvector_unavailable"}
        results = [
            {
                "record_id": row.record_id,
                "kind": row.kind,
                "score": self._cosine_similarity(
                    query_embedding,
                    self._coerce_vector(row.embedding),
                ),
                "metadata": metadata,
            }
            for row in rows
        ]
        results.sort(key=lambda item: item["score"], reverse=True)
        return results[: max(1, top_k)]

    def _coerce_vector(self, value: Any) -> list[float]:
        if hasattr(value, "tolist"):
            value = value.tolist()
        if isinstance(value, str):
            raw = value.strip().removeprefix("[").removesuffix("]")
            return [float(part) for part in raw.split(",") if part.strip()]
        if isinstance(value, Sequence):
            return [float(part) for part in value]
        return []

    def _cosine_similarity(self, left: list[float], right: list[float]) -> float:
        if len(left) != self.dimensions or len(right) != self.dimensions:
            return 0.0
        dot = sum(a * b for a, b in zip(left, right, strict=True))
        left_norm = math.sqrt(sum(a * a for a in left))
        right_norm = math.sqrt(sum(b * b for b in right))
        if left_norm == 0.0 or right_norm == 0.0:
            return 0.0
        return max(0.0, min(1.0, dot / (left_norm * right_norm)))

    def _is_pgvector_unavailable(self, exc: BaseException) -> bool:
        text = str(exc).lower()
        return any(
            marker in text
            for marker in (
                "operator does not exist",
                "type \"vector\" does not exist",
                "undefinedfunction",
                "undefinedobject",
                "vector extension",
                "no such function",
            )
        )

    def _rollback_after_failed_statement(self) -> None:
        if self.db is None:
            return
        try:
            self.db.rollback()
        except SQLAlchemyError:
            pass

    def _set_statement_timeout(self) -> None:
        if self.db is None:
            return
        bind = self.db.get_bind()
        if bind.dialect.name != "postgresql":
            return
        timeout_ms = max(1, int(self.timeout_seconds * 1000))
        self.db.execute(text("SET LOCAL statement_timeout = :timeout_ms"), {"timeout_ms": timeout_ms})
