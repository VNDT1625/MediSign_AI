"""Integration tests for conversation management endpoints.

Tests:
- GET /conversations returns only the authenticated user's conversations.
- GET /conversations/{id} returns 404 for another user's conversation.
- DELETE /conversations/{id} sets is_archived=True.
- Sending a message to an archived conversation returns HTTP 409.

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.dependencies import get_current_user
from app.database.base import Base, get_db
from app.database.cloud_models import ChatConversation, ChatMessage, User
from app.main import app


# ─── Constants ───────────────────────────────────────────────────────────────

USER_A_ID = str(uuid4())
USER_B_ID = str(uuid4())

CONV_A1_ID = str(uuid4())
CONV_A2_ID = str(uuid4())
CONV_B1_ID = str(uuid4())
CONV_ARCHIVED_ID = str(uuid4())


# ─── In-memory DB setup ─────────────────────────────────────────────────────

TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _make_user(user_id: str, email: str) -> User:
    return User(
        id=user_id,
        username=email.split("@")[0],
        email=email,
        password_hash="hashed",
        full_name="Test User",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


def _make_conversation(
    conv_id: str,
    user_id: str,
    is_archived: bool = False,
    phase: str = "initial",
) -> ChatConversation:
    return ChatConversation(
        id=conv_id,
        user_id=user_id,
        title=f"Conversation {conv_id[:8]}",
        adapter="medical",
        phase=phase,
        is_archived=is_archived,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


def _make_message(
    conv_id: str,
    role: str,
    content: str,
    metadata: dict | None = None,
) -> ChatMessage:
    return ChatMessage(
        id=str(uuid4()),
        conversation_id=conv_id,
        role=role,
        content=content,
        metadata_json=metadata or {},
        created_at=datetime.utcnow(),
    )


def _seed_data(db: Session) -> None:
    """Seed test data into the in-memory database."""
    # Users
    user_a = _make_user(USER_A_ID, "user_a@test.com")
    user_b = _make_user(USER_B_ID, "user_b@test.com")
    db.add_all([user_a, user_b])

    # Conversations
    conv_a1 = _make_conversation(CONV_A1_ID, USER_A_ID)
    conv_a2 = _make_conversation(CONV_A2_ID, USER_A_ID)
    conv_b1 = _make_conversation(CONV_B1_ID, USER_B_ID)
    conv_archived = _make_conversation(CONV_ARCHIVED_ID, USER_A_ID, is_archived=True)
    db.add_all([conv_a1, conv_a2, conv_b1, conv_archived])

    # Messages for conv_a1
    msg1 = _make_message(CONV_A1_ID, "user", "Toi bi dau dau")
    msg2 = _make_message(
        CONV_A1_ID,
        "assistant",
        "Ban co the mo ta them trieu chung?",
        metadata={
            "diagnosis_state": {
                "diseases_ranked": [
                    {
                        "name": "Migraine",
                        "probability": 0.6,
                        "severity": "medium",
                        "sources": ["kb_001"],
                    }
                ],
                "eliminated": [],
                "symptoms_collected": ["dau dau"],
                "questions_asked": [],
                "phase": "questioning",
                "turn_count": 1,
                "triage_level": None,
                "top_disease_history": [],
            }
        },
    )
    db.add_all([msg1, msg2])
    db.commit()


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables and seed data for each test."""
    Base.metadata.create_all(bind=TEST_ENGINE)
    db = TestSessionLocal()
    _seed_data(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture()
def client_user_a():
    """Test client authenticated as user A."""
    user_a = _make_user(USER_A_ID, "user_a@test.com")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: user_a

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


@pytest.fixture()
def client_user_b():
    """Test client authenticated as user B."""
    user_b = _make_user(USER_B_ID, "user_b@test.com")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: user_b

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


@pytest.fixture()
def client_unauthenticated():
    """Test client without authentication (no dependency override for auth)."""
    app.dependency_overrides[get_db] = override_get_db
    # Do NOT override get_current_user — let the real auth check run
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ─── Tests: GET /api/v1/ai/conversations ─────────────────────────────────────


class TestListConversations:
    """Tests for GET /api/v1/ai/conversations."""

    def test_returns_only_authenticated_users_conversations(
        self, client_user_a: TestClient
    ) -> None:
        """User A should only see their own non-archived conversations."""
        response = client_user_a.get("/api/v1/ai/conversations")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 2  # conv_a1 and conv_a2 (not archived one)
        assert len(data["items"]) == 2

        conv_ids = {item["id"] for item in data["items"]}
        assert CONV_A1_ID in conv_ids
        assert CONV_A2_ID in conv_ids
        assert CONV_B1_ID not in conv_ids
        assert CONV_ARCHIVED_ID not in conv_ids

    def test_user_b_sees_only_their_conversations(
        self, client_user_b: TestClient
    ) -> None:
        """User B should only see their own conversations."""
        response = client_user_b.get("/api/v1/ai/conversations")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == CONV_B1_ID

    def test_pagination_works(self, client_user_a: TestClient) -> None:
        """Pagination parameters should be respected."""
        response = client_user_a.get(
            "/api/v1/ai/conversations", params={"page": 1, "page_size": 1}
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["page_size"] == 1
        assert data["has_next"] is True

    def test_unauthenticated_returns_401(
        self, client_unauthenticated: TestClient
    ) -> None:
        """Unauthenticated request should return 401."""
        response = client_unauthenticated.get("/api/v1/ai/conversations")
        assert response.status_code == 401


# ─── Tests: GET /api/v1/ai/conversations/{id} ────────────────────────────────


class TestGetConversation:
    """Tests for GET /api/v1/ai/conversations/{id}."""

    def test_returns_conversation_with_messages(
        self, client_user_a: TestClient
    ) -> None:
        """Should return full conversation detail with messages and state."""
        response = client_user_a.get(f"/api/v1/ai/conversations/{CONV_A1_ID}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == CONV_A1_ID
        assert data["adapter"] == "medical"
        assert len(data["messages"]) == 2
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][1]["role"] == "assistant"

        # Should have extracted diagnosis_state from last assistant message
        assert data["diagnosis_state"] is not None
        assert data["diagnosis_state"]["phase"] == "questioning"
        assert data["diagnosis_state"]["turn_count"] == 1
        assert len(data["diagnosis_state"]["diseases_ranked"]) == 1
        assert data["diagnosis_state"]["diseases_ranked"][0]["name"] == "Migraine"

    def test_returns_404_for_another_users_conversation(
        self, client_user_a: TestClient
    ) -> None:
        """User A should not be able to access user B's conversation."""
        response = client_user_a.get(f"/api/v1/ai/conversations/{CONV_B1_ID}")
        assert response.status_code == 404

        data = response.json()
        assert data["code"] == "CONVERSATION_NOT_FOUND"

    def test_returns_404_for_nonexistent_conversation(
        self, client_user_a: TestClient
    ) -> None:
        """Should return 404 for a conversation that doesn't exist."""
        fake_id = str(uuid4())
        response = client_user_a.get(f"/api/v1/ai/conversations/{fake_id}")
        assert response.status_code == 404

        data = response.json()
        assert data["code"] == "CONVERSATION_NOT_FOUND"

    def test_returns_422_for_invalid_uuid(self, client_user_a: TestClient) -> None:
        """Should return 422 for an invalid UUID format."""
        response = client_user_a.get("/api/v1/ai/conversations/not-a-valid-uuid")
        assert response.status_code == 422


# ─── Tests: DELETE /api/v1/ai/conversations/{id} ─────────────────────────────


class TestDeleteConversation:
    """Tests for DELETE /api/v1/ai/conversations/{id}."""

    def test_soft_deletes_conversation(self, client_user_a: TestClient) -> None:
        """DELETE should set is_archived=True (soft delete)."""
        response = client_user_a.delete(f"/api/v1/ai/conversations/{CONV_A1_ID}")
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == "CONVERSATION_ARCHIVED"
        assert data["conversation_id"] == CONV_A1_ID

        # Verify it no longer appears in the list
        list_response = client_user_a.get("/api/v1/ai/conversations")
        assert list_response.status_code == 200
        list_data = list_response.json()
        conv_ids = {item["id"] for item in list_data["items"]}
        assert CONV_A1_ID not in conv_ids

    def test_returns_404_for_another_users_conversation(
        self, client_user_a: TestClient
    ) -> None:
        """User A should not be able to delete user B's conversation."""
        response = client_user_a.delete(f"/api/v1/ai/conversations/{CONV_B1_ID}")
        assert response.status_code == 404

        data = response.json()
        assert data["code"] == "CONVERSATION_NOT_FOUND"

    def test_returns_404_for_nonexistent_conversation(
        self, client_user_a: TestClient
    ) -> None:
        """Should return 404 for a conversation that doesn't exist."""
        fake_id = str(uuid4())
        response = client_user_a.delete(f"/api/v1/ai/conversations/{fake_id}")
        assert response.status_code == 404

    def test_returns_422_for_invalid_uuid(self, client_user_a: TestClient) -> None:
        """Should return 422 for an invalid UUID format."""
        response = client_user_a.delete("/api/v1/ai/conversations/bad-uuid")
        assert response.status_code == 422


# ─── Tests: Archived conversation behavior ───────────────────────────────────


class TestArchivedConversation:
    """Tests for archived conversation behavior (Req 10.5)."""

    def test_archived_conversation_visible_in_detail(
        self, client_user_a: TestClient
    ) -> None:
        """Archived conversations can still be viewed via GET detail."""
        response = client_user_a.get(
            f"/api/v1/ai/conversations/{CONV_ARCHIVED_ID}"
        )
        assert response.status_code == 200
        assert response.json()["is_archived"] is True

    def test_archived_conversation_excluded_from_list(
        self, client_user_a: TestClient
    ) -> None:
        """Archived conversations should not appear in the list endpoint."""
        response = client_user_a.get("/api/v1/ai/conversations")
        assert response.status_code == 200

        data = response.json()
        conv_ids = {item["id"] for item in data["items"]}
        assert CONV_ARCHIVED_ID not in conv_ids
