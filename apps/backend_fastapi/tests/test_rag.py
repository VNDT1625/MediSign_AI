from fastapi.testclient import TestClient

from app.main import app


def test_rag_status_loads_knowledge_base() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/ai/rag/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["documents"] > 0


def test_rag_search_finds_drug_interaction_by_brand_name() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/ai/rag/search",
        json={"query": "Panadol uống với rượu được không?", "top_k": 3},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["hits"]
    assert any("Paracetamol" in hit["title"] for hit in payload["hits"])
    assert "record_id=" in payload["context"]


def test_ai_chat_returns_rag_sources_in_fallback_mode() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "Người 60 tuổi cần bao nhiêu canxi mỗi ngày?", "adapter": "medical"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["fallback_used"] is True
    assert payload["rag_used"] is True
    assert payload["sources"]
