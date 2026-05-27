"""Quick Summary endpoint for the diagnostic chat widget.

Implements:
- GET /api/v1/ai/summary — read-only projection of latest DiagnosticState

Requirements: 11.1, 11.2, 11.3, 11.4, 17.1
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.database.cloud_models import User
from app.schemas.diagnostic import QuickSummary
from app.services.quick_summary_service import (
    ConversationNotFoundError,
    QuickSummaryService,
)

router = APIRouter(prefix="/ai", tags=["summary"])

_summary_service = QuickSummaryService()


def _validate_conversation_id(conversation_id: str) -> None:
    """Validate that conversation_id is a valid 36-char UUID string."""
    if len(conversation_id) != 36:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "conversation_id must be a 36-character UUID",
            },
        )
    try:
        UUID(conversation_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "conversation_id must be a valid UUID",
            },
        ) from error


@router.get("/summary", response_model=QuickSummary)
def get_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    conversation_id: str | None = Query(
        default=None,
        description=(
            "Optional conversation ID. When omitted, the user's most recent "
            "non-archived conversation is used."
        ),
    ),
) -> QuickSummary:
    """Return a QuickSummary derived from the latest persisted DiagnosticState.

    Authentication is enforced by ``get_current_user`` (HTTP 401 if missing).
    The summary is computed purely from persisted state — no LLM or RAG calls.
    """
    if conversation_id is not None:
        _validate_conversation_id(conversation_id)

    try:
        return _summary_service.latest(
            db=db,
            user_id=current_user.id,
            conversation_id=conversation_id,
        )
    except ConversationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CONVERSATION_NOT_FOUND",
                "message": "Khong tim thay cuoc hoi thoai",
            },
        ) from error
