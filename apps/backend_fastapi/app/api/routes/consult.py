"""Consult / triage endpoints.

POST /consult/triage              — phân loại mức độ khẩn cấp (public)
GET  /consult/triage/history      — lịch sử triage của user (auth)
DELETE /consult/triage/{id}       — xoá một bản ghi triage (auth)
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_optional_current_user
from app.database.base import get_db
from app.database.cloud_models import TriageHistory, User
from app.schemas.triage import TriageRequest, TriageResponse
from app.services.triage_service import build_triage_result

router = APIRouter(prefix="/consult", tags=["consult"])


# ── Extra response schema ─────────────────────────────────────────────────────

class TriageHistoryItem(BaseModel):
    id: int
    session_id: str
    symptoms: str
    triage_level: Optional[str]
    advice: Optional[str]
    recommended_specialty: Optional[str]
    was_emergency: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TriageHistoryResponse(BaseModel):
    items: list[TriageHistoryItem]
    total: int
    page: int
    page_size: int
    has_next: bool


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/triage", response_model=TriageResponse)
def triage_consult(
    payload: TriageRequest,
    db: Session = Depends(get_db),
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
) -> TriageResponse:
    """Phân loại mức độ khẩn cấp từ mô tả triệu chứng.

    Public endpoint — không yêu cầu đăng nhập.
    Khi đã đăng nhập, kết quả được lưu vào triage_history.
    """
    result = build_triage_result(payload)

    # Lưu vào triage_history (dù có đăng nhập hay không)
    session_id = current_user.id if current_user else str(uuid.uuid4())
    advice_text = "; ".join(result.recommendations) if result.recommendations else None
    history_entry = TriageHistory(
        session_id=session_id,
        symptoms=payload.symptom_text[:2000],
        triage_level=result.urgency_level.upper() if result.urgency_level else None,
        advice=advice_text,
        was_emergency=(result.urgency_level == "emergency"),
    )
    try:
        db.add(history_entry)
        db.commit()
    except Exception:
        db.rollback()  # Non-fatal — still return the result

    return result


@router.get("/triage/history", response_model=TriageHistoryResponse)
def get_triage_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> TriageHistoryResponse:
    """Lịch sử các lần triage của user đăng nhập (mới nhất trước)."""
    q = db.query(TriageHistory).filter(
        TriageHistory.session_id == current_user.id
    )
    total = q.count()
    offset = (page - 1) * page_size
    items = q.order_by(TriageHistory.created_at.desc()).offset(offset).limit(page_size).all()

    return TriageHistoryResponse(
        items=[TriageHistoryItem.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(offset + page_size) < total,
    )


@router.delete("/triage/{triage_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_triage(
    triage_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> None:
    """Xoá một bản ghi triage của user."""
    entry = db.query(TriageHistory).filter(
        TriageHistory.id == triage_id,
        TriageHistory.session_id == current_user.id,
    ).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TRIAGE_NOT_FOUND", "message": "Không tìm thấy bản ghi triage"},
        )
    db.delete(entry)
    db.commit()
