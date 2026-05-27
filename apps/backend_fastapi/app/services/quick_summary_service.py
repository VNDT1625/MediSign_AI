"""QuickSummaryService — read-only projection of latest diagnostic state for the widget.

Validates: Requirements 11.1, 11.2, 11.3, 11.4
"""

from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.cloud_models import ChatConversation, ChatMessage
from app.schemas.diagnostic import DiagnosticState, QuickSummary, TriageLevel


class ConversationNotFoundError(ValueError):
    """Raised when the requested conversation does not exist or is not owned by the user."""


class QuickSummaryService:
    """Derives a QuickSummary purely from persisted DiagnosticState — no LLM or RAG calls."""

    # Recommendation strings keyed by triage level
    _RECOMMENDATIONS: dict[str | None, str] = {
        "green": "Bạn có thể tự chăm sóc tại nhà. Nghỉ ngơi, uống đủ nước và theo dõi triệu chứng.",
        "yellow": "Theo dõi triệu chứng và đặt lịch khám bác sĩ nếu không cải thiện trong 1-2 ngày.",
        "red": "Hãy đến cơ sở y tế ngay lập tức hoặc gọi cấp cứu 115.",
        None: "Chưa đủ thông tin để đưa ra khuyến nghị. Vui lòng tiếp tục mô tả triệu chứng.",
    }

    def latest(
        self,
        db: Session,
        user_id: str,
        conversation_id: str | None = None,
    ) -> QuickSummary:
        """Return a QuickSummary derived from the latest persisted DiagnosticState.

        If *conversation_id* is provided, load that specific conversation (verify
        ownership). Otherwise, find the user's most recent non-archived conversation.

        Raises:
            ConversationNotFoundError: when no matching conversation is found or
                the conversation does not belong to the user.
        """
        conversation = self._resolve_conversation(db, user_id, conversation_id)
        state = self._load_latest_state(db, conversation.id)

        recommendation = self._recommendation_for(state.triage_level)

        return QuickSummary(
            conversation_id=conversation.id,
            symptoms_collected=state.symptoms_collected,
            diseases_ranked=state.diseases_ranked,
            triage_level=state.triage_level,
            recommendation=recommendation,
            updated_at=state.last_updated,
        )

    # ─── Private helpers ─────────────────────────────────────────────────────

    def _resolve_conversation(
        self,
        db: Session,
        user_id: str,
        conversation_id: str | None,
    ) -> ChatConversation:
        """Find the target conversation, verifying ownership."""
        if conversation_id is not None:
            conversation = (
                db.query(ChatConversation)
                .filter(ChatConversation.id == conversation_id)
                .first()
            )
            if conversation is None or conversation.user_id != user_id:
                raise ConversationNotFoundError(
                    "Conversation not found or does not belong to the user."
                )
            return conversation

        # No conversation_id — find the most recent non-archived conversation
        conversation = (
            db.query(ChatConversation)
            .filter(
                ChatConversation.user_id == user_id,
                ChatConversation.is_archived == False,  # noqa: E712
            )
            .order_by(ChatConversation.updated_at.desc())
            .first()
        )
        if conversation is None:
            raise ConversationNotFoundError(
                "No active conversation found for this user."
            )
        return conversation

    def _load_latest_state(
        self, db: Session, conversation_id: str
    ) -> DiagnosticState:
        """Read the latest assistant message's diagnosis_state from metadata."""
        message = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.conversation_id == conversation_id,
                ChatMessage.role == "assistant",
            )
            .order_by(ChatMessage.created_at.desc())
            .first()
        )

        if message is None:
            return DiagnosticState()

        metadata = message.metadata_json or {}
        raw_state = metadata.get("diagnosis_state")
        if raw_state is None:
            return DiagnosticState()

        try:
            return DiagnosticState.model_validate(raw_state)
        except (Exception,):
            # On validation error, return default state (same pattern as ChatMemoryService)
            return DiagnosticState()

    def _recommendation_for(self, triage_level: TriageLevel | None) -> str:
        """Generate recommendation string from triage level."""
        return self._RECOMMENDATIONS.get(triage_level, self._RECOMMENDATIONS[None])
