from app.main import app


def test_triage_compatibility_import_only() -> None:
    assert app is not None
