from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class AuthLoginRequest(BaseModel):
    """Login with email or phone"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str = Field(min_length=8, max_length=128)


class AuthRegisterRequest(BaseModel):
    """Registration request"""
    email: EmailStr
    phone: str = Field(min_length=10, max_length=20)
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class AuthRefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=10)


class AuthTokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # seconds


class AuthUserResponse(BaseModel):
    """User info response"""
    id: str
    email: str
    phone: Optional[str] = None
    username: str
    full_name: str
    is_email_verified: bool = False
    is_phone_verified: bool = False
    account_type: str = "user"
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthLoginResponse(BaseModel):
    """Login response with user info"""
    user: AuthUserResponse
    tokens: AuthTokenPair


class AuthRegisterResponse(BaseModel):
    """Registration response"""
    message: str
    user: AuthUserResponse
    tokens: AuthTokenPair


class PasswordResetRequest(BaseModel):
    """Request password reset"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Confirm password reset with token"""
    token: str = Field(min_length=32)
    new_password: str = Field(min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    """Change password when logged in"""
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class RefreshTokenResponse(BaseModel):
    """Response when refreshing token"""
    tokens: AuthTokenPair
