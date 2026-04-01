"""Tests for protected endpoints requiring authentication."""

from fastapi.testclient import TestClient

from app.main import app


def test_protected_endpoint_without_token_fails() -> None:
    """Protected endpoint should return 403 without token."""
    client = TestClient(app)
    response = client.get("/api/v1/consult/triage/history")

    assert response.status_code == 403
    payload = response.json()
    assert "detail" in payload


def test_protected_endpoint_with_invalid_token_fails() -> None:
    """Protected endpoint should return 401 with invalid token."""
    client = TestClient(app)
    response = client.get(
        "/api/v1/consult/triage/history",
        headers={"Authorization": "Bearer invalid_token_here"},
    )

    assert response.status_code == 401
    payload = response.json()
    assert payload["code"] == "AUTH_INVALID_TOKEN"
    assert payload["message"]
    assert payload["request_id"]


def test_protected_endpoint_with_valid_token_succeeds() -> None:
    """Protected endpoint should work with valid access token."""
    client = TestClient(app)

    # First login to get valid token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "demo@medisign.ai", "password": "ChangeMe123"},
    )
    assert login_response.status_code == 200
    login_payload = login_response.json()
    access_token = login_payload["tokens"]["access_token"]

    # Then access protected endpoint
    response = client.get(
        "/api/v1/consult/triage/history",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)  # Should return list of triage history
