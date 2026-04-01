from fastapi.testclient import TestClient

from app.main import app


def test_auth_login_and_refresh_success() -> None:
    client = TestClient(app)

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "demo@medisign.ai", "password": "ChangeMe123"},
    )
    assert login_response.status_code == 200

    login_payload = login_response.json()
    tokens = login_payload["tokens"]
    assert tokens["token_type"] == "bearer"
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200

    refresh_payload = refresh_response.json()
    assert refresh_payload["access_token"]
    assert refresh_payload["refresh_token"]


def test_auth_login_invalid_credentials_error_envelope() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "demo@medisign.ai", "password": "wrong-password"},
    )
    assert response.status_code == 401

    payload = response.json()
    assert payload["code"] == "AUTH_INVALID_CREDENTIALS"
    assert payload["request_id"]
