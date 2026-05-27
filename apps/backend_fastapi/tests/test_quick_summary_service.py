"""Unit tests for QuickSummaryService.latest.

Validates: Requirements 11.1, 11.2, 11.3, 11.4
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.database.cloud_models import ChatConversation, ChatMessage
from app.schemas.diagnostic import DiagnosticState, RankedDisease
from app.services.quick_summary_service import (
    ConversationNotFoundError,
    QuickSummaryService,
)


@pytest.fixture
def service() -> QuickSummaryService:
    return QuickSummaryService()


@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock()


def _make_conversation(
    user_id: str = "user-1",
    conv_id: str | None = None,
    is_archived: bool = False,
) -> ChatConversation:
    conv = ChatConversation()
    conv.id = conv_id or str(uuid4())
    conv.user_id = user_id
    conv.adapter = "medical"
    conv.phase = "questioning"
    conv.is_archived = is_archived
    conv.created_at = datetime.utcnow()
    conv.updated_at = datetime.utcnow()
    return conv


def _make_assistant_message(
    conversation_id: str,
    state: DiagnosticState,
) -> ChatMessage:
    msg = ChatMessage()
    msg.id = str(uuid4())
    msg.conversation_id = conversation_id
    msg.role = "assistant"
    msg.content = "Test response"
    msg.metadata_json = {"diagnosis_state": state.model_dump(mode="json")}
    msg.created_at = datetime.utcnow()
    return msg


class TestQuickSummaryServiceLatest:
    """Tests for QuickSummaryService.latest method."""

    def test_returns_summary_for_specific_conversation(
        self, service: QuickSummaryService, mock_db: MagicMock
    ) -> None:
        """When conversation_id is provided, load that conversation and derive summary."""
        user_id = "user-1"
        conv = _make_conversation(user_id=user_id)
        state = DiagnosticState(
            symptoms_collected=["sốt", "đau họng"],
            diseases_ranked=[
                RankedDisease(
                    name="Viêm họng",
                    probability=0.7,
                    severity="low",
                    sources=["kb-1"],
                )
            ],
            triage_level="green",
            phase="conclusion",
            turn_count=3,
        )
        msg = _make_assistant_message(conv.id, state)

        # Mock the DB queries
        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock

        # First call: find conversation by id
        filter_mock.first.return_value = conv
        # Second call: find latest assistant message
        order_mock = MagicMock()
        filter_mock.order_by.return_value = order_mock
        order_mock.first.return_value = msg

        result = service.latest(mock_db, user_id, conversation_id=conv.id)

        assert result.conversation_id == conv.id
        assert result.symptoms_collected == ["sốt", "đau họng"]
        assert len(result.diseases_ranked) == 1
        assert result.diseases_ranked[0].name == "Viêm họng"
        assert result.triage_level == "green"
        assert "tự chăm sóc tại nhà" in result.recommendation

    def test_returns_summary_for_most_recent_conversation(
        self, service: QuickSummaryService, mock_db: MagicMock
    ) -> None:
        """When no conversation_id, find the user's most recent non-archived conversation."""
        user_id = "user-1"
        conv = _make_conversation(user_id=user_id)
        state = DiagnosticState(
            symptoms_collected=["đau ngực"],
            diseases_ranked=[
                RankedDisease(
                    name="Nhồi máu cơ tim",
                    probability=0.5,
                    severity="high",
                    sources=["kb-2"],
                )
            ],
            triage_level="red",
            phase="conclusion",
            turn_count=4,
        )
        msg = _make_assistant_message(conv.id, state)

        # Track calls to db.query to return different chains for
        # ChatConversation vs ChatMessage queries
        call_count = {"n": 0}

        def query_side_effect(model):
            call_count["n"] += 1
            chain = MagicMock()
            if call_count["n"] == 1:
                # First query: ChatConversation — filter → order_by → first
                filter_mock = MagicMock()
                chain.filter.return_value = filter_mock
                order_mock = MagicMock()
                filter_mock.order_by.return_value = order_mock
                order_mock.first.return_value = conv
            else:
                # Second query: ChatMessage — filter → order_by → first
                filter_mock = MagicMock()
                chain.filter.return_value = filter_mock
                order_mock = MagicMock()
                filter_mock.order_by.return_value = order_mock
                order_mock.first.return_value = msg
            return chain

        mock_db.query.side_effect = query_side_effect

        result = service.latest(mock_db, user_id, conversation_id=None)

        assert result.conversation_id == conv.id
        assert result.triage_level == "red"
        assert "cơ sở y tế ngay lập tức" in result.recommendation

    def test_raises_when_conversation_not_found(
        self, service: QuickSummaryService, mock_db: MagicMock
    ) -> None:
        """Raises ConversationNotFoundError when conversation_id doesn't exist."""
        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = None

        with pytest.raises(ConversationNotFoundError):
            service.latest(mock_db, "user-1", conversation_id="nonexistent-id-000000000000000")

    def test_raises_when_conversation_belongs_to_other_user(
        self, service: QuickSummaryService, mock_db: MagicMock
    ) -> None:
        """Raises ConversationNotFoundError when conversation belongs to another user."""
        conv = _make_conversation(user_id="other-user")

        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = conv

        with pytest.raises(ConversationNotFoundError):
            service.latest(mock_db, "user-1", conversation_id=conv.id)

    def test_raises_when_no_active_conversation(
        self, service: QuickSummaryService, mock_db: MagicMock
    ) -> None:
        """Raises ConversationNotFoundError when user has no active conversations."""
        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        order_mock = MagicMock()
        filter_mock.order_by.return_value = order_mock
        order_mock.first.return_value = None

        with pytest.raises(ConversationNotFoundError):
            service.latest(mock_db, "user-1", conversation_id=None)

    def test_returns_default_state_when_no_messages(
        self, service: QuickSummaryService, mock_db: MagicMock
    ) -> None:
        """Returns summary with empty state when conversation has no assistant messages."""
        user_id = "user-1"
        conv = _make_conversation(user_id=user_id)

        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        # First call: find conversation
        filter_mock.first.return_value = conv
        # Second call: no assistant messages
        order_mock = MagicMock()
        filter_mock.order_by.return_value = order_mock
        order_mock.first.return_value = None

        result = service.latest(mock_db, user_id, conversation_id=conv.id)

        assert result.conversation_id == conv.id
        assert result.symptoms_collected == []
        assert result.diseases_ranked == []
        assert result.triage_level is None
        assert "Chưa đủ thông tin" in result.recommendation

    def test_recommendation_yellow(
        self, service: QuickSummaryService, mock_db: MagicMock
    ) -> None:
        """Yellow triage level produces monitor/follow-up recommendation."""
        user_id = "user-1"
        conv = _make_conversation(user_id=user_id)
        state = DiagnosticState(
            symptoms_collected=["ho"],
            diseases_ranked=[
                RankedDisease(
                    name="Cảm cúm",
                    probability=0.45,
                    severity="medium",
                    sources=["kb-3"],
                )
            ],
            triage_level="yellow",
            phase="questioning",
            turn_count=2,
        )
        msg = _make_assistant_message(conv.id, state)

        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = conv
        order_mock = MagicMock()
        filter_mock.order_by.return_value = order_mock
        order_mock.first.return_value = msg

        result = service.latest(mock_db, user_id, conversation_id=conv.id)

        assert result.triage_level == "yellow"
        assert "Theo dõi triệu chứng" in result.recommendation

    def test_handles_invalid_metadata_gracefully(
        self, service: QuickSummaryService, mock_db: MagicMock
    ) -> None:
        """Returns default state when metadata contains invalid diagnosis_state."""
        user_id = "user-1"
        conv = _make_conversation(user_id=user_id)

        msg = ChatMessage()
        msg.id = str(uuid4())
        msg.conversation_id = conv.id
        msg.role = "assistant"
        msg.content = "Test"
        msg.metadata_json = {"diagnosis_state": {"phase": "INVALID_PHASE_VALUE"}}
        msg.created_at = datetime.utcnow()

        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = conv
        order_mock = MagicMock()
        filter_mock.order_by.return_value = order_mock
        order_mock.first.return_value = msg

        result = service.latest(mock_db, user_id, conversation_id=conv.id)

        # Should fall back to default state
        assert result.symptoms_collected == []
        assert result.triage_level is None
