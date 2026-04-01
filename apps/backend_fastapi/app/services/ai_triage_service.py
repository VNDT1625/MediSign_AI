"""AI-powered triage service.

ARCHITECTURE OVERVIEW (CRITICAL - Read First!)
==============================================

MediSign AI có 3 DEPLOYMENT MODES:

┌─────────────────────────────────────────────────────────────────────┐
│                    MEDISIGN AI DEPLOYMENT MODES                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐│
│  │    CLOUD        │    │     LOCAL        │    │    HYBRID       ││
│  │   (Bảo mật)     │    │  (Security)      │    │  (Kết hợp)     ││
│  ├─────────────────┤    ├─────────────────┤    ├─────────────────┤│
│  │ Qwen 2.5 72B   │    │  Gemma 2B       │    │   Cloud +      ││
│  │ + LoRA Y tế VN │    │  + 2 Adapters    │    │   Local        ││
│  │ Self-hosted    │    │  On-device      │    │                 ││
│  └─────────────────┘    └─────────────────┘    └─────────────────┘│
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

───────────────────────────────────────────────────────────────────────
MODE 1: CLOUD (Đám mây - Ẩn danh hoàn toàn)
───────────────────────────────────────────────────────────────────────
  • Model CHÍNH: Qwen 2.5 72B + LoRA Adapter Y tế VN (tự train)
  • Deploy: Self-hosted trên server riêng (A100 GPU)

  ┌─────────────────────────────────────────────────────────────┐
  │ FALLBACK STRATEGY (Tránh quá tải):                         │
  ├─────────────────────────────────────────────────────────────┤
  │ 1. Qwen 72B xử lý bình thường                             │
  │ 2. 80-95% tải → Chuyển sang Qwen 7B (nhanh 10x)          │
  │ 3. 95-100% tải → Gemini Flash API (trả phí nhưng không  │
  │    sập)                                                    │
  │ 4. 100% quá tải → Request Queue + Ưu tiên emergency       │
  └─────────────────────────────────────────────────────────────┘

  • Use case: User muốn AI mạnh nhất, chấp nhận gửi data lên cloud
  • CẦN TRAIN: Qwen 2.5 72B + LoRA Medical Adapter

───────────────────────────────────────────────────────────────────────
MODE 2: LOCAL (Local - Bảo mật tối đa)
───────────────────────────────────────────────────────────────────────
  • Base Model: Gemma 2B (4-bit, ~1.5GB)
  • Adapter #1: MediSign-Med (LoRA y tế, ~50MB) - CẦN TRAIN
  • Adapter #2: MediSign-Personal (LoRA cá nhân, ~50-100MB) - CẦN TRAIN
  • Total RAM: ~1.65GB
  • Use case: User muốn 100% offline, data không rời máy
  • CẦN TRAIN: 2 Adapters (Medical + Personal)

───────────────────────────────────────────────────────────────────────
MODE 3: HYBRID (Kết hợp)
───────────────────────────────────────────────────────────────────────
  • Cloud cho complex queries
  • Local cho quick responses & offline fallback
  • Adapter Personal đồng bộ encrypted lên cloud (backup)

───────────────────────────────────────────────────────────────────────
INTERNAL FALLBACK (trong mỗi mode):
───────────────────────────────────────────────────────────────────────

    REQUEST → RULE-BASED (fast path for emergencies)
                  │
                  ▼ If NOT emergency → AI MODEL
                  │    (Qwen/Gemini/Gemma tùy mode)
                  │
                  ▼ If AI fails → RULE-BASED RESPONSE
                       (always works, no external deps)

───────────────────────────────────────────────────────────────────────
WHAT NEEDS TRAINING:
───────────────────────────────────────────────────────────────────────
1. Qwen 2.5 72B + LoRA Medical Adapter (Cloud mode)
2. Gemma 2B + LoRA Medical Adapter (Local mode)
3. LoRA Personal Adapter (Local/Hybrid mode)

See: packages/ai_training/

ENVIRONMENT VARIABLES:
======================
- DASHSCOPE_API_KEY: API key from Alibaba Cloud DashScope (for Qwen)
- AI_MODEL: Model name (default: "qwen-turbo")
- LOCAL_MODE: Set to "true" for local-only mode (Gemma 2B)

NOTE: AI is OPTIONAL - rule-based always works as fallback.
"""
import os
from typing import Optional

from app.schemas.triage import TriageRequest, TriageResponse
from app.services.text_processing import find_phrase_starts, tokenize

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
    """AI-powered triage service with Qwen integration.

    IMPORTANT: This service is designed with AI as BACKUP, not primary.

    Priority Order:
    1. Rule-based (fast) - Always runs first for emergencies
    2. Qwen via DashScope (optional) - Only for nuanced non-emergency cases
    3. Rule-based fallback (always works)

    Usage:
        service = AITriageService()
        result = await service.triage_with_ai(payload)

    Note: Set DASHSCOPE_API_KEY env var to enable Qwen.
    Without API key, only rule-based triage is used.
    """

    def __init__(self):
        # AI Provider Configuration (Qwen PRIMARY)
        # ======================================
        # AI is OPTIONAL - service works without it via rule-based fallback
        #
        # Environment Variables:
        # - DASHSCOPE_API_KEY: API key from Alibaba Cloud DashScope (REQUIRED for Qwen)
        # - AI_MODEL: Model name (default: "qwen-turbo")
        #
        # If DASHSCOPE_API_KEY is NOT set:
        #   → Only rule-based triage is used (Tier 1 + Tier 3)
        #   → Service still works fully
        #
        # If DASHSCOPE_API_KEY IS set:
        #   → Qwen is used for non-emergency cases (Tier 2)
        #   → Provides better nuance for complex symptoms
        self.api_key = os.getenv("DASHSCOPE_API_KEY", "")
        self.model = os.getenv("AI_MODEL", "qwen-turbo")

    async def triage_with_ai(self, payload: TriageRequest) -> TriageResponse:
        """
        Perform AI-powered triage with multi-tier fallback.

        TIER 1 (Primary): Rule-based classification
            → Returns emergency immediately if detected

        TIER 2 (Optional): AI analysis via Gemini/Qwen
            → Only called if: has API key AND NOT emergency
            → Provides nuanced symptom analysis

        TIER 3 (Fallback): Rule-based response
            → Returns deterministic response if AI unavailable

        Args:
            payload: Triage request with symptom text

        Returns:
            TriageResponse with urgency level and recommendations
        """
        # Fast path: rule-based for obvious emergencies
        rule_urgency = _classify_urgency_rule_based(payload.symptom_text)
        if rule_urgency == "emergency":
            return self._build_emergency_response(payload)

        # Use AI for nuanced analysis (Qwen via DashScope)
        if self.api_key:
            try:
                return await self._call_ai_triage(payload)
            except Exception as e:
                # Fallback to rule-based on AI error
                pass

        # Default: rule-based response
        return self._build_rule_based_response(payload, rule_urgency)

    async def _call_ai_triage(self, payload: TriageRequest) -> TriageResponse:
        """Call Qwen API for triage via DashScope.

        NOTE: This method is only called when:
        - DASHSCOPE_API_KEY is configured
        - Case is NOT an obvious emergency (already handled by Tier 1)

        This design prevents:
        - AI API quota exhaustion from emergency calls
        - Latency in critical situations
        - Unnecessary costs for obvious cases
        """
        prompt = self._build_triage_prompt(payload)
        return await self._call_qwen(prompt, payload)

    def _build_triage_prompt(self, payload: TriageRequest) -> str:
        """Build the triage prompt for AI."""
        age = getattr(payload, "age", None)
        gender = getattr(payload, "gender", None)
        duration = getattr(payload, "duration", None)

        age_info = f", tuoi: {age}" if age else ""
        gender_info = f", gioi tinh: {gender}" if gender else ""

        return f"""Ban la bac si chuyen nghiep. Phan tich cac trieu chung sau va dua ra khuyen cao y te.

Trieu chung: {payload.symptom_text}
Thoi gian: {duration or "khong ro"}{age_info}{gender_info}

Chi tra ve JSON voi cac truong:
- urgency_level: "emergency" | "urgent" | "non_emergency"
- summary: tom tat 2-3 cau ve tinh trang
- recommendations: danh sach 2-4 khuyen cao cu the

Phan tich:"""

    async def _call_gemini(self, prompt: str, payload: TriageRequest) -> TriageResponse:
        """Call Gemini API for triage analysis."""
        import google.generativeai as genai
        import json

        genai.configure(api_key=self.api_key)

        model = genai.GenerativeModel(self.model)

        # Generate content with JSON response format
        generation_config = {
            "temperature": 0.2,
            "max_output_tokens": 1024,
            "response_mime_type": "application/json",
        }

        response = model.generate_content(
            prompt,
            generation_config=generation_config,
        )

        # Parse the JSON response
        try:
            result = json.loads(response.text)
            return TriageResponse(
                urgency_level=result.get("urgency_level", "non_emergency"),
                summary=result.get("summary", ""),
                recommendations=result.get("recommendations", []),
            )
        except json.JSONDecodeError:
            # If response is not valid JSON, use rule-based
            raise Exception("Invalid JSON response from Gemini")

    async def _call_qwen(self, prompt: str, payload: TriageRequest) -> TriageResponse:
        """Call Qwen API via DashScope.

        Uses Alibaba Cloud DashScope API for Qwen models.
        See: https://dashscope.console.aliyun.com/
        """
        import dashscope
        import json

        dashscope.api_key = self.api_key

        response = dashscope.Generation.call(
            model=self.model,
            prompt=prompt,
            result_format='message',
            temperature=0.2,
            max_tokens=1024,
        )

        # Parse the response
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            # Try to extract JSON from response
            try:
                # Qwen might return raw text, try to parse JSON
                result = json.loads(content)
                return TriageResponse(
                    urgency_level=result.get("urgency_level", "non_emergency"),
                    summary=result.get("summary", ""),
                    recommendations=result.get("recommendations", []),
                )
            except json.JSONDecodeError:
                # If not JSON, extract structured info from text
                return self._parse_qwen_text_response(content)
        else:
            raise Exception(f"Qwen API error: {response.code} - {response.message}")

    def _parse_qwen_text_response(self, text: str) -> TriageResponse:
        """Parse Qwen text response into structured TriageResponse."""
        # Simple parsing - in production, use better prompt engineering
        text_lower = text.lower()

        # Determine urgency
        if any(word in text_lower for word in ['khẩn', 'cấp', 'nguy hiểm', '115']):
            urgency = "emergency"
        elif any(word in text_lower for word in ['nên đi khám', 'trong 24', 'trong 48']):
            urgency = "urgent"
        else:
            urgency = "non_emergency"

        return TriageResponse(
            urgency_level=urgency,
            summary=text[:200] if len(text) > 200 else text,
            recommendations=[
                "Tham khảo ý kiến bác sĩ",
                "Theo dõi triệu chứng",
                "Liên hệ cơ sở y tế nếu tình trạng nặng lên",
            ],
        )

    def _build_emergency_response(self, payload: TriageRequest) -> TriageResponse:
        """Build emergency response.

        TIER 1 RESPONSE: This is returned IMMEDIATELY when rule-based
        detects emergency keywords (e.g., "khó thở", "đau ngực", "ngất").

        This bypasses AI entirely to ensure:
        - Fastest possible response for critical cases
        - No AI API quota consumed for obvious emergencies
        - Reliable response even when AI service is down
        """
        return TriageResponse(
            urgency_level="emergency",
            summary="Trieu chung can cap cuu ngay. Lien he 115 hoac den benh vien gan nhat.",
            recommendations=[
                "Goi cap cuu 115 hoac den benh vien ngay lap tuc.",
                "Neu co dau nguc hoac kho tho, goi 115 ngay.",
                "Khong tu y uong thuoc chua ro.",
                "Neu co nguoi than, thong bao ngay.",
            ],
        )

    def _build_rule_based_response(
        self, payload: TriageRequest, urgency: str
    ) -> TriageResponse:
        """Build rule-based response."""
        if urgency == "urgent":
            recommendations = [
                "Den phong kham hoac BV trong 24-48 gio.",
                "Theo doi trieu chung, neu nang len goi 115.",
                "Uong du nuoc, nghi ngoi.",
            ]
        else:
            recommendations = [
                "Theo doi trieu chung trong 24-48 gio.",
                "Uong du nuoc va nghi ngoi.",
                "Lien he co so y te neu trieu chung tang len.",
            ]

        return TriageResponse(
            urgency_level=urgency,
            summary="Thong tin mang tinh tham khao, khong thay the chan doan bac si.",
            recommendations=recommendations,
        )


# Default instance
ai_triage_service = AITriageService()


# Keep backwards compatibility
def build_triage_result(payload: TriageRequest) -> TriageResponse:
    """Legacy function - uses rule-based triage."""
    import asyncio

    urgency_level = _classify_urgency_rule_based(payload.symptom_text)

    recommendations = [
        "Theo doi trieu chung trong 24 gio.",
        "Uong du nuoc va nghi ngoi.",
        "Lien he co so y te neu trieu chung tang len.",
    ]

    if urgency_level == "emergency":
        recommendations = [
            "Goi cap cuu 115 hoac den benh vien gan nhat ngay.",
            "Khong tu y dung thuoc chua ro nguon goc.",
        ]

    return TriageResponse(
        urgency_level=urgency_level,
        summary="Thong tin mang tinh tham khao, khong thay the chan doan bac si.",
        recommendations=recommendations,
    )
