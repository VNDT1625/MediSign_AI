from fastapi.testclient import TestClient

from app.main import app


def test_medicine_scan_success() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/medicine/scan",
        json={
            "extracted_text": "Paracetamol 500mg",
            "current_medications": ["alcohol"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["risk_level"] in {"low", "medium", "high"}
    assert isinstance(payload["warnings"], list)


def test_medicine_scan_detects_vietnamese_alcohol_keyword() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/medicine/scan",
        json={
            "extracted_text": "Paracetamol 500mg",
            "current_medications": ["Rượu"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["risk_level"] == "high"
    assert any("ruou bia" in warning.lower() for warning in payload["warnings"])


def test_medicine_scan_does_not_downgrade_high_risk() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/medicine/scan",
        json={
            "extracted_text": "Paracetamol + Ibuprofen",
            "current_medications": ["alcohol", "aspirin"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["risk_level"] == "high"
    assert len(payload["warnings"]) == 2
