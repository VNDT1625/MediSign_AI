from __future__ import annotations

import asyncio
import json
import logging
import math
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Iterable

import httpx

from app.core.config import settings
from app.schemas.diagnostic import (
    ConclusionEvidence,
    DiagnosticState,
    DiscriminativeQuestion,
    PersonalContext,
    RankedDisease,
    SelfCheckResult,
)
from app.services.disease_symptom_graph import DiseaseSymptomGraph
from app.services.embedding_client import EmbeddingClient, EmbeddingUnavailableError
from app.services.kb_lazy_loader import KB_MISS_THRESHOLD, KBLazyLoader, KBSearchTimeoutError
from app.services.rag_service import MEDICAL_SYNONYMS, RAGHit, RAGService

logger = logging.getLogger(__name__)


@dataclass
class FusedHit:
    record_id: str
    score: float = 0.0
    ranks: dict[str, int] = field(default_factory=dict)
    sources: set[str] = field(default_factory=set)
    payload: Any | None = None


@dataclass
class SymptomScore:
    symptom: str
    score: float
    expected_in: list[str]
    expected_absent_in: list[str]
    sources: list[str]


class RAGEngine:
    def __init__(
        self,
        sparse: RAGService,
        embedder: EmbeddingClient,
        graph: DiseaseSymptomGraph,
        lazy_loader: KBLazyLoader | None = None,
    ) -> None:
        self.sparse = sparse
        self.embedder = embedder
        self.graph = graph
        self.lazy_loader = lazy_loader

    async def retrieve_initial(
        self,
        query: str,
        personal_ctx: PersonalContext,
        top_k: int = 10,
        db: Any | None = None,
    ) -> list[RankedDisease]:
        rewritten = self._rewrite_query(query)
        dense_hits: list[Any] = []
        degradation: dict[str, Any] | None = None

        sparse_task = asyncio.to_thread(self.sparse.search, rewritten, top_k * 2, "medical")
        dense_task = self._maybe_await(self.embedder.search(rewritten, top_k * 2, kind="disease"))

        sparse_result, dense_result = await asyncio.gather(
            sparse_task,
            dense_task,
            return_exceptions=True,
        )

        if isinstance(sparse_result, Exception):
            logger.warning("Sparse RAG retrieval failed: %s", sparse_result)
            bm25_hits: list[Any] = []
        else:
            bm25_hits = list(sparse_result)

        if isinstance(dense_result, EmbeddingUnavailableError):
            degradation = dense_result.metadata
            logger.warning("Dense RAG unavailable, degrading to BM25-only: %s", degradation)
        elif isinstance(dense_result, Exception):
            degradation = {"degraded": True, "reason": "embedding_unavailable"}
            logger.warning("Dense RAG failed, degrading to BM25-only: %s", dense_result)
        else:
            dense_hits = list(dense_result)

        fused = self._rrf_merge(bm25_hits, dense_hits, k=60)
        candidates = self._to_disease_candidates(fused)

        # KBLazyLoader activation: when KB has no relevant results
        if self.lazy_loader is not None and db is not None:
            max_score = max((c.probability for c in candidates), default=0.0)
            if not candidates or max_score < KB_MISS_THRESHOLD:
                try:
                    lazy_candidates = await self.lazy_loader.search_and_enrich(query, db)
                    if lazy_candidates:
                        candidates = lazy_candidates
                        logger.info(
                            "KBLazyLoader activated: %d candidates from MedGemma search",
                            len(candidates),
                        )
                except KBSearchTimeoutError:
                    logger.warning("KBLazyLoader timed out for query: %s", query[:100])
                    raise
                except Exception as exc:
                    logger.warning("KBLazyLoader failed: %s", exc)

        if degradation:
            candidates = [self._with_degradation(candidate, degradation) for candidate in candidates]

        if self._has_personal_context(personal_ctx):
            candidates = self._rerank_with_context(candidates, personal_ctx)

        return self._softmax_topk(candidates, top_k)

    async def retrieve_differential(
        self,
        candidates: list[RankedDisease],
        symptoms_known: list[str],
    ) -> DiscriminativeQuestion:
        if len(candidates) < 2:
            raise ValueError("retrieve_differential requires at least two candidate diseases")

        edges = await self._maybe_await(self.graph.edges_for(candidates[:5]))
        scored = self._discriminative_scores(list(edges or []), candidates[:5], symptoms_known)
        top = self._compress(scored, k=3)

        if not top:
            return self._fallback_question(candidates, symptoms_known)

        known = {self._normalize(symptom) for symptom in symptoms_known}
        best = next((item for item in top if self._normalize(item.symptom) not in known), None)
        if best is None:
            return self._fallback_question(candidates, symptoms_known)

        return DiscriminativeQuestion(
            symptom=best.symptom,
            question=f"Bạn có đang gặp {best.symptom} không?",
            expected_in=best.expected_in,
            expected_absent_in=best.expected_absent_in,
            metadata={"sources": best.sources, "score": best.score},
        )

    async def retrieve_conclusion(self, top_disease: RankedDisease) -> ConclusionEvidence:
        queries = [
            f"{top_disease.name} mức độ nguy hiểm biến chứng dấu hiệu nặng",
            f"{top_disease.name} xét nghiệm chẩn đoán",
            f"{top_disease.name} chăm sóc tại nhà điều trị theo dõi",
        ]
        chunks = await asyncio.gather(
            *[self._hybrid_retrieve(query, top_k=3, kind_filter="evidence") for query in queries]
        )
        evidence = self._compose_evidence(top_disease, chunks)
        if top_disease.severity == "high" and not evidence.red_flags:
            logger.warning("High severity disease %s has no retrieved red flags", top_disease.name)
            evidence.needs_test = True
        return evidence

    async def self_check(
        self,
        state: DiagnosticState,
        evidence: ConclusionEvidence,
    ) -> SelfCheckResult:
        if settings.ai_provider not in {"openai_compatible", "medgemma_server"}:
            return SelfCheckResult(
                supports_conclusion=not evidence.needs_test,
                missing_evidence=["red_flags"] if evidence.needs_test else [],
                contradictions=[],
            )

        prompt = (
            "Bạn là bộ kiểm tra an toàn y khoa. Trả về JSON hợp lệ duy nhất với schema "
            '{"supports_conclusion": bool, "missing_evidence": [str], "contradictions": [str]}.\n'
            f"STATE={state.model_dump(mode='json')}\n"
            f"EVIDENCE={evidence.model_dump(mode='json')}"
        )
        body = {
            "model": settings.ai_medical_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 256,
        }
        headers = {"Content-Type": "application/json"}
        if settings.ai_api_key:
            headers["Authorization"] = f"Bearer {settings.ai_api_key}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{settings.ai_base_url.rstrip('/')}/chat/completions",
                    json=body,
                    headers=headers,
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
            return SelfCheckResult.model_validate_json(self._extract_json(content))
        except Exception as exc:
            logger.warning("Self-check failed, requiring test/escalation: %s", exc)
            return SelfCheckResult(
                supports_conclusion=False,
                missing_evidence=["self_check_unavailable"],
                contradictions=[],
            )

    def _rewrite_query(self, query: str) -> str:
        rewritten = query.strip()
        normalized = self._normalize(rewritten)
        additions: list[str] = []
        for phrase, synonyms in MEDICAL_SYNONYMS.items():
            if self._normalize(phrase) in normalized:
                additions.extend(synonyms)
        if additions:
            rewritten = f"{rewritten} {' '.join(additions)}"
        return rewritten

    def _rrf_merge(
        self,
        bm25_hits: Iterable[Any],
        dense_hits: Iterable[Any],
        k: int = 60,
    ) -> dict[str, FusedHit]:
        fused: dict[str, FusedHit] = {}
        for source_name, hits in (("bm25", bm25_hits), ("dense", dense_hits)):
            for rank, hit in enumerate(hits, start=1):
                record_id = self._hit_record_id(hit)
                if not record_id:
                    continue
                item = fused.setdefault(record_id, FusedHit(record_id=record_id))
                item.score += 1.0 / (k + rank)
                item.ranks[source_name] = rank
                item.sources.add(record_id)
                if item.payload is None or source_name == "bm25":
                    item.payload = hit
        return fused

    def _to_disease_candidates(self, fused: dict[str, FusedHit]) -> list[RankedDisease]:
        candidates: list[RankedDisease] = []
        for item in sorted(fused.values(), key=lambda hit: hit.score, reverse=True):
            payload = item.payload
            record_type = self._hit_type(payload)
            if record_type not in {
                "disease",
                "vietnam_common_disease",
                "common_disease",
                "guideline_chunk",
                "knowledge",
            }:
                continue
            structured = self._hit_structured(payload)
            severity = structured.get("severity") if isinstance(structured, dict) else None
            if severity not in {"low", "medium", "high"}:
                severity = "medium"
            name = self._disease_name(payload, item.record_id)
            sources = sorted(item.sources) or [item.record_id]
            candidates.append(
                RankedDisease(
                    name=name,
                    probability=max(item.score, 0.0),
                    severity=severity,
                    rationale=self._hit_content(payload),
                    sources=sources,
                )
            )
        return candidates

    def _rerank_with_context(
        self,
        candidates: list[RankedDisease],
        personal_ctx: PersonalContext,
    ) -> list[RankedDisease]:
        reranked: list[RankedDisease] = []
        medications = " ".join(med.name for med in personal_ctx.medications).lower()
        conditions = " ".join(personal_ctx.profile.conditions if personal_ctx.profile else []).lower()
        journal = (personal_ctx.recent_journal_summary or "").lower()

        for candidate in candidates:
            multiplier = 1.0
            text = f"{candidate.name} {candidate.rationale or ''}".lower()
            if self._mentions_antibiotic(medications):
                if "kháng thuốc" in text or "resistance" in text:
                    multiplier *= 1.2
                if "vi khuẩn" in text or "bacterial" in text:
                    multiplier *= 0.8
            if "diabetes" in conditions or "tiểu đường" in conditions or "dai thao duong" in conditions:
                if "cơ hội" in text or "opportunistic" in text or "nhiễm trùng" in text:
                    multiplier *= 1.3
            if "mệt 1 tuần" in journal or "met 1 tuan" in self._normalize(journal):
                if "mạn" in text or "chronic" in text:
                    multiplier *= 1.2
                if "cấp" in text or "acute" in text:
                    multiplier *= 0.9
            reranked.append(candidate.model_copy(update={"probability": candidate.probability * multiplier}))
        return reranked

    def _softmax_topk(self, candidates: list[RankedDisease], top_k: int) -> list[RankedDisease]:
        top = sorted(candidates, key=lambda disease: disease.probability, reverse=True)[
            : max(1, top_k)
        ]
        if not top:
            return []
        max_score = max(disease.probability for disease in top)
        weights = [math.exp(disease.probability - max_score) for disease in top]
        total = sum(weights) or 1.0
        normalized = [
            disease.model_copy(update={"probability": weight / total})
            for disease, weight in zip(top, weights, strict=True)
        ]
        return sorted(normalized, key=lambda disease: disease.probability, reverse=True)

    async def _hybrid_retrieve(
        self,
        query: str,
        top_k: int,
        kind_filter: str = "evidence",
    ) -> list[Any]:
        rewritten = self._rewrite_query(query)
        sparse_task = asyncio.to_thread(self.sparse.search, rewritten, top_k, "medical")
        dense_task = self._maybe_await(self.embedder.search(rewritten, top_k, kind=kind_filter))
        sparse_result, dense_result = await asyncio.gather(
            sparse_task,
            dense_task,
            return_exceptions=True,
        )
        sparse_hits = [] if isinstance(sparse_result, Exception) else list(sparse_result)
        dense_hits = [] if isinstance(dense_result, Exception) else list(dense_result)
        fused = self._rrf_merge(sparse_hits, dense_hits)
        return [item.payload for item in sorted(fused.values(), key=lambda hit: hit.score, reverse=True)]

    def _compose_evidence(
        self,
        top_disease: RankedDisease,
        chunks: list[list[Any]],
    ) -> ConclusionEvidence:
        red_flags: list[str] = []
        lab_tests: list[str] = []
        home_care: list[str] = []
        recommendations: list[str] = []
        sources: list[str] = list(top_disease.sources)

        for hit in [item for group in chunks for item in group if item is not None]:
            record_id = self._hit_record_id(hit)
            if record_id:
                sources.append(record_id)
            structured = self._hit_structured(hit)
            red_flags.extend(self._list_field(structured, "red_flags"))
            lab_tests.extend(self._list_field(structured, "lab_tests"))
            home_care.extend(self._list_field(structured, "home_care"))
            recommendations.extend(self._list_field(structured, "recommendations"))

        return ConclusionEvidence(
            disease_name=top_disease.name,
            severity=top_disease.severity,
            red_flags=self._dedupe(red_flags),
            lab_tests=self._dedupe(lab_tests),
            home_care=self._dedupe(home_care),
            recommendations=self._dedupe(recommendations),
            sources=self._dedupe(sources),
            needs_test=False,
        )

    def _discriminative_scores(
        self,
        edges: list[Any],
        candidates: list[RankedDisease],
        symptoms_known: list[str],
    ) -> list[SymptomScore]:
        known = {self._normalize(symptom) for symptom in symptoms_known}
        candidate_names = [candidate.name for candidate in candidates]
        candidate_prob = {candidate.name: candidate.probability for candidate in candidates}
        by_symptom: dict[str, list[Any]] = {}
        for edge in edges:
            symptom = str(getattr(edge, "symptom", "") or "").strip()
            if not symptom or self._normalize(symptom) in known:
                continue
            by_symptom.setdefault(symptom, []).append(edge)

        scored: list[SymptomScore] = []
        for symptom, symptom_edges in by_symptom.items():
            present = [str(getattr(edge, "disease_id", "")) for edge in symptom_edges]
            present = [disease for disease in present if disease]
            absent = [name for name in candidate_names if name not in present]
            if not present or not absent:
                continue
            p_present = sum(candidate_prob.get(name, 0.0) for name in present)
            p_absent = sum(candidate_prob.get(name, 0.0) for name in absent)
            avg_weight = sum(float(getattr(edge, "weight", 0.0) or 0.0) for edge in symptom_edges)
            avg_weight /= max(1, len(symptom_edges))
            scored.append(
                SymptomScore(
                    symptom=symptom,
                    score=abs(p_present - p_absent) * avg_weight,
                    expected_in=self._dedupe(present),
                    expected_absent_in=self._dedupe(absent),
                    sources=[
                        f"{getattr(edge, 'disease_id', '')}:{symptom}"
                        for edge in symptom_edges
                    ],
                )
            )
        return sorted(scored, key=lambda item: item.score, reverse=True)

    def _compress(self, scored: list[SymptomScore], k: int) -> list[SymptomScore]:
        return scored[: max(1, k)]

    def _fallback_question(
        self,
        candidates: list[RankedDisease],
        symptoms_known: list[str],
    ) -> DiscriminativeQuestion:
        known = {self._normalize(symptom) for symptom in symptoms_known}
        for symptom in ("mức độ nặng tăng nhanh", "sốt kéo dài", "khó thở", "đau ngực"):
            if self._normalize(symptom) not in known:
                chosen = symptom
                break
        else:
            chosen = "triệu chứng mới xuất hiện"

        return DiscriminativeQuestion(
            symptom=chosen,
            question=f"Triệu chứng {chosen} của bạn có xuất hiện hoặc nặng lên không?",
            expected_in=[candidates[0].name],
            expected_absent_in=[candidate.name for candidate in candidates[1:]] or [candidates[0].name],
            metadata={"fallback": True},
        )

    def _has_personal_context(self, personal_ctx: PersonalContext) -> bool:
        return bool(
            personal_ctx.consent_personal_context
            and (
                personal_ctx.profile is not None
                or personal_ctx.medications
                or personal_ctx.recent_journal_summary
            )
        )

    def _with_degradation(self, candidate: RankedDisease, metadata: dict[str, Any]) -> RankedDisease:
        rationale = candidate.rationale or ""
        suffix = f" degradation={metadata.get('reason', 'embedding_unavailable')}"
        return candidate.model_copy(update={"rationale": f"{rationale}{suffix}".strip()})

    async def _maybe_await(self, value: Any) -> Any:
        if hasattr(value, "__await__"):
            return await value
        return value

    def _hit_record_id(self, hit: Any) -> str:
        if isinstance(hit, dict):
            return str(hit.get("record_id") or hit.get("id") or "").strip()
        return str(getattr(hit, "record_id", "") or getattr(hit, "id", "") or "").strip()

    def _hit_type(self, hit: Any) -> str:
        if isinstance(hit, dict):
            return str(hit.get("type") or hit.get("kind") or "disease")
        return str(getattr(hit, "type", None) or getattr(hit, "kind", None) or "disease")

    def _hit_structured(self, hit: Any) -> dict[str, Any]:
        value = hit.get("structured") if isinstance(hit, dict) else getattr(hit, "structured", None)
        return value if isinstance(value, dict) else {}

    def _hit_content(self, hit: Any) -> str | None:
        if isinstance(hit, dict):
            content = hit.get("content")
        else:
            content = getattr(hit, "content", None)
        return str(content)[:500] if content else None

    def _disease_name(self, hit: Any, fallback: str) -> str:
        if isinstance(hit, dict):
            return str(hit.get("title") or hit.get("name") or fallback)
        return str(getattr(hit, "title", None) or getattr(hit, "name", None) or fallback)

    def _list_field(self, value: dict[str, Any], key: str) -> list[str]:
        raw = value.get(key)
        if raw is None:
            return []
        if isinstance(raw, list):
            return [str(item).strip() for item in raw if str(item).strip()]
        text = str(raw).strip()
        return [text] if text else []

    def _dedupe(self, values: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            item = str(value).strip()
            key = self._normalize(item)
            if item and key not in seen:
                seen.add(key)
                result.append(item)
        return result

    def _mentions_antibiotic(self, text: str) -> bool:
        normalized = self._normalize(text)
        terms = ("khang sinh", "antibiotic", "amoxicillin", "azithromycin", "cephalexin")
        return any(term in normalized for term in terms)

    def _extract_json(self, text: str) -> str:
        stripped = text.strip()
        if stripped.startswith("{"):
            return stripped
        match = re.search(r"\{.*\}", stripped, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in self-check response")
        return match.group(0)

    def _normalize(self, value: str) -> str:
        text = unicodedata.normalize("NFD", value.lower())
        text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
        text = text.replace("đ", "d")
        return re.sub(r"\s+", " ", text).strip()
