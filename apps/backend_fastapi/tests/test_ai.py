from fastapi.testclient import TestClient

from app.main import app


def test_ai_status_works_without_model_server() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/ai/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"]
    assert payload["model"]
    assert "adapter" in payload["detail"]


def test_ai_chat_uses_fallback_without_model_server() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "Tôi bị đau họng", "adapter": "medical"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["fallback_used"] is True
    assert payload["adapter"] == "medical"
    assert payload["content"]
