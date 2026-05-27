"""User profile endpoints.

GET  /profile          — đọc hồ sơ cá nhân + consent flag
PUT  /profile          — tạo hoặc cập nhật toàn bộ hồ sơ
PATCH /profile         — cập nhật từng trường (partial update)
DELETE /profile        — xoá hồ sơ (reset về trống)
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.database.cloud_models import User
from app.database.local_models import UserProfile

router = APIRouter(prefix="/profile", tags=["profile"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class ProfileResponse(BaseModel):
    id: str
    user_id: str
    name: Optional[str]
    yob: Optional[int]
    gender: Optional[str]
    medical_history: Optional[str]
    allergies: Optional[str]
    disability_type: Optional[str]
    preferred_communication: Optional[str]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    consent_personal_context: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProfileUpsertRequest(BaseModel):
    """Full upsert — all fields optional (omitted = unchanged)."""
    name: Optional[str] = Field(default=None, max_length=255)
    yob: Optional[int] = Field(default=None, ge=1900, le=2099)
    gender: Optional[str] = Field(default=None, pattern="^(male|female|other)$")
    medical_history: Optional[str] = Field(default=None, max_length=5000)
    allergies: Optional[str] = Field(default=None, max_length=2000)
    disability_type: Optional[str] = Field(
        default=None, pattern="^(DEAF|BLIND|ELDERLY|NONE)$"
    )
    preferred_communication: Optional[str] = Field(
        default=None, pattern="^(text|voice|sign)$"
    )
    emergency_contact_name: Optional[str] = Field(default=None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(default=None, max_length=20)
    consent_personal_context: Optional[bool] = None


def _get_or_create(db: Session, user_id: str) -> UserProfile:
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile is None:
        profile = UserProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
        )
        db.add(profile)
        db.flush()
    return profile


def _apply_fields(profile: UserProfile, data: ProfileUpsertRequest) -> None:
    field_map = {
        "name", "yob", "gender", "medical_history", "allergies",
        "disability_type", "preferred_communication",
        "emergency_contact_name", "emergency_contact_phone",
        "consent_personal_context",
    }
    for field in field_map:
        val = getattr(data, field, None)
        if val is not None:
            setattr(profile, field, val)
        elif field == "consent_personal_context" and data.consent_personal_context is not None:
            # Allow explicit False
            setattr(profile, field, data.consent_personal_context)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    """Đọc hồ sơ cá nhân. Trả 404 nếu chưa tạo."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROFILE_NOT_FOUND", "message": "Chưa có hồ sơ cá nhân"},
        )
    return ProfileResponse.model_validate(profile)


@router.put("", response_model=ProfileResponse, status_code=201)
def upsert_profile(
    payload: ProfileUpsertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    """Tạo mới hoặc ghi đè toàn bộ hồ sơ."""
    profile = _get_or_create(db, current_user.id)
    _apply_fields(profile, payload)
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    return ProfileResponse.model_validate(profile)


@router.patch("", response_model=ProfileResponse)
def patch_profile(
    payload: ProfileUpsertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    """Cập nhật từng trường hồ sơ (partial). Tạo mới nếu chưa có."""
    profile = _get_or_create(db, current_user.id)

    update_data = payload.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(profile, key, val)

    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    return ProfileResponse.model_validate(profile)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Xoá toàn bộ hồ sơ cá nhân (reset)."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if profile:
        db.delete(profile)
        db.commit()
