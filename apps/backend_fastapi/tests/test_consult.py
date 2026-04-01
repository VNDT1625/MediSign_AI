from fastapi.testclient import TestClient

from app.main import app


def test_consult_triage_success() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/consult/triage",
        json={"symptom_text": "Dau hong nhe 2 ngay", "locale": "vi-VN"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["urgency_level"] == "non_emergency"
    assert isinstance(payload["recommendations"], list)


def test_consult_triage_validation_error_envelope() -> None:
    client = TestClient(app)
    response = client.post("/api/v1/consult/triage", json={"symptom_text": "a"})

    assert response.status_code == 422
    payload = response.json()
    assert payload["code"] == "VALIDATION_ERROR"
    assert payload["message"]
    assert payload["request_id"]


def test_consult_triage_supports_accented_emergency_keywords() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/consult/triage",
        json={"symptom_text": "Tôi bị khó thở và đau ngực", "locale": "vi-VN"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["urgency_level"] == "emergency"


def test_consult_triage_ignores_negated_emergency_phrase() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/consult/triage",
        json={"symptom_text": "Tôi không đau ngực nhưng khá mệt mỏi", "locale": "vi-VN"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["urgency_level"] == "urgent"


def test_consult_triage_prioritizes_emergency_over_urgent() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/consult/triage",
        json={"symptom_text": "Sốt cao kèm khó thở", "locale": "vi-VN"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["urgency_level"] == "emergency"


def test_consult_triage_emergency_edge_cases() -> None:
    """Test edge cases: emergency keywords with typos, mixed case, extra spaces."""
    client = TestClient(app)

    # Case 1: Emergency with typo variations
    response = client.post(
        "/api/v1/consult/triage",
        json={"symptom_text": "Kho  tho  nhieu, dau nguc", "locale": "vi-VN"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["urgency_level"] == "emergency", "Should detect 'kho tho' with extra spaces"

    # Case 2: Mixed case emergency
    response = client.post(
        "/api/v1/consult/triage",
        json={"symptom_text": "DAU NGUC rat nhieu", "locale": "vi-VN"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["urgency_level"] == "emergency", "Should detect 'dau nguc' in uppercase"

    # Case 3: Emergency keyword at end
    response = client.post(
        "/api/v1/consult/triage",
        json={"symptom_text": "Toi cam thay rat met va ngat", "locale": "vi-VN"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["urgency_level"] == "emergency", "Should detect 'ngat' at end"


def test_consult_triage_urgent_vs_emergency() -> None:
    """Test boundary between urgent and emergency."""
    client = TestClient(app)

    # Urgent case
    response = client.post(
        "/api/v1/consult/triage",
        json={"symptom_text": "Sot cao 39 do, dau dau nhieu", "locale": "vi-VN"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["urgency_level"] == "urgent", "Should be urgent, not emergency"

    # Emergency case
    response = client.post(
        "/api/v1/consult/triage",
        json={"symptom_text": "Sot cao va kho tho", "locale": "vi-VN"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["urgency_level"] == "emergency", "Should be emergency when has 'kho tho'"
