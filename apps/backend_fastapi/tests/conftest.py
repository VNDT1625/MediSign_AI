"""Pytest bootstrap.

This file runs *before* any test module is imported, which lets us:

1.  Force the test suite to use an isolated SQLite database so contributors
    can run ``pytest`` without a Postgres container running locally. CI
    pipelines that *do* provide a Postgres instance can override the
    ``DATABASE_URL`` (or ``BACKEND_DATABASE_URL``) env var before pytest
    starts, in which case we honour their choice.

2.  Set sensible defaults for the rest of the backend settings so the import
    of ``app.main`` doesn't blow up because of missing ``BACKEND_*`` keys.

3.  Configure Hypothesis with a fast profile suitable for the property
    tests scattered across the suite.
"""

from __future__ import annotations

import os
from pathlib import Path

# ─── Database isolation ──────────────────────────────────────────────────────
# Honour explicit overrides from CI / dev shells; otherwise default to a
# disposable SQLite file under the test workspace.
_DEFAULT_TEST_DB = Path(__file__).resolve().parent / "_test_backend.sqlite3"
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_DEFAULT_TEST_DB}")
os.environ.setdefault("BACKEND_DATABASE_URL", os.environ["DATABASE_URL"])

# Disable rate limiting so unit tests don't trip 429 responses.
os.environ.setdefault("BACKEND_RATE_LIMIT_ENABLED", "false")

# Note: BACKEND_RAG_ENABLED is left unset so tests can opt-in. The default
# value in `Settings` (rag_enabled=True) is kept for tests that exercise the
# RAG status endpoint.

# Keep auth secret deterministic in tests, but long enough to satisfy the
# production-secret guard.
os.environ.setdefault(
    "BACKEND_JWT_SECRET_KEY",
    "tests-only-not-a-real-secret-tests-only-not-a-real-secret",
)


# ─── Hypothesis profile ──────────────────────────────────────────────────────
from hypothesis import HealthCheck, settings  # noqa: E402  (after env setup)


# Fast profile for the backend test suite: keeps property coverage meaningful
# while keeping the suite snappy in CI / local runs.
settings.register_profile(
    "backend",
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.load_profile("backend")


# ─── Demo-user seeding ───────────────────────────────────────────────────────
import uuid

import pytest  # noqa: E402  (after env setup)


@pytest.fixture(scope="session", autouse=True)
def _seed_demo_user():
    """Seed the canonical `demo@medisign.ai` user once per test session.

    Several tests assume this user exists with the password ``ChangeMe123``.
    Previously they only worked against externally-provisioned Postgres
    instances; with the SQLite fallback we provision the user here so the
    suite passes on a fresh checkout.
    """
    from app.core.security import hash_password
    from app.database.base import Base, SessionLocal, engine
    from app.database import cloud_models, local_models  # noqa: F401
    from app.database.cloud_models import User

    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        existing = session.query(User).filter(User.email == "demo@medisign.ai").first()
        if existing is None:
            session.add(
                User(
                    id=str(uuid.uuid4()),
                    username="demo",
                    email="demo@medisign.ai",
                    full_name="Demo User",
                    password_hash=hash_password("ChangeMe123"),
                    account_type="user",
                    is_active=True,
                    is_email_verified=True,
                )
            )
            session.commit()
    finally:
        session.close()
    yield
