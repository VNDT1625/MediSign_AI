from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.rate_limit import RateLimitExceeded, limiter
from app.core.security import assert_production_secret
from app.database.base import engine, Base
from app.database import cloud_models, local_models  # noqa: F401  ensure metadata

logger = logging.getLogger(__name__)

# Dev/test convenience: ensure tables exist before any request handler runs.
# Production deployments rely on Alembic migrations instead — see
# `alembic upgrade head`. We keep idempotent create_all() here for local dev,
# unit tests, and the SQLite fallback used by CI. In production we skip this
# step entirely so schema drift surfaces as an explicit migration failure
# rather than being silently masked by ORM-driven create.
_PRODUCTION_ENVS = {"production", "prod", "live"}


def _should_create_all() -> bool:
    env = (settings.app_env or "").strip().lower()
    if env in _PRODUCTION_ENVS:
        return False
    return True


if _should_create_all():
    Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Startup/shutdown lifecycle hook (replaces deprecated on_event)."""
    # Refuse to boot in production with a placeholder JWT secret.
    assert_production_secret()

    if _should_create_all():
        Base.metadata.create_all(bind=engine)

    if os.getenv("BACKEND_RAG_PRELOAD", "").lower() in {"1", "true", "yes"}:
        from app.services.rag_service import rag_service

        rag_service.status()

    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# Wire slowapi rate limiter (no-op when slowapi is missing or disabled).
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Return a structured payload that matches the rest of the API."""
    return JSONResponse(
        status_code=429,
        content={
            "code": "RATE_LIMIT_EXCEEDED",
            "message": "Quá nhiều yêu cầu. Vui lòng thử lại sau ít phút.",
            "details": {"limit": str(getattr(exc, "detail", ""))},
            "request_id": getattr(request.state, "request_id", None),
        },
    )


# ─── CORS ────────────────────────────────────────────────────────────────────
# - allow_origin_regex: localhost/127.0.0.1 by default for local dev
# - allow_origins: explicit list from BACKEND_CORS_ALLOWED_ORIGINS (comma-sep)
_extra_cors_origins = [
    origin.strip()
    for origin in (settings.cors_allowed_origins or "").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_extra_cors_origins,
    allow_origin_regex=settings.cors_allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
if _extra_cors_origins:
    logger.info("CORS additional allowed origins: %s", _extra_cors_origins)

app.include_router(api_router, prefix=settings.api_prefix)


@app.middleware("http")
async def attach_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "code": "VALIDATION_ERROR",
            "message": "Payload khong hop le",
            "details": {"errors": exc.errors()},
            "request_id": getattr(request.state, "request_id", None),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, dict):
        code = detail.get("code", "HTTP_ERROR")
        message = detail.get("message", "Yeu cau that bai")
        details = detail.get("details")
    else:
        code = "HTTP_ERROR"
        message = str(detail)
        details = None

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": code,
            "message": message,
            "details": details,
            "request_id": getattr(request.state, "request_id", None),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    _ = exc
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Co loi he thong. Vui long thu lai sau.",
            "request_id": getattr(request.state, "request_id", None),
        },
    )