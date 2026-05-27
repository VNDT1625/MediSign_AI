from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.cloud_models import ChatConversation, ChatMessage
from app.schemas.diagnostic import DiagnosticState, RankedDisease


STATE_RESET_NOTE = "state_reset_due_to_validation_error"


class ConversationArchivedError(RuntimeError):
    """Raised when a caller tries to continue an archived conversation."""


class ServiceUnavailableError(RuntimeError):
    """Raised when persistent chat memory cannot be accessed."""


class InvalidDiagnosticStateError(ValueError):
    """Raised when a diagnostic state is unsafe to persist."""


def _validate_uuid(value: str) -> None:
    if len(value) != 36:
        raise ValueError("conversation_id must be a 36-character UUID string")
    UUID(value)


class ChatMemoryService:
    """Persistence boundary for diagnostic chat conversations and state."""

    VALID_ADAPTERS = {"medical", "psychology"}

    def __init__(self) -> None:
        self._state_reset_conversations: set[str] = set()

    def get_or_create_conversation(
        self,
        db: Session,
        user_id: str,
        conversation_id: str | None,
        adapter: str = "medical",
    ) -> ChatConversation:
        if adapter not in self.VALID_ADAPTERS:
            raise ValueError("adapter must be 'medical' or 'psychology'")
        if conversation_id is not None:
            _validate_uuid(conversation_id)

        try:
            conversation = None
            if conversation_id:
                conversation = (
                    db.query(ChatConversation)
                    .filter(ChatConversation.id == conversation_id)
                    .first()
                )
                if conversation and conversation.is_archived:
                    raise ConversationArchivedError("conversation is archived")

            if conversation:
                return conversation

            conversation = ChatConversation(
                id=conversation_id or str(uuid4()),
                user_id=user_id,
                adapter=adapter,
                phase="initial",
                is_archived=False,
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            return conversation
        except ConversationArchivedError:
            raise
        except SQLAlchemyError as exc:
            db.rollback()
            raise ServiceUnavailableError("chat memory unavailable") from exc

    def load_history(
        self, db: Session, conversation_id: str, limit: int = 20
    ) -> list[ChatMessage]:
        _validate_uuid(conversation_id)
        try:
            messages = (
                db.query(ChatMessage)
                .filter(ChatMessage.conversation_id == conversation_id)
                .order_by(ChatMessage.created_at.desc())
                .limit(max(1, limit))
                .all()
            )
            return list(reversed(messages))
        except SQLAlchemyError as exc:
            raise ServiceUnavailableError("chat history unavailable") from exc

    def load_state(self, db: Session, conversation_id: str) -> DiagnosticState:
        _validate_uuid(conversation_id)
        try:
            message = (
                db.query(ChatMessage)
                .filter(
                    ChatMessage.conversation_id == conversation_id,
                    ChatMessage.role == "assistant",
                )
                .order_by(ChatMessage.created_at.desc())
                .first()
            )
        except SQLAlchemyError as exc:
            raise ServiceUnavailableError("diagnostic state unavailable") from exc

        if not message:
            return DiagnosticState()

        metadata = message.metadata_json or {}
        raw_state = metadata.get("diagnosis_state")
        if raw_state is None:
            return DiagnosticState()

        try:
            return DiagnosticState.model_validate(raw_state)
        except (ValidationError, ValueError, TypeError):
            self._state_reset_conversations.add(conversation_id)
            return DiagnosticState()

    def append_turn(
        self,
        db: Session,
        conversation_id: str,
        user_message: str,
        assistant_message: str,
        state: DiagnosticState,
        sources: list[Any],
    ) -> None:
        _validate_uuid(conversation_id)
        state = DiagnosticState.model_validate(state)
        self._reject_ranked_diseases_without_sources(state.diseases_ranked)
        self._reject_ranked_diseases_without_sources(state.eliminated)

        metadata: dict[str, Any] = {
            "diagnosis_state": state.model_dump(mode="json"),
            "sources": [self._serialize_source(source) for source in sources],
        }
        if conversation_id in self._state_reset_conversations:
            metadata["system_note"] = STATE_RESET_NOTE

        now = datetime.utcnow()
        user_record = ChatMessage(
            id=str(uuid4()),
            conversation_id=conversation_id,
            role="user",
            content=user_message,
            metadata_json={},
            created_at=now,
        )
        assistant_record = ChatMessage(
            id=str(uuid4()),
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_message,
            metadata_json=metadata,
            created_at=datetime.utcnow(),
        )
        try:
            db.add(user_record)
            db.flush()
            db.add(assistant_record)
            conversation = (
                db.query(ChatConversation)
                .filter(ChatConversation.id == conversation_id)
                .first()
            )
            if conversation:
                conversation.phase = state.phase
                conversation.updated_at = datetime.utcnow()
            db.commit()
            self._state_reset_conversations.discard(conversation_id)
        except SQLAlchemyError as exc:
            db.rollback()
            raise ServiceUnavailableError("failed to append chat turn") from exc

    def _serialize_source(self, source: Any) -> dict[str, Any]:
        if hasattr(source, "model_dump"):
            return source.model_dump(mode="json")
        if isinstance(source, dict):
            return source
        return {"value": str(source)}

    @staticmethod
    def _reject_ranked_diseases_without_sources(diseases: list[RankedDisease]) -> None:
        invalid_names = [disease.name for disease in diseases if not disease.sources]
        if invalid_names:
            raise InvalidDiagnosticStateError(
                "ranked diseases must include at least one source: "
                + ", ".join(invalid_names)
            )
