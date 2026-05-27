"""Conversation management endpoints for diagnostic chat.

Implements:
- GET /api/v1/ai/conversations — paginated list of user's conversations
- GET /api/v1/ai/conversations/{id} — full conversation with messages and state
- DELETE /api/v1/ai/conversations/{id} — soft-delete (archive) a conversation

Requirements: 10.1, 10.2, 10.3, 10.4, 17.1, 17.2
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.database.cloud_models import ChatConversation, ChatMessage, User
from app.schemas.diagnostic import DiagnosticState
from app.services.feedback_service import feedback_service

router = APIRouter(prefix="/ai/conversations", tags=["conversations"])


# ─── Response schemas ────────────────────────────────────────────────────────


class ConversationListItem(BaseModel):
    """Summary item for the conversations list endpoint."""

    id: str
    title: str | None = None
    adapter: str
    phase: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageItem(BaseModel):
    """A single message in a conversation detail response."""

    id: str
    role: str
    content: str
    metadata_json: dict = Field(default_factory=dict)
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetail(BaseModel):
    """Full conversation detail with messages and final state."""

    id: str
    title: str | None = None
    adapter: str
    phase: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    messages: list[MessageItem] = Field(default_factory=list)
    diagnosis_state: DiagnosticState | None = None

    model_config = {"from_attributes": True}


class PaginatedConversations(BaseModel):
    """Paginated response for conversations list."""

    items: list[ConversationListItem]
    total: int
    page: int
    page_size: int
    has_next: bool


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _validate_conversation_id(conversation_id: str) -> None:
    """Validate that conversation_id is a valid 36-char UUID string."""
    if len(conversation_id) != 36:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "conversation_id must be a 36-character UUID",
            },
        )
    try:
        UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "conversation_id must be a valid UUID",
            },
        )


def _get_conversation_or_404(
    db: Session, conversation_id: str, user_id: str
) -> ChatConversation:
    """Fetch a conversation, ensuring it belongs to the authenticated user."""
    conversation = (
        db.query(ChatConversation)
        .filter(ChatConversation.id == conversation_id)
        .first()
    )
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CONVERSATION_NOT_FOUND",
                "message": "Cuoc hoi thoai khong ton tai",
            },
        )
    return conversation


# ─── Endpoints ───────────────────────────────────────────────────────────────


@router.get("", response_model=PaginatedConversations)
def list_conversations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> PaginatedConversations:
    """Return paginated list of the authenticated user's conversations.

    Ordered by updated_at descending (most recent first).
    Excludes archived conversations by default.
    """
    base_query = db.query(ChatConversation).filter(
        ChatConversation.user_id == current_user.id,
        ChatConversation.is_archived == False,  # noqa: E712
    )

    total = base_query.count()
    offset = (page - 1) * page_size

    conversations = (
        base_query.order_by(ChatConversation.updated_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    items = [
        ConversationListItem(
            id=conv.id,
            title=conv.title,
            adapter=conv.adapter,
            phase=conv.phase,
            is_archived=conv.is_archived,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        )
        for conv in conversations
    ]

    return PaginatedConversations(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_next=(offset + page_size) < total,
    )


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> ConversationDetail:
    """Return full message history and final DiagnosticState for a conversation.

    Returns 404 if conversation not found or belongs to another user.
    """
    _validate_conversation_id(conversation_id)
    conversation = _get_conversation_or_404(db, conversation_id, current_user.id)

    # Load all messages ordered chronologically
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    # Extract final DiagnosticState from the last assistant message
    diagnosis_state: DiagnosticState | None = None
    for msg in reversed(messages):
        if msg.role == "assistant" and msg.metadata_json:
            raw_state = msg.metadata_json.get("diagnosis_state")
            if raw_state:
                try:
                    diagnosis_state = DiagnosticState.model_validate(raw_state)
                except Exception:
                    pass
            break

    message_items = [
        MessageItem(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            metadata_json=msg.metadata_json or {},
            created_at=msg.created_at,
        )
        for msg in messages
    ]

    return ConversationDetail(
        id=conversation.id,
        title=conversation.title,
        adapter=conversation.adapter,
        phase=conversation.phase,
        is_archived=conversation.is_archived,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=message_items,
        diagnosis_state=diagnosis_state,
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_200_OK)
def delete_conversation(
    conversation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> dict:
    """Soft-delete a conversation by setting is_archived=True.

    Returns 404 if conversation not found or belongs to another user.
    """
    _validate_conversation_id(conversation_id)
    conversation = _get_conversation_or_404(db, conversation_id, current_user.id)

    conversation.is_archived = True
    conversation.updated_at = datetime.utcnow()
    db.commit()

    return {
        "code": "CONVERSATION_ARCHIVED",
        "message": "Cuoc hoi thoai da duoc luu tru",
        "conversation_id": conversation_id,
    }


# ─── Feedback endpoint ───────────────────────────────────────────────────────


class FeedbackRequest(BaseModel):
    """Payload for submitting diagnosis feedback."""

    is_correct: bool = Field(..., description="True nếu AI đoán đúng bệnh")
    ai_predicted_disease: str = Field(..., description="Bệnh AI dự đoán tại kết luận")
    ai_confidence: float | None = Field(None, ge=0.0, le=1.0)
    actual_disease: str | None = Field(None, description="Bệnh thực tế từ bác sĩ (khi sai)")
    symptoms_at_time: list[str] = Field(default_factory=list)
    notes: str | None = None


class FeedbackResponse(BaseModel):
    feedback_id: int
    conversation_id: str
    is_correct: bool
    message: str


@router.post("/{conversation_id}/feedback", response_model=FeedbackResponse)
def submit_feedback(
    conversation_id: str,
    payload: FeedbackRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> FeedbackResponse:
    """Submit diagnosis feedback after a real doctor visit.

    User xác nhận AI đúng hay sai. Nếu sai thì cung cấp bệnh thực tế.
    Khi đủ ngưỡng (10 feedbacks), hệ thống tự động tạo WeightUpdateProposal
    cho admin review.
    """
    _validate_conversation_id(conversation_id)
    _get_conversation_or_404(db, conversation_id, current_user.id)

    feedback = feedback_service.submit_feedback(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
        is_correct=payload.is_correct,
        ai_predicted_disease=payload.ai_predicted_disease,
        ai_confidence=payload.ai_confidence,
        actual_disease=payload.actual_disease,
        symptoms_at_time=payload.symptoms_at_time,
        notes=payload.notes,
    )

    msg = "Cảm ơn bạn đã xác nhận. Phản hồi đã được ghi nhận." if payload.is_correct else \
        "Cảm ơn bạn đã phản hồi. Thông tin sẽ giúp cải thiện hệ thống."

    return FeedbackResponse(
        feedback_id=feedback.id,
        conversation_id=conversation_id,
        is_correct=payload.is_correct,
        message=msg,
    )
