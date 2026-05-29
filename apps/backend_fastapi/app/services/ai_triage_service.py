"""AI-powered triage service.

ARCHITECTURE
============
Backend FastAPI là **thin client**, KHÔNG load model trực tiếp. Mọi cuộc gọi
AI đi qua AI server cloud OpenAI-compatible:

    Backend (port 8000) ──httpx──> AI Server (cloud, /v1/chat/completions)
                                    └── MedGemma 4B + medical adapter

Triage có 3 tầng:
    TIER 1 — Rule-based (luôn chạy trước, fast path cho emergency).
    TIER 2 — MedGemma medical adapter (chỉ gọi cho non-emergency, qua AI server).
    TIER 3 — Rule-based fallback (khi AI server lỗi/không cấu hình).

Cấu hình AI server qua biến môi trường:
    BACKEND_AI_PROVIDER          rule_based | openai_compatible | medgemma_server
    BACKEND_AI_BASE_URL          URL AI server (vd: https://ai.example.com/v1)
    BACKEND_AI_MEDICAL_MODEL     model name khi gọi (vd: medisign-medgemma-medical)
    BACKEND_AI_API_KEY           bearer token nếu AI server yêu cầu

Khi `ai_provider == "rule_based"` hoặc AI server không khả dụng, service vẫn
chạy đầy đủ bằng rule-based fallback.
"""
from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.core.config import settings
from app.schemas.triage import TriageRequest, TriageResponse
from app.services.text_processing import find_phrase_starts, tokenize

logger = logging.getLogger(__name__)


# Emergency detection (rule-based for fast path)
_EMERGENCY_PHRASES = (
    ("kho", "tho"),
    ("dau", "nguc"),
    ("ngat",),
    ("chet", "nguon"),
)
_URGENT_PHRASES = (
    ("sot", "cao"),
    ("dau", "nhieu"),
    ("met", "moi"),
    ("buon", "non"),
)
_NEGATION_TOKENS = {"khong", "ko", "chua", "khongco"}


def _has_non_negated_phrase(tokens: list[str], phrase_tokens: tuple[str, ...]) -> bool:
    for start in find_phrase_starts(tokens, list(phrase_tokens)):
        left_window = tokens[max(0, start - 4) : start]
        if any(token in _NEGATION_TOKENS for token in left_window):
            continue
        return True
    return False


def _classify_urgency_rule_based(symptom_text: str) -> str:
    """Fast rule-based urgency classification."""
    tokens = tokenize(symptom_text)

    if any(_has_non_negated_phrase(tokens, phrase) for phrase in _EMERGENCY_PHRASES):
        return "emergency"

    if any(_has_non_negated_phrase(tokens, phrase) for phrase in _URGENT_PHRASES):
        return "urgent"

    return "non_emergency"


class AITriageService:
    """AI-powered triage service.

    AI is OPTIONAL — service falls back to rule-based when AI server is not
    configured or returns errors. Emergency cases bypass AI entirely.
    """

    def __init__(self) -> None:
        # Pull config at instance time so tests can override `settings`.
        self.provider = settings.ai_provider
        self.base_url = settings.ai_base_url.rstrip("/")
        self.api_key = settings.ai_api_key
        self.model = settings.ai_medical_model
        self.timeout_seconds = settings.ai_request_timeout_seconds

    @property
    def _ai_enabled(self) -> bool:
        return self.provider in {"openai_compatible", "medgemma_server"}

    async def triage_with_ai(self, payload: TriageRequest) -> TriageResponse:
        """Perform triage with multi-tier fallback.

        Tier 1 (Rule-based) catches obvious emergencies immediately. Tier 2
        (AI server) provides nuanced analysis for non-emergency cases. Tier 3
        is a deterministic rule-based response when AI is unavailable.
        """
        rule_urgency = _classify_urgency_rule_based(payload.symptom_text)
        if rule_urgency == "emergency":
            return self._build_emergency_response(payload)

        if self._ai_enabled:
            try:
                return await self._call_ai_triage(payload)
            except Exception as exc:  # noqa: BLE001
                logger.warning("AI triage failed, falling back to rule-based: %s", exc)

        return self._build_rule_based_response(payload, rule_urgency)

    async def _call_ai_triage(self, payload: TriageRequest) -> TriageResponse:
        """Call MedGemma medical adapter via AI server (OpenAI-compatible).

        Only invoked when:
        - ai_provider is openai_compatible/medgemma_server
        - Case is NOT an obvious emergency (Tier 1 already handled).
        """
        prompt = self._build_triage_prompt(payload)
        body: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT_VI},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 1024,
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=body,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        content: str = data["choices"][0]["message"]["content"]
        return self._parse_ai_response(content)

    def _build_triage_prompt(self, payload: TriageRequest) -> str:
        age = getattr(payload, "age", None)
        gender = getattr(payload, "gender", None)
        duration = getattr(payload, "duration", None)

        age_info = f", tuổi: {age}" if age else ""
        gender_info = f", giới tính: {gender}" if gender else ""

        return (
            "Phân tích các triệu chứng sau và trả về JSON thuần (không markdown):\n"
            f"Triệu chứng: {payload.symptom_text}\n"
            f"Thời gian: {duration or 'không rõ'}{age_info}{gender_info}\n\n"
            "JSON gồm các trường:\n"
            '- "urgency_level": "emergency" | "urgent" | "non_emergency"\n'
            '- "summary": tóm tắt 2-3 câu về tình trạng\n'
            '- "recommendations": mảng 2-4 khuyến cáo cụ thể (tiếng Việt)\n'
        )

    def _parse_ai_response(self, content: str) -> TriageResponse:
        """Parse JSON output from AI server. Falls back to text heuristics."""
        text = content.strip()
        # Strip markdown fence if model wraps JSON in ```json ... ```
        if text.startswith("```"):
            stripped = text.strip("`")
            if stripped.lower().startswith("json"):
                stripped = stripped[4:]
            text = stripped.strip()

        try:
            result = json.loads(text)
            return TriageResponse(
                urgency_level=result.get("urgency_level", "non_emergency"),
                summary=result.get("summary", ""),
                recommendations=result.get("recommendations") or [],
            )
        except (json.JSONDecodeError, TypeError, ValueError):
            logger.info("AI response was not valid JSON, parsing text heuristically.")
            return self._parse_text_response(content)

    def _parse_text_response(self, text: str) -> TriageResponse:
        """Fallback parser when AI returns free-form Vietnamese text."""
        text_lower = text.lower()
        if any(word in text_lower for word in ("khẩn cấp", "cấp cứu", "nguy hiểm", "115")):
            urgency = "emergency"
        elif any(word in text_lower for word in ("nên đi khám", "trong 24", "trong 48")):
            urgency = "urgent"
        else:
            urgency = "non_emergency"

        return TriageResponse(
            urgency_level=urgency,
            summary=text[:200] if len(text) > 200 else text,
            recommendations=[
                "Tham khảo ý kiến bác sĩ.",
                "Theo dõi triệu chứng.",
                "Liên hệ cơ sở y tế nếu tình trạng nặng lên.",
            ],
        )

    def _build_emergency_response(self, payload: TriageRequest) -> TriageResponse:
        """Tier 1 response — bypasses AI for fastest possible reply."""
        return TriageResponse(
            urgency_level="emergency",
            summary="Triệu chứng cần cấp cứu ngay. Liên hệ 115 hoặc đến bệnh viện gần nhất.",
            recommendations=[
                "Gọi cấp cứu 115 hoặc đến bệnh viện ngay lập tức.",
                "Nếu có đau ngực hoặc khó thở, gọi 115 ngay.",
                "Không tự ý uống thuốc chưa rõ.",
                "Nếu có người thân, thông báo ngay.",
            ],
        )

    def _build_rule_based_response(
        self, payload: TriageRequest, urgency: str
    ) -> TriageResponse:
        """Tier 3 fallback — deterministic response when AI unavailable."""
        if urgency == "urgent":
            recommendations = [
                "Đến phòng khám hoặc bệnh viện trong 24-48 giờ.",
                "Theo dõi triệu chứng, nếu nặng lên gọi 115.",
                "Uống đủ nước, nghỉ ngơi.",
            ]
        else:
            recommendations = [
                "Theo dõi triệu chứng trong 24-48 giờ.",
                "Uống đủ nước và nghỉ ngơi.",
                "Liên hệ cơ sở y tế nếu triệu chứng tăng lên.",
            ]

        return TriageResponse(
            urgency_level=urgency,
            summary="Thông tin mang tính tham khảo, không thay thế chẩn đoán bác sĩ.",
            recommendations=recommendations,
        )


_SYSTEM_PROMPT_VI = (
    "Bạn là MediSign AI, trợ lý y tế tiếng Việt. "
    "Phân loại mức độ khẩn cấp và đưa khuyến cáo dựa trên triệu chứng. "
    "Luôn trả lời bằng tiếng Việt, không dịch sang ngôn ngữ khác. "
    "Chỉ đưa gợi ý sơ bộ, không chẩn đoán chắc chắn, "
    "luôn khuyên gặp bác sĩ khi có dấu hiệu nặng."
)


# Default instance
ai_triage_service = AITriageService()


# Backward-compatible legacy function — uses rule-based only.
def build_triage_result(payload: TriageRequest) -> TriageResponse:
    """Legacy function — uses rule-based triage (no AI call)."""
    urgency_level = _classify_urgency_rule_based(payload.symptom_text)

    recommendations = [
        "Theo dõi triệu chứng trong 24 giờ.",
        "Uống đủ nước và nghỉ ngơi.",
        "Liên hệ cơ sở y tế nếu triệu chứng tăng lên.",
    ]

    if urgency_level == "emergency":
        recommendations = [
            "Gọi cấp cứu 115 hoặc đến bệnh viện gần nhất ngay.",
            "Không tự ý dùng thuốc chưa rõ nguồn gốc.",
        ]

    return TriageResponse(
        urgency_level=urgency_level,
        summary="Thông tin mang tính tham khảo, không thay thế chẩn đoán bác sĩ.",
        recommendations=recommendations,
    )
