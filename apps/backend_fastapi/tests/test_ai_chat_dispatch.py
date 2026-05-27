"""Integration tests for backwards-compatible dispatch on `POST /api/v1/ai/chat`.

Covers task 17.2:
- Request without `conversation_id` returns the existing single-shot response
  shape with all multi-turn fields left at their defaults (None).
- Request with `conversation_id` is dispatched to the diagnostic orchestrator
  and returns the enriched response shape (`conversation_id`, `phase`,
  `diagnosis_state`, `triage_level`).
- Request with an invalid `conversation_id` (not a UUID) returns HTTP 422 with
  error code ``INVALID_CONVERSATION_ID``.

Requirements: 8.1, 8.5, 8.6
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.routes import ai as ai_route
from app.core.dependencies import get_optional_current_user
from app.database.cloud_models import User
from app.main import app
from app.schemas.ai import AIChatResponse
from app.schemas.diagnostic import DiagnosticState, RankedDisease


# ─── Test user fixture ──────────────────────────────────────────────────────


def _make_test_user() -> User:
    """Build a lightweight `User` ORM instance for dependency overrides.

    We do not persist this user; the route only reads ``current_user.id`` after
    auth resolves, and the orchestrator path is monkey-patched in the
    multi-turn tests, so a non-persisted ORM object is sufficient.
    """
    return User(
        id=str(uuid4()),
        username="dispatch_tester",
        email="dispatch_tester@test.com",
        password_hash="hashed",
        full_name="Dispatch Tester",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture()
def authenticated_client():
    """`TestClient` with ``get_optional_current_user`` overridden to a test user.

    Multi-turn dispatch (`conversation_id` present) requires authentication;
    overriding the dependency keeps the test focused on routing/dispatch rather
    than JWT minting and DB-backed user lookup.
    """
    user = _make_test_user()
    app.dependency_overrides[get_optional_current_user] = lambda: user
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_optional_current_user, None)


@pytest.fixture()
def anonymous_client():
    """Plain `TestClient` with no auth override (single-shot path)."""
    return TestClient(app)


# ─── Test 1: backwards-compatible single-shot path ──────────────────────────


def test_chat_without_conversation_id_returns_legacy_shape(
    anonymous_client: TestClient,
) -> None:
    """Requests without ``conversation_id`` must keep the existing shape.

    Validates Requirement 8.1: existing API consumers that do not send a
    ``conversation_id`` continue to receive the single-shot response with
    ``diagnosis_state``/``phase``/``triage_level`` left at their defaults.
    """
    response = anonymous_client.post(
        "/api/v1/ai/chat",
        json={"message": "Tôi bị đau họng", "adapter": "medical"},
    )

    assert response.status_code == 200
    payload = response.json()

    # Existing fields are populated.
    assert payload["adapter"] == "medical"
    assert payload["content"]
    assert "provider" in payload
    assert "model" in payload
    assert isinstance(payload["sources"], list)

    # Multi-turn fields stay at their backwards-compatible defaults.
    assert payload["conversation_id"] is None
    assert payload["phase"] is None
    assert payload["diagnosis_state"] is None
    assert payload["triage_level"] is None
    assert payload["image_findings"] is None
    assert payload["image_modality"] is None


# ─── Test 2: enriched multi-turn dispatch path ──────────────────────────────


def test_chat_with_conversation_id_returns_enriched_response(
    authenticated_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Requests with a valid ``conversation_id`` are routed to ``diagnose_turn``.

    Validates Requirement 8.6: the enriched ``AIChatResponse`` carries
    ``conversation_id``, ``phase``, ``diagnosis_state`` (and ``triage_level``)
    on the multi-turn path. ``diagnose_turn`` is monkey-patched so the test
    does not require a live DB, RAG engine, or LLM.
    """
    conversation_id = str(uuid4())

    expected_state = DiagnosticState(
        diseases_ranked=[
            RankedDisease(
                name="Viêm họng cấp",
                probability=0.62,
                severity="medium",
                sources=["kb_001"],
            )
        ],
        symptoms_collected=["đau họng"],
        questions_asked=[],
        phase="questioning",
        turn_count=1,
        triage_level="yellow",
    )

    captured: dict = {}

    async def fake_diagnose_turn(*, payload, conversation_id, user_id):
        # Record the call so we can assert routing happened.
        captured["payload_message"] = payload.message
        captured["conversation_id"] = conversation_id
        captured["user_id"] = user_id
        return AIChatResponse(
            provider="test-provider",
            model="test-model",
            adapter=payload.adapter,
            content="Bạn có sốt kèm theo không?",
            fallback_used=False,
            rag_used=True,
            sources=[],
            conversation_id=conversation_id,
            phase="questioning",
            diagnosis_state=expected_state,
            triage_level="yellow",
            image_findings=None,
            image_modality=None,
        )

    monkeypatch.setattr(ai_route, "diagnose_turn", fake_diagnose_turn)

    response = authenticated_client.post(
        "/api/v1/ai/chat",
        json={
            "message": "Tôi đau họng 2 ngày",
            "adapter": "medical",
            "conversation_id": conversation_id,
        },
    )

    assert response.status_code == 200
    payload = response.json()

    # Routing actually delegated to the orchestrator.
    assert captured["conversation_id"] == conversation_id
    assert captured["payload_message"] == "Tôi đau họng 2 ngày"
    assert captured["user_id"]  # populated from the overridden auth dep

    # Enriched fields are present.
    assert payload["conversation_id"] == conversation_id
    assert payload["phase"] == "questioning"
    assert payload["triage_level"] == "yellow"
    assert payload["diagnosis_state"] is not None
    assert payload["diagnosis_state"]["phase"] == "questioning"
    assert payload["diagnosis_state"]["turn_count"] == 1
    assert payload["diagnosis_state"]["diseases_ranked"][0]["name"] == "Viêm họng cấp"
    assert payload["diagnosis_state"]["symptoms_collected"] == ["đau họng"]


# ─── Test 3: invalid UUID conversation_id ───────────────────────────────────


def test_chat_with_invalid_uuid_conversation_id_returns_422(
    authenticated_client: TestClient,
) -> None:
    """Non-UUID ``conversation_id`` values are rejected with HTTP 422.

    Validates Requirement 8.5: the orchestrator rejects malformed
    conversation IDs (length ≠ 36 OR not a valid UUID) before doing any DB
    work, returning ``INVALID_CONVERSATION_ID``.
    """
    # Length != 36 → caught by the length check.
    # Note: ``app.main.http_exception_handler`` flattens the ``HTTPException``
    # ``detail`` dict into top-level ``code``/``message`` keys.
    short_response = authenticated_client.post(
        "/api/v1/ai/chat",
        json={
            "message": "Tôi bị sốt",
            "adapter": "medical",
            "conversation_id": "not-a-uuid",
        },
    )
    assert short_response.status_code == 422
    assert short_response.json()["code"] == "INVALID_CONVERSATION_ID"

    # 36-character string that is not a real UUID → caught by UUID parsing.
    bad_uuid_36 = "x" * 36
    bad_response = authenticated_client.post(
        "/api/v1/ai/chat",
        json={
            "message": "Tôi bị sốt",
            "adapter": "medical",
            "conversation_id": bad_uuid_36,
        },
    )
    assert bad_response.status_code == 422
    assert bad_response.json()["code"] == "INVALID_CONVERSATION_ID"
