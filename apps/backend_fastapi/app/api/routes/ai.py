"""Chat endpoint for the AI assistant.

Two request shapes are accepted on ``POST /api/v1/ai/chat``:

* ``application/json`` — original single-shot payload (``AIChatRequest``).
* ``multipart/form-data`` — form fields plus an optional ``image`` upload
  for multimodal diagnostic input.

Dispatch rules:

* When ``conversation_id`` is present in the parsed payload, the handler
  delegates to :func:`app.services.diagnostic_orchestrator.diagnose_turn`
  (multi-turn diagnostic flow) using the authenticated user's id. Auth is
  required on this path.
* When ``conversation_id`` is absent, the handler preserves the existing
  single-shot ``ai_model_service.chat`` behaviour exactly. Auth is optional
  to keep backwards compatibility with existing API consumers.

Requirements: 8.1, 8.2, 8.6, 17.1
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from pydantic import ValidationError

from app.core.dependencies import get_optional_current_user
from app.database.cloud_models import User
from app.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    AIStatusResponse,
    RAGSearchRequest,
    RAGSearchResponse,
)
from app.services.ai_model_service import ai_model_service
from app.services.diagnostic_orchestrator import diagnose_turn
from app.services.rag_service import rag_service
from app.core.rate_limit import rate_limit_ai_chat

router = APIRouter(prefix="/ai", tags=["ai"])

# Limit raw image upload size (mirrors ImagePreprocessor's 10 MB ceiling per
# Req 7.4) so we reject oversize bodies before buffering them in memory.
_MAX_IMAGE_BYTES = 10 * 1024 * 1024
_VALID_IMAGE_TYPES: tuple[str, ...] = ("xray", "dermatology")


@router.get("/status", response_model=AIStatusResponse)
def ai_status() -> AIStatusResponse:
    return ai_model_service.status()


@router.post("/chat", response_model=AIChatResponse)
@rate_limit_ai_chat()
async def ai_chat(
    request: Request,
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
) -> AIChatResponse:
    """Chat entry point.

    Supports both JSON and multipart/form-data bodies. See module docstring.
    """
    content_type = (request.headers.get("content-type") or "").lower()

    if content_type.startswith("multipart/form-data") or content_type.startswith(
        "application/x-www-form-urlencoded"
    ):
        payload = await _parse_form_request(request)
    else:
        payload = await _parse_json_request(request)

    # ─── Dispatch ────────────────────────────────────────────────────────
    if payload.conversation_id is not None:
        # Multi-turn diagnostic flow requires an authenticated user so that
        # ChatMemoryService can scope conversations and PersonalContextService
        # can run user-scoped queries (Req 17.1, 17.4).
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "AUTH_REQUIRED",
                    "message": "Yeu cau xac thuc khi su dung conversation_id",
                },
            )
        return await diagnose_turn(
            payload=payload,
            conversation_id=payload.conversation_id,
            user_id=current_user.id,
        )

    # ─── Backwards-compatible single-shot path ──────────────────────────
    return await ai_model_service.chat(payload)


@router.get("/rag/status")
def rag_status() -> dict:
    return rag_service.status()


@router.post("/rag/rebuild")
def rag_rebuild() -> dict:
    return rag_service.rebuild()


@router.post("/rag/search", response_model=RAGSearchResponse)
def rag_search(payload: RAGSearchRequest) -> RAGSearchResponse:
    hits = rag_service.search(payload.query, top_k=payload.top_k, adapter=payload.adapter)
    return RAGSearchResponse(
        query=payload.query,
        hits=ai_model_service._rag_sources(hits),
        context=rag_service.build_context(hits),
    )


# ─── Request parsers ────────────────────────────────────────────────────────


async def _parse_json_request(request: Request) -> AIChatRequest:
    """Parse a JSON body into an :class:`AIChatRequest`.

    Mirrors FastAPI's default behaviour for the original endpoint but lets us
    keep a single route that also accepts multipart bodies.
    """
    try:
        body = await request.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "Body khong phai JSON hop le",
            },
        ) from exc

    try:
        return AIChatRequest.model_validate(body)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "Payload khong hop le",
                "details": {"errors": exc.errors()},
            },
        ) from exc


async def _parse_form_request(request: Request) -> AIChatRequest:
    """Parse a form-encoded body (multipart or url-encoded) into an
    :class:`AIChatRequest`.

    Recognised form fields (all are strings except ``image``):

    * ``message`` (required)
    * ``system_prompt``
    * ``adapter`` (default ``medical``)
    * ``use_rag`` (``"true"``/``"false"``, default ``true``)
    * ``rag_top_k`` (int, default 5)
    * ``conversation_id``
    * ``use_personal_context`` (``"true"``/``"false"``, default ``false``)
    * ``image_type`` (``xray`` | ``dermatology``)
    * ``image`` (file upload, optional)
    """
    form = await request.form()

    raw: dict[str, object] = {}

    message = _form_str(form.get("message"))
    if message is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "Field 'message' la bat buoc",
            },
        )
    raw["message"] = message

    system_prompt = _form_str(form.get("system_prompt"))
    if system_prompt is not None:
        raw["system_prompt"] = system_prompt

    adapter = _form_str(form.get("adapter"))
    if adapter is not None:
        raw["adapter"] = adapter

    use_rag = _form_bool(form.get("use_rag"))
    if use_rag is not None:
        raw["use_rag"] = use_rag

    rag_top_k = _form_int(form.get("rag_top_k"), field="rag_top_k")
    if rag_top_k is not None:
        raw["rag_top_k"] = rag_top_k

    conversation_id = _form_str(form.get("conversation_id"))
    if conversation_id is not None:
        raw["conversation_id"] = conversation_id

    use_personal_context = _form_bool(form.get("use_personal_context"))
    if use_personal_context is not None:
        raw["use_personal_context"] = use_personal_context

    image_type = _form_str(form.get("image_type"))
    if image_type is not None:
        if image_type not in _VALID_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": (
                        "image_type phai la 'xray' hoac 'dermatology'"
                    ),
                },
            )
        raw["image_type"] = image_type  # narrows to Literal at validation time

    image_field = form.get("image")
    if image_field is not None and isinstance(image_field, UploadFile):
        raw["image"] = await _read_upload_bytes(image_field)

    try:
        return AIChatRequest.model_validate(raw)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "Payload khong hop le",
                "details": {"errors": exc.errors()},
            },
        ) from exc


# ─── Form-field helpers ─────────────────────────────────────────────────────


def _form_str(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else None
    return None


def _form_bool(value: object) -> bool | None:
    if value is None or not isinstance(value, str):
        return None
    cleaned = value.strip().lower()
    if cleaned in {"true", "1", "yes", "on"}:
        return True
    if cleaned in {"false", "0", "no", "off"}:
        return False
    return None


def _form_int(value: object, *, field: str) -> int | None:
    if value is None or not isinstance(value, str) or not value.strip():
        return None
    try:
        return int(value.strip())
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "VALIDATION_ERROR",
                "message": f"Field '{field}' phai la so nguyen",
            },
        ) from exc


async def _read_upload_bytes(upload: UploadFile) -> bytes:
    """Read an uploaded file enforcing the 10 MB ceiling (Req 7.4).

    The full ``ImagePreprocessor`` pipeline performs deeper validation
    (MIME type, decode, normalisation); this is just a cheap upfront guard
    so we don't buffer arbitrarily large bodies.
    """
    data = await upload.read()
    if len(data) > _MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "code": "IMAGE_TOO_LARGE",
                "message": "Anh vuot qua gioi han 10 MB",
            },
        )
    return data
