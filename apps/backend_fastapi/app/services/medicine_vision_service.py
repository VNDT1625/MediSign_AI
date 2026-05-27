"""medicine_vision_service.py — Image-based drug recognition using MedGemma 4B.

Luồng:
  1. Nhận ảnh bytes → encode base64
  2. Gọi MedGemma 4B (vision) để đọc tên thuốc từ ảnh
  3. Tra cứu tên thuốc trong drug database (drug_lookup_service)
  4. Chạy interaction check qua medicine_service.scan_medicine
  5. Trả về kết quả tổng hợp

MedGemma 4B nhận ảnh qua OpenAI-compatible multimodal format:
  messages[0].content = [
    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}},
    {"type": "text", "text": "<prompt>"},
  ]
"""

from __future__ import annotations

import base64
import json
import logging
import re
from typing import Any

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.medicine import (
    MedicineScanResponse,
    MedicineImageScanResponse,
)
from app.services.drug_lookup_service import get_drug_info
from app.services.medicine_service import scan_medicine
from app.schemas.medicine import MedicineScanRequest

logger = logging.getLogger(__name__)

# 10 MB hard limit
_MAX_BYTES = 10 * 1024 * 1024
_ALLOWED_MIMES = {"image/jpeg", "image/png", "image/webp"}

_VISION_PROMPT = (
    "Đây là ảnh nhãn hoặc vỏ hộp thuốc. "
    "Hãy đọc kỹ ảnh và trả về JSON hợp lệ DUY NHẤT, không giải thích:\n"
    '{"drug_name": "Tên thuốc đầy đủ", '
    '"dosage": "Hàm lượng/liều nếu đọc được hoặc null", '
    '"manufacturer": "Nhà sản xuất nếu đọc được hoặc null", '
    '"raw_text": "Toàn bộ chữ đọc được trên nhãn (ngắn gọn)"}\n\n'
    "Nếu không đọc được tên thuốc, đặt drug_name là null."
)


def _detect_mime(file_bytes: bytes, content_type: str | None) -> str:
    """Detect MIME type from content_type header or magic bytes."""
    if content_type and content_type.split(";")[0].strip() in _ALLOWED_MIMES:
        return content_type.split(";")[0].strip()
    # Fallback via magic bytes
    if file_bytes[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if file_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if file_bytes[:4] in (b"RIFF", b"WEBP"):
        return "image/webp"
    return content_type or "image/jpeg"


def _to_data_url(image_bytes: bytes, mime_type: str) -> str:
    """Encode image as data URL for MedGemma vision input."""
    b64 = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime_type};base64,{b64}"


def _parse_vision_json(content: str) -> dict[str, Any]:
    """Extract JSON dict from LLM output (may be wrapped in markdown)."""
    text = content.strip()
    # Strip markdown code fences
    if "```" in text:
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if m:
            text = m.group(1)
    # Find raw JSON object
    if not text.startswith("{"):
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            text = m.group(0)
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        logger.warning("medicine_vision: failed to parse JSON from LLM output: %r", content[:300])
        return {}


async def _call_medgemma_vision(data_url: str) -> dict[str, Any]:
    """Call MedGemma 4B with vision input. Returns parsed dict from model."""
    if settings.ai_provider not in {"openai_compatible", "medgemma_server"}:
        # Fallback: return empty so caller uses rule-based path
        return {}

    body: dict[str, Any] = {
        "model": settings.ai_medical_model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url},
                    },
                    {
                        "type": "text",
                        "text": _VISION_PROMPT,
                    },
                ],
            }
        ],
        "temperature": 0,
        "max_tokens": 300,
    }
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if settings.ai_api_key:
        headers["Authorization"] = f"Bearer {settings.ai_api_key}"

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                f"{settings.ai_base_url.rstrip('/')}/chat/completions",
                json=body,
                headers=headers,
            )
            resp.raise_for_status()
            llm_content = resp.json()["choices"][0]["message"]["content"]
        return _parse_vision_json(llm_content)
    except Exception as exc:
        logger.warning("medicine_vision: MedGemma call failed: %s", exc)
        return {}


async def scan_medicine_from_image(
    image_bytes: bytes,
    content_type: str | None,
    current_medications: list[str],
) -> MedicineImageScanResponse:
    """Full pipeline: image bytes → drug name → lookup → interaction check.

    Args:
        image_bytes: Raw file bytes from upload.
        content_type: MIME type from Content-Type header.
        current_medications: User's current active medicines for interaction check.

    Returns:
        MedicineImageScanResponse with extracted name, drug info, and warnings.

    Raises:
        HTTPException(413): File > 10 MB.
        HTTPException(415): Unsupported image type.
        HTTPException(422): Cannot process image.
    """
    # ── 1. Validate ──────────────────────────────────────────────────────────
    if len(image_bytes) > _MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail={"code": "FILE_TOO_LARGE", "message": "Ảnh vượt quá giới hạn 10 MB."},
        )

    mime = _detect_mime(image_bytes, content_type)
    if mime not in _ALLOWED_MIMES:
        raise HTTPException(
            status_code=415,
            detail={
                "code": "UNSUPPORTED_MEDIA_TYPE",
                "message": f"Định dạng ảnh không hỗ trợ: {mime}. Dùng JPEG hoặc PNG.",
            },
        )

    # ── 2. Encode + call MedGemma 4B vision ──────────────────────────────────
    data_url = _to_data_url(image_bytes, mime)
    vision_result = await _call_medgemma_vision(data_url)

    extracted_drug_name: str | None = vision_result.get("drug_name") or None
    extracted_dosage: str | None = vision_result.get("dosage") or None
    extracted_manufacturer: str | None = vision_result.get("manufacturer") or None
    raw_text: str | None = vision_result.get("raw_text") or None

    # ── 3. Drug database lookup ───────────────────────────────────────────────
    drug_info: dict | None = None
    drug_lookup_status = "not_found"
    suggestions: list[dict] = []

    if extracted_drug_name:
        lookup = get_drug_info(extracted_drug_name)
        drug_lookup_status = lookup["status"]
        if lookup["status"] == "found":
            drug_info = lookup.get("drug")
        elif lookup["status"] == "suggestions":
            suggestions = lookup.get("suggestions", [])

    # ── 4. Interaction/warning check (reuse existing rule-based engine) ───────
    scan_result: MedicineScanResponse | None = None
    if extracted_drug_name:
        scan_text = f"{extracted_drug_name}"
        if extracted_dosage:
            scan_text = f"{extracted_drug_name} {extracted_dosage}"
        scan_result = scan_medicine(
            MedicineScanRequest(
                extracted_text=scan_text,
                current_medications=current_medications,
            )
        )

    # ── 5. Build response ─────────────────────────────────────────────────────
    return MedicineImageScanResponse(
        # What MedGemma read from the image
        extracted_drug_name=extracted_drug_name,
        extracted_dosage=extracted_dosage,
        extracted_manufacturer=extracted_manufacturer,
        raw_ocr_text=raw_text,
        # Drug database result
        drug_lookup_status=drug_lookup_status,
        drug_info=drug_info,
        suggestions=suggestions,
        # Interaction warnings (from existing scan engine)
        normalized_name=scan_result.normalized_name if scan_result else (extracted_drug_name or ""),
        risk_level=scan_result.risk_level if scan_result else "unknown",
        warnings=scan_result.warnings if scan_result else [],
        guidance=scan_result.guidance if scan_result else "Xác minh với dược sĩ hoặc bác sĩ.",
        # Meta
        model_used=settings.ai_medical_model,
        fallback_used=(not bool(vision_result)),
    )
