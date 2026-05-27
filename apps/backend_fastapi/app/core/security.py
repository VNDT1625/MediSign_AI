from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import HTTPException, status

from app.core.config import settings


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        settings.password_hash_iterations,
    ).hex()
    return f"pbkdf2_sha256${settings.password_hash_iterations}${salt}${password_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected_hash = stored_hash.split("$")
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    candidate_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        int(iterations),
    ).hex()
    return hmac.compare_digest(candidate_hash, expected_hash)


def create_access_token(subject: str) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_minutes)
    return _create_token(subject=subject, token_type="access", expires_at=expires_at)


def create_refresh_token(subject: str) -> str:
    expires_at = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_days)
    return _create_token(subject=subject, token_type="refresh", expires_at=expires_at)


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "AUTH_INVALID_TOKEN", "message": "Token khong hop le"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as error:
        raise credentials_exception from error

    token_type = payload.get("type")
    if token_type != expected_type:
        raise credentials_exception

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise credentials_exception

    return payload


def _create_token(subject: str, token_type: str, expires_at: datetime) -> str:
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": datetime.now(UTC),
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


# ─── Production secret validation ────────────────────────────────────────────

DEFAULT_INSECURE_JWT_SECRET = "change-this-secret-key-at-least-32-bytes"
_PRODUCTION_ENVS = {"production", "prod", "live"}


def assert_production_secret() -> None:
    """Refuse to start the app in production with the default JWT secret.

    Called from the FastAPI lifespan. In non-production environments the
    function only logs a warning so local developers don't get blocked.
    """
    import logging

    logger = logging.getLogger("medisign.security")
    secret = settings.jwt_secret_key or ""
    env = (settings.app_env or "").strip().lower()

    is_default = secret == DEFAULT_INSECURE_JWT_SECRET
    is_too_short = len(secret.encode("utf-8")) < 32

    if env in _PRODUCTION_ENVS and (is_default or is_too_short):
        raise RuntimeError(
            "BACKEND_JWT_SECRET_KEY is missing, default, or shorter than 32 bytes. "
            "Set a strong random secret before starting the app in production."
        )

    if is_default:
        logger.warning(
            "BACKEND_JWT_SECRET_KEY is using the default placeholder. "
            "This is acceptable for local dev only — rotate before staging/prod."
        )
    elif is_too_short:
        logger.warning(
            "BACKEND_JWT_SECRET_KEY is shorter than 32 bytes (current=%d). "
            "Use a longer random secret in any shared environment.",
            len(secret.encode("utf-8")),
        )
