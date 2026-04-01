from datetime import datetime, timedelta
import secrets
import hashlib

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.database.cloud_models import User, UserSession
from app.schemas.auth import (
    AuthLoginRequest,
    AuthRefreshRequest,
    AuthTokenPair,
    AuthRegisterRequest,
    AuthLoginResponse,
    AuthRegisterResponse,
    AuthUserResponse,
    ChangePasswordRequest,
)
from app.services.auth_service import (
    login,
    refresh_tokens,
    register,
    logout,
    change_password,
)
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthRegisterResponse)
def register_route(payload: AuthRegisterRequest, request: Request, db: Session = Depends(get_db)):
    """Register new user account"""
    result = register(payload, db, request.client.host if request.client else None)
    return result


@router.post("/login", response_model=AuthLoginResponse)
def login_route(payload: AuthLoginRequest, request: Request, db: Session = Depends(get_db)):
    """Login with email or phone"""
    result = login(payload, db, request.client.host if request.client else None)
    return result


@router.post("/refresh", response_model=AuthTokenPair)
def refresh_route(payload: AuthRefreshRequest, db: Session = Depends(get_db)):
    """Refresh access token"""
    return refresh_tokens(payload.refresh_token, db)


@router.post("/logout")
def logout_route(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout current session"""
    return logout(current_user.id, db)


@router.post("/change-password")
def change_password_route(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change password when logged in"""
    return change_password(current_user.id, payload.current_password, payload.new_password, db)


@router.get("/me", response_model=AuthUserResponse)
def get_me_route(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user
