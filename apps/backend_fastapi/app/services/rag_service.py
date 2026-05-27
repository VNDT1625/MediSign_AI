from __future__ import annotations

import json
import math
import re
import threading
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.config import settings


TOKEN_RE = re.compile(r"[0-9a-zA-ZÀ-ỹ]+", re.UNICODE)

MEDICAL_SYNONYMS: dict[str, tuple[str, ...]] = {
    "panadol": ("paracetamol", "acetaminophen"),
    "hapacol": ("paracetamol", "acetaminophen"),
    "efferalgan": ("paracetamol", "acetaminophen"),
    "tylenol": ("paracetamol", "acetaminophen"),
    "ruou": ("bia", "con", "alcohol"),
    "sot": ("nhiet", "nong", "febrile"),
    "cam": ("cum", "virus", "ho", "sot"),
    "bao tu": ("da day", "thuong vi", "tieu hoa"),
    "dau hong": ("viem hong", "ho", "nuot dau"),
    "kho tho": ("ho hap", "cap cuu"),
    "dau nguc": ("tim mach", "cap cuu"),
    "khong muon song": ("tu hai", "khung hoang", "cap cuu"),
    "canxi": ("calcium",),
    "sat": ("iron",),
    "kem": ("zinc",),
    "vitamin d": ("vitamin_d",),
}


@dataclass(frozen=True)
class RAGDocument:
    record_id: str
    type: str
    title: str
    content: str
    aliases: tuple[str, ...]
    source: dict[str, Any]
    structured: dict[str, Any]
    confidence: str
    needs_medical_review: bool
    token_counts: Counter[str]
    length: int


@dataclass(frozen=True)
class RAGHit:
    record_id: str
    type: str
    title: str
    content: str
    score: float
    confidence: str
    needs_medical_review: bool
    source: dict[str, Any]
    structured: dict[str, Any]


class RAGService:
    """Production-ready local RAG over the generated MediSign knowledge base.

    The service intentionally avoids heavyweight vector dependencies inside the
    FastAPI process. It builds a deterministic BM25-style sparse index from the
    post-training knowledge base and can be swapped later for a remote vector DB
    without changing API contracts.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._docs: list[RAGDocument] = []
        self._idf: dict[str, float] = {}
        self._avg_doc_len = 1.0
        self._loaded_path: Path | None = None
        self._loaded_mtime: float | None = None

    def status(self) -> dict[str, Any]:
        self._ensure_loaded()
        with self._lock:
            return {
                "enabled": settings.rag_enabled,
                "knowledge_base_path": str(self._loaded_path or self._resolve_kb_path()),
                "documents": len(self._docs),
                "index_terms": len(self._idf),
                "ready": settings.rag_enabled and bool(self._docs),
            }

    def rebuild(self) -> dict[str, Any]:
        with self._lock:
            self._loaded_mtime = None
        self._ensure_loaded(force=True)
        return self.status()

    def search(
        self,
        query: str,
        top_k: int | None = None,
        adapter: str = "medical",
        kind_filter: set[str] | None = None,
    ) -> list[RAGHit]:
        """Search the knowledge base with BM25 scoring.

        Args:
            query: The search query string.
            top_k: Maximum number of results to return.
            adapter: Adapter type for scoring adjustments ("medical" or "psychology").
            kind_filter: Optional set of document types to restrict results to
                (e.g. {"disease", "evidence"}). When provided, only documents whose
                ``type`` field is in this set are returned.
        """
        if not settings.rag_enabled or not query.strip():
            return []

        self._ensure_loaded()
        query_tokens = self._expand_tokens(self._tokenize(query))
        if not query_tokens:
            return []

        limit = max(1, min(top_k or settings.rag_default_top_k, 20))
        query_counter = Counter(query_tokens)

        with self._lock:
            scored = [
                (self._score_document(doc, query_counter, query, adapter), doc)
                for doc in self._docs
                if kind_filter is None or doc.type in kind_filter
            ]

        hits = [
            self._to_hit(doc, score)
            for score, doc in sorted(scored, key=lambda item: item[0], reverse=True)
            if score >= settings.rag_min_score
        ]
        return hits[:limit]

    def build_context(
        self, hits: list[RAGHit] | list[dict[str, Any]], max_chars: int | None = None
    ) -> str:
        """Build a context string from RAGHit objects or plain dicts.

        Accepts either a list of ``RAGHit`` dataclass instances (existing usage)
        or a list of plain dicts with keys ``record_id``, ``type``, ``title``,
        ``content``, ``confidence``, ``needs_medical_review``, ``source``
        (used by OARSPromptLayer and other services that pass raw records).
        """
        budget = max_chars or settings.rag_max_context_chars
        sections: list[str] = []
        used = 0
        for idx, item in enumerate(hits, start=1):
            if isinstance(item, dict):
                record_id = str(item.get("record_id") or item.get("id") or "")
                doc_type = str(item.get("type") or item.get("kind") or "knowledge")
                title = str(item.get("title") or record_id)
                content = str(item.get("content") or "")
                confidence = str(item.get("confidence") or "medium")
                needs_review = bool(item.get("needs_medical_review"))
                source_dict = item.get("source") if isinstance(item.get("source"), dict) else {}
            else:
                record_id = item.record_id
                doc_type = item.type
                title = item.title
                content = item.content
                confidence = item.confidence
                needs_review = item.needs_medical_review
                source_dict = item.source

            source_name = source_dict.get("name") or source_dict.get("type") or "MediSign KB"
            review = "can_bac_si_kiem_duyet" if needs_review else "tham_khao"
            block = (
                f"[{idx}] record_id={record_id}; type={doc_type}; title={title}; "
                f"confidence={confidence}; review={review}; source={source_name}\n"
                f"{content.strip()}"
            )
            if used + len(block) > budget:
                remaining = max(0, budget - used)
                if remaining > 200:
                    sections.append(block[:remaining].rstrip())
                break
            sections.append(block)
            used += len(block)
        return "\n\n".join(sections)

    def _ensure_loaded(self, force: bool = False) -> None:
        path = self._resolve_kb_path()
        mtime = path.stat().st_mtime if path.exists() else None
        with self._lock:
            if not force and self._loaded_path == path and self._loaded_mtime == mtime:
                return

        docs = self._load_documents(path)
        idf, avg_doc_len = self._build_idf(docs)

        with self._lock:
            self._docs = docs
            self._idf = idf
            self._avg_doc_len = avg_doc_len
            self._loaded_path = path
            self._loaded_mtime = mtime

    def _resolve_kb_path(self) -> Path:
        configured = Path(settings.rag_knowledge_base_path)
        if configured.is_absolute():
            return configured

        candidates = [
            Path.cwd() / configured,
            Path(__file__).resolve().parents[4] / configured,
            Path(__file__).resolve().parents[2] / configured,
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return candidates[0]

    def _load_documents(self, path: Path) -> list[RAGDocument]:
        if not path.exists():
            return []

        size_mb = path.stat().st_size / 1024**2

        # Always include lightweight files (vietnam_common_diseases, symptom_phrases, etc.)
        # alongside the main KB, regardless of main KB size.
        items: list[dict[str, Any]] = []

        # Load main KB
        if size_mb > 200:
            # Very large file → stream parse one record at a time
            items.extend(self._stream_parse_jsonl_array(path))
        else:
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise ValueError(f"Failed to load RAG KB at {path}: {exc}") from exc
            if not isinstance(raw, list):
                raise ValueError(f"RAG knowledge base must be a JSON list: {path}")
            items.extend(item for item in raw if isinstance(item, dict))

        # Always merge lightweight files
        items.extend(self._load_lightweight_items(path.parent))

        return self._items_to_documents(items)

    def _stream_parse_jsonl_array(self, path: Path) -> list[dict[str, Any]]:
        """Stream-parse a JSON array of objects (one record at a time).

        Avoids loading 700MB+ into memory at once. Uses a depth-tracking parser
        on the raw bytes so we can yield records as soon as their closing `}` is
        found.
        """
        items: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8", errors="replace") as f:
            buffer = ""
            depth = 0
            in_str = False
            esc = False
            start = -1
            seen_open_bracket = False
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                buffer += chunk
                i = 0
                while i < len(buffer):
                    c = buffer[i]
                    if not seen_open_bracket:
                        if c == "[":
                            seen_open_bracket = True
                        i += 1
                        continue
                    if esc:
                        esc = False
                    elif c == "\\":
                        esc = True
                    elif c == '"':
                        in_str = not in_str
                    elif not in_str:
                        if c == "{":
                            if depth == 0:
                                start = i
                            depth += 1
                        elif c == "}":
                            depth -= 1
                            if depth == 0 and start >= 0:
                                obj_str = buffer[start:i + 1]
                                try:
                                    obj = json.loads(obj_str)
                                    if isinstance(obj, dict):
                                        items.append(obj)
                                except json.JSONDecodeError:
                                    pass
                                start = -1
                    i += 1
                # Trim parsed prefix to keep buffer bounded
                if depth == 0 and start < 0:
                    buffer = buffer[i:]
        return items

    def _load_lightweight_items(self, kb_dir: Path) -> list[dict[str, Any]]:
        """Load supplementary KB files (always included)."""
        items: list[dict[str, Any]] = [
            {
                "id": "drug_interaction:paracetamol:alcohol",
                "type": "drug_interaction",
                "title": "Paracetamol / Panadol và rượu",
                "aliases": ["Panadol", "paracetamol", "acetaminophen", "rượu", "alcohol"],
                "content": (
                    "Paracetamol, Panadol hoặc acetaminophen có thể tăng nguy cơ độc gan "
                    "khi dùng cùng rượu/bia. Cần tránh uống rượu khi đang dùng thuốc này "
                    "và hỏi bác sĩ nếu có bệnh gan hoặc dùng quá liều."
                ),
                "confidence": "high",
                "source": {"name": "MediSign built-in safety note"},
                "structured": {"severity": "medium"},
            }
        ]
        for filename in (
            "nutrition_requirements_by_age.json",
            "vietnam_common_diseases.json",
            "vietnam_diseases_full.json",       # ICD-10 enriched (17K diseases)
            "vietnamese_symptom_phrases.json",
            "public_guideline_chunks.json",
        ):
            candidate = kb_dir / filename
            if not candidate.exists():
                continue
            # raised limit: 200MB — vietnam_diseases_full.json có thể ~50-100MB
            if candidate.stat().st_size > 200 * 1024 * 1024:
                continue
            try:
                raw = json.loads(candidate.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(raw, list):
                items.extend(item for item in raw if isinstance(item, dict))
        return items

    def _load_lightweight_documents(self, kb_dir: Path) -> list[RAGDocument]:
        """Backwards-compat wrapper kept for tests that call this directly."""
        return self._items_to_documents(self._load_lightweight_items(kb_dir))

    def _items_to_documents(self, raw: list[dict[str, Any]]) -> list[RAGDocument]:
        docs: list[RAGDocument] = []
        seen: set[str] = set()
        for item in raw:
            if not isinstance(item, dict):
                continue
            record_id = str(item.get("id") or "").strip()
            content = str(item.get("content") or "").strip()
            if not record_id or not content or record_id in seen:
                continue
            seen.add(record_id)

            title = str(item.get("title") or record_id).strip()
            aliases = tuple(
                str(alias).strip() for alias in item.get("aliases") or [] if str(alias).strip()
            )
            weighted_text = " ".join([title, title, " ".join(aliases), content])
            tokens = self._expand_tokens(self._tokenize(weighted_text))
            counts = Counter(tokens)
            docs.append(
                RAGDocument(
                    record_id=record_id,
                    type=str(item.get("type") or "knowledge"),
                    title=title,
                    content=content,
                    aliases=aliases,
                    source=item.get("source") if isinstance(item.get("source"), dict) else {},
                    structured=(
                        item.get("structured") if isinstance(item.get("structured"), dict) else {}
                    ),
                    confidence=str(item.get("confidence") or "medium"),
                    needs_medical_review=bool(item.get("needs_medical_review")),
                    token_counts=counts,
                    length=max(1, sum(counts.values())),
                )
            )
        return docs

    def _build_idf(self, docs: list[RAGDocument]) -> tuple[dict[str, float], float]:
        if not docs:
            return {}, 1.0
        doc_freq: Counter[str] = Counter()
        for doc in docs:
            doc_freq.update(doc.token_counts.keys())
        total = len(docs)
        idf = {
            token: math.log(1 + (total - freq + 0.5) / (freq + 0.5))
            for token, freq in doc_freq.items()
        }
        avg_len = sum(doc.length for doc in docs) / total
        return idf, max(avg_len, 1.0)

    def _score_document(
        self, doc: RAGDocument, query_counter: Counter[str], raw_query: str, adapter: str
    ) -> float:
        k1 = 1.5
        b = 0.75
        score = 0.0
        for token, qf in query_counter.items():
            tf = doc.token_counts.get(token, 0)
            if not tf:
                continue
            idf = self._idf.get(token, 0.0)
            denom = tf + k1 * (1 - b + b * doc.length / self._avg_doc_len)
            score += idf * (tf * (k1 + 1) / denom) * min(qf, 3)

        normalized_query = self._normalize(raw_query)
        title_alias_text = self._normalize(" ".join([doc.title, *doc.aliases]))
        if normalized_query and normalized_query in title_alias_text:
            score += 3.0

        if adapter == "psychology" and doc.type in {"vietnamese_symptom_phrase"}:
            score *= 1.15
        if adapter == "medical" and doc.type in {
            "drug",
            "drug_interaction",
            "nutrition_requirement",
            "vietnam_common_disease",
        }:
            score *= 1.12

        if doc.confidence == "high":
            score *= 1.05
        elif doc.confidence == "low":
            score *= 0.92

        return score

    def _to_hit(self, doc: RAGDocument, score: float) -> RAGHit:
        return RAGHit(
            record_id=doc.record_id,
            type=doc.type,
            title=doc.title,
            content=doc.content,
            score=round(score, 4),
            confidence=doc.confidence,
            needs_medical_review=doc.needs_medical_review,
            source=doc.source,
            structured=doc.structured,
        )

    def _expand_tokens(self, tokens: list[str]) -> list[str]:
        expanded = list(tokens)
        joined = " ".join(tokens)
        for phrase, synonyms in MEDICAL_SYNONYMS.items():
            phrase_tokens = self._tokenize(phrase)
            phrase_key = " ".join(phrase_tokens)
            if phrase_key and phrase_key in joined:
                for synonym in synonyms:
                    expanded.extend(self._tokenize(synonym))
        return expanded

    def _tokenize(self, value: str) -> list[str]:
        normalized = self._normalize(value)
        return [token for token in TOKEN_RE.findall(normalized) if len(token) > 1]

    def _normalize(self, value: str) -> str:
        text = unicodedata.normalize("NFD", value.lower())
        text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
        text = text.replace("đ", "d")
        return re.sub(r"\s+", " ", text).strip()


rag_service = RAGService()
