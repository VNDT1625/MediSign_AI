"""FastAPI dependencies for authentication and authorization."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.database.base import get_db
from app.database.cloud_models import User

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate JWT token, return full User object."""
    token = credentials.credentials

    try:
        payload = decode_token(token, expected_type="access")
        user_id: str = payload["sub"]

        # Find user by ID
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "AUTH_USER_NOT_FOUND", "message": "Tai khoan khong ton tai"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "AUTH_ACCOUNT_INACTIVE", "message": "Tai khoan bi khoa"},
            )

        return user
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_INVALID_TOKEN", "message": "Token khong hop le"},
        ) from error


def get_optional_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(optional_security)
    ] = None,
    db: Session = Depends(get_db),
) -> User | None:
    """Same contract as `get_current_user` but returns ``None`` when no token is
    supplied instead of raising 401.

    Use this for endpoints that have a backwards-compatible anonymous path
    (e.g. the original single-shot ``POST /api/v1/ai/chat`` request shape) and
    a separate authenticated path (e.g. multi-turn diagnostic chat with a
    `conversation_id`). When credentials *are* supplied, they must still be
    valid — invalid tokens raise the same 401 errors as ``get_current_user``.
    """
    if credentials is None:
        return None

    token = credentials.credentials

    try:
        payload = decode_token(token, expected_type="access")
        user_id: str = payload["sub"]

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "AUTH_USER_NOT_FOUND",
                    "message": "Tai khoan khong ton tai",
                },
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "AUTH_ACCOUNT_INACTIVE",
                    "message": "Tai khoan bi khoa",
                },
            )

        return user
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_INVALID_TOKEN", "message": "Token khong hop le"},
        ) from error
