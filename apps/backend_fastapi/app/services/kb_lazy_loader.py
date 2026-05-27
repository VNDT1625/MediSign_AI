"""KBLazyLoader — on-demand knowledge base enrichment via MedGemma search.

When RAG #1 returns no relevant results (max_score < KB_MISS_THRESHOLD),
this service calls MedGemma 4B to generate structured medical information,
validates it, and upserts into the knowledge base for future retrieval.

Only activates during the "initial" phase — no lazy loading mid-conversation.

Requirements: 19.1, 19.2, 19.3, 19.4, 19.5
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.diagnostic import RankedDisease

logger = logging.getLogger(__name__)

# Threshold below which we consider the KB to have "missed" — trigger lazy loading
KB_MISS_THRESHOLD: float = 0.25


class KBSearchTimeoutError(RuntimeError):
    """Raised when MedGemma search exceeds the 15-second timeout."""

    pass


class KBRecord(BaseModel):
    """Schema for a single record returned by MedGemma search.

    All fields are required for a valid KB entry.
    """

    name: str
    symptoms: list[str] = Field(min_length=1)
    severity: str
    red_flags: list[str] = Field(default_factory=list)
    home_care: list[str] = Field(default_factory=list)
    lab_tests: list[str] = Field(default_factory=list)

    @field_validator("severity")
    @classmethod
    def severity_must_be_valid(cls, v: str) -> str:
        allowed = {"low", "medium", "high"}
        if v not in allowed:
            raise ValueError(f"severity must be one of {allowed}, got '{v}'")
        return v

    @field_validator("name")
    @classmethod
    def name_must_be_non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must be non-empty")
        return v.strip()


class KBLazyLoader:
    """On-demand KB enrichment via MedGemma 4B structured search.

    Workflow:
    1. Call MedGemma with a structured prompt requesting disease info in Vietnamese
    2. Validate and parse the JSON response
    3. Upsert valid records into knowledge_base.json, kb_embeddings, and disease_symptom_edges
    4. Return RankedDisease candidates for immediate use
    """

    def __init__(
        self,
        embedder: Any | None = None,
        timeout_seconds: float = 15.0,
    ) -> None:
        self.embedder = embedder
        self.timeout_seconds = timeout_seconds
        self._last_query: str = ""

    async def search_and_enrich(
        self,
        query: str,
        db: Session,
    ) -> list[RankedDisease]:
        """Search MedGemma for medical info and enrich the KB.

        Args:
            query: The user's symptom description.
            db: SQLAlchemy session for DB upserts.

        Returns:
            List of RankedDisease candidates derived from MedGemma output.

        Raises:
            KBSearchTimeoutError: If MedGemma call exceeds timeout.
        """
        prompt = self._build_search_prompt(query)
        self._last_query = query

        body = {
            "model": settings.ai_medical_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 1024,
        }
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if settings.ai_api_key:
            headers["Authorization"] = f"Bearer {settings.ai_api_key}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{settings.ai_base_url.rstrip('/')}/chat/completions",
                    json=body,
                    headers=headers,
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
        except httpx.TimeoutException as exc:
            raise KBSearchTimeoutError(
                f"MedGemma search timed out after {self.timeout_seconds}s"
            ) from exc
        except Exception as exc:
            logger.warning("KBLazyLoader MedGemma call failed: %s", exc)
            return []

        records = self._validate_and_parse(content)
        if not records:
            return []

        # Upsert to KB for future retrieval
        await self._upsert_to_kb(records, db)

        # Convert to RankedDisease for immediate use
        return self._to_ranked_diseases(records)

    def _build_search_prompt(self, query: str) -> str:
        """Build prompt instructing MedGemma to return structured medical info in Vietnamese."""
        return (
            "Bạn là bác sĩ chuyên khoa. Dựa trên triệu chứng sau, hãy liệt kê các bệnh "
            "có thể liên quan. Trả về JSON array hợp lệ duy nhất, mỗi phần tử có schema:\n"
            '{"name": "tên bệnh", "symptoms": ["triệu chứng 1", ...], '
            '"severity": "low|medium|high", "red_flags": ["dấu hiệu nguy hiểm"], '
            '"home_care": ["hướng dẫn chăm sóc tại nhà"], '
            '"lab_tests": ["xét nghiệm cần thiết"]}\n\n'
            "Yêu cầu:\n"
            "- Trả lời bằng tiếng Việt\n"
            "- Liệt kê 2-5 bệnh có khả năng cao nhất\n"
            "- severity phải là một trong: low, medium, high\n"
            "- red_flags bắt buộc khi severity là high\n"
            "- Chỉ trả về JSON array, không giải thích thêm\n\n"
            f"Triệu chứng: {query}"
        )

    def _validate_and_parse(self, llm_output: str) -> list[KBRecord]:
        """Parse LLM JSON output and validate against KBRecord schema.

        Skips invalid records with a warning log. Returns empty list if all fail.
        """
        # Try to extract JSON array from the response
        raw_json = self._extract_json_array(llm_output)
        if raw_json is None:
            logger.warning("KBLazyLoader: could not extract JSON array from LLM output")
            return []

        try:
            parsed = json.loads(raw_json)
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning("KBLazyLoader: JSON parse failed: %s", exc)
            return []

        if not isinstance(parsed, list):
            # Try wrapping single object in a list
            if isinstance(parsed, dict):
                parsed = [parsed]
            else:
                logger.warning("KBLazyLoader: LLM output is not a list or dict")
                return []

        valid_records: list[KBRecord] = []
        for i, item in enumerate(parsed):
            if not isinstance(item, dict):
                logger.warning("KBLazyLoader: record %d is not a dict, skipping", i)
                continue
            try:
                record = KBRecord.model_validate(item)
                valid_records.append(record)
            except Exception as exc:
                logger.warning("KBLazyLoader: record %d validation failed: %s", i, exc)
                continue

        return valid_records

    async def _upsert_to_kb(self, records: list[KBRecord], db: Session) -> None:
        """Insert valid records into kb_pending_records for admin review.

        Records are NO LONGER written directly to knowledge_base.json.
        They are quarantined in kb_pending_records with status='pending'.
        Admin can approve them via the admin API, which will then promote
        them to the main KB.

        All records are tagged with source_query for traceability.
        """
        from sqlalchemy import and_, select

        from app.database.cloud_models import KBPendingRecord

        for record in records:
            # Skip if already pending for this disease name to avoid duplicates
            existing = db.execute(
                select(KBPendingRecord).where(
                    and_(
                        KBPendingRecord.disease_name == record.name,
                        KBPendingRecord.status == "pending",
                    )
                )
            ).scalar_one_or_none()

            if existing:
                logger.debug(
                    "KBLazyLoader: skipping duplicate pending record for %s", record.name
                )
                continue

            pending = KBPendingRecord(
                source_query=self._last_query,
                disease_name=record.name,
                symptoms=json.dumps(record.symptoms, ensure_ascii=False),
                severity=record.severity,
                red_flags=json.dumps(record.red_flags, ensure_ascii=False),
                home_care=json.dumps(record.home_care, ensure_ascii=False),
                lab_tests=json.dumps(record.lab_tests, ensure_ascii=False),
                status="pending",
            )
            db.add(pending)

        try:
            db.commit()
            logger.info(
                "KBLazyLoader: inserted %d records into kb_pending_records", len(records)
            )
        except Exception as exc:
            logger.warning("KBLazyLoader: failed to insert pending records: %s", exc)
            db.rollback()

    def _to_ranked_diseases(self, records: list[KBRecord]) -> list[RankedDisease]:
        """Convert KBRecords to RankedDisease candidates with equal probability distribution."""
        if not records:
            return []

        # Distribute probability equally, then normalize
        base_prob = 1.0 / len(records)
        candidates: list[RankedDisease] = []
        for i, record in enumerate(records):
            # First record gets slightly higher probability
            prob = base_prob * (1.0 + 0.1 * (len(records) - 1 - i))
            candidates.append(
                RankedDisease(
                    name=record.name,
                    probability=min(1.0, prob),
                    severity=record.severity,
                    rationale=f"Triệu chứng: {', '.join(record.symptoms[:3])}",
                    sources=["medgemma_search"],
                )
            )

        # Normalize probabilities to sum to 1.0
        total = sum(c.probability for c in candidates)
        if total > 0:
            candidates = [
                c.model_copy(update={"probability": c.probability / total})
                for c in candidates
            ]

        return sorted(candidates, key=lambda d: d.probability, reverse=True)

    def _extract_json_array(self, text: str) -> str | None:
        """Extract a JSON array from potentially noisy LLM output."""
        import re

        stripped = text.strip()

        # Try direct parse first — array
        if stripped.startswith("["):
            return stripped

        # Try direct parse — single object (will be wrapped in list by caller)
        if stripped.startswith("{"):
            return f"[{stripped}]"

        # Look for JSON array in markdown code blocks
        match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", stripped, re.DOTALL)
        if match:
            return match.group(1)

        # Look for JSON object in markdown code blocks
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, re.DOTALL)
        if match:
            return f"[{match.group(1)}]"

        # Look for bare JSON array
        match = re.search(r"\[.*\]", stripped, re.DOTALL)
        if match:
            return match.group(0)

        # Look for bare JSON object
        match = re.search(r"\{.*\}", stripped, re.DOTALL)
        if match:
            return f"[{match.group(0)}]"

        return None
