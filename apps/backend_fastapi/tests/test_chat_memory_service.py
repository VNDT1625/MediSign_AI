from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.cloud_models import ChatConversation, ChatMessage
from app.schemas.diagnostic import DiagnosticState, RankedDisease
from app.services.chat_memory_service import (
    InvalidDiagnosticStateError,
    ServiceUnavailableError,
    STATE_RESET_NOTE,
    ChatMemoryService,
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def _conversation(db_session) -> ChatConversation:
    conversation = ChatConversation(id=str(uuid4()), user_id=str(uuid4()), adapter="medical")
    db_session.add(conversation)
    db_session.commit()
    return conversation


def test_load_state_returns_default_for_empty_conversation(db_session) -> None:
    service = ChatMemoryService()
    conversation = _conversation(db_session)

    state = service.load_state(db_session, conversation.id)

    assert state.phase == "initial"
    assert state.turn_count == 0
    assert state.diseases_ranked == []
    assert state.eliminated == []
    assert state.symptoms_collected == []
    assert state.questions_asked == []


def test_append_turn_rolls_back_both_messages_on_mid_transaction_failure(
    db_session, monkeypatch
) -> None:
    service = ChatMemoryService()
    conversation = _conversation(db_session)
    state = DiagnosticState(
        diseases_ranked=[
            RankedDisease(
                name="Cúm mùa",
                probability=0.7,
                severity="low",
                sources=["kb-flu"],
            )
        ],
        turn_count=1,
    )

    original_add = db_session.add
    add_calls = 0

    def failing_add(instance):
        nonlocal add_calls
        add_calls += 1
        if add_calls == 2:
            raise SQLAlchemyError("simulated assistant insert failure")
        original_add(instance)

    monkeypatch.setattr(db_session, "add", failing_add)

    with pytest.raises(ServiceUnavailableError):
        service.append_turn(
            db_session,
            conversation.id,
            "Tôi bị sốt",
            "Tôi cần hỏi thêm.",
            state,
            [],
        )

    messages = db_session.query(ChatMessage).filter_by(conversation_id=conversation.id).all()
    assert messages == []


def test_append_turn_rejects_ranked_disease_without_sources(db_session) -> None:
    service = ChatMemoryService()
    conversation = _conversation(db_session)
    state = DiagnosticState(
        diseases_ranked=[
            RankedDisease(
                name="Viêm họng",
                probability=0.6,
                severity="medium",
                sources=[],
            )
        ]
    )

    with pytest.raises(InvalidDiagnosticStateError):
        service.append_turn(
            db_session,
            conversation.id,
            "Đau họng",
            "Tôi sẽ hỏi thêm.",
            state,
            [],
        )

    assert db_session.query(ChatMessage).filter_by(conversation_id=conversation.id).count() == 0


def test_load_state_validation_error_returns_default_and_marks_next_append(
    db_session,
) -> None:
    service = ChatMemoryService()
    conversation = _conversation(db_session)
    bad_message = ChatMessage(
        id=str(uuid4()),
        conversation_id=conversation.id,
        role="assistant",
        content="bad state",
        metadata_json={
            "diagnosis_state": {
                "phase": "not-a-phase",
                "turn_count": -1,
            }
        },
    )
    db_session.add(bad_message)
    db_session.commit()

    state = service.load_state(db_session, conversation.id)

    assert state.phase == "initial"
    assert state.turn_count == 0

    valid_state = DiagnosticState(
        diseases_ranked=[
            RankedDisease(
                name="Cảm lạnh",
                probability=0.5,
                severity="low",
                sources=["kb-cold"],
            )
        ],
        turn_count=1,
    )
    service.append_turn(
        db_session,
        conversation.id,
        "Tôi bị nghẹt mũi",
        "Tôi sẽ hỏi thêm về triệu chứng.",
        valid_state,
        [],
    )

    latest_assistant = (
        db_session.query(ChatMessage)
        .filter_by(conversation_id=conversation.id, role="assistant")
        .order_by(ChatMessage.created_at.desc())
        .first()
    )
    assert latest_assistant.metadata_json["system_note"] == STATE_RESET_NOTE
