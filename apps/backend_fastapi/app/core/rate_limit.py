"""Rate-limit primitives based on slowapi.

slowapi is an optional dependency. When it is unavailable (or
``BACKEND_RATE_LIMIT_ENABLED=false``), this module exposes no-op decorators
so the application keeps working — useful for tests and offline dev.

Intended use::

    from app.core.rate_limit import limiter, rate_limit_login

    @router.post("/login")
    @rate_limit_login()
    def login_route(...):
        ...

Per-IP keying via ``get_remote_address`` is sufficient for v1; revisit when
deploying behind a CDN/L7 load balancer (``X-Forwarded-For``).
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from slowapi import Limiter
    from slowapi.errors import RateLimitExceeded
    from slowapi.util import get_remote_address

    _SLOWAPI_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised in environments without slowapi
    Limiter = None  # type: ignore[assignment]
    RateLimitExceeded = Exception  # type: ignore[assignment]
    get_remote_address = lambda request: "anonymous"  # type: ignore[assignment]
    _SLOWAPI_AVAILABLE = False
    logger.warning(
        "slowapi is not installed; rate limiting decorators will be no-ops. "
        "Install `slowapi` to enable per-IP throttling."
    )


def _make_noop_decorator() -> Callable[..., Callable[..., Any]]:
    def _decorator(*_args: Any, **_kwargs: Any) -> Callable[..., Any]:
        def _wrap(func: Callable[..., Any]) -> Callable[..., Any]:
            return func

        return _wrap

    return _decorator


if _SLOWAPI_AVAILABLE and settings.rate_limit_enabled:
    limiter = Limiter(key_func=get_remote_address, default_limits=[])
else:  # pragma: no cover - simple fallback
    class _NullLimiter:
        """Drop-in replacement matching the slowapi.Limiter interface used here."""

        def limit(self, *_args: Any, **_kwargs: Any):
            return _make_noop_decorator()()

        # Allow `app.state.limiter = limiter` even when slowapi is missing
        def __bool__(self) -> bool:  # pragma: no cover
            return False

    limiter = _NullLimiter()


def rate_limit_login() -> Callable[..., Any]:
    return limiter.limit(settings.rate_limit_login)


def rate_limit_forgot_password() -> Callable[..., Any]:
    return limiter.limit(settings.rate_limit_forgot_password)


def rate_limit_register() -> Callable[..., Any]:
    return limiter.limit(settings.rate_limit_register)


def rate_limit_ai_chat() -> Callable[..., Any]:
    return limiter.limit(settings.rate_limit_ai_chat)


__all__ = [
    "limiter",
    "RateLimitExceeded",
    "rate_limit_login",
    "rate_limit_forgot_password",
    "rate_limit_register",
    "rate_limit_ai_chat",
]
