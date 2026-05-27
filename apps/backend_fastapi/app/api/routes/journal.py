"""Daily Journal (Soul Garden) endpoints.

GET  /journal                   — list user's journals (paginated)
GET  /journal/{id}              — get single entry
POST /journal                   — create new entry
PATCH /journal/{id}             — partial update
DELETE /journal/{id}            — hard delete
"""

from __future__ import annotations

import json
import uuid
from datetime import date as _date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.database.cloud_models import User
from app.database.local_models import DailyJournal

router = APIRouter(prefix="/journal", tags=["journal"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class JournalResponse(BaseModel):
    id: str
    user_id: str
    date: _date
    mood: Optional[int]
    content: Optional[str]
    tags: list[str]
    ai_analysis: Optional[str]
    tree_points: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_tags(cls, obj: DailyJournal) -> "JournalResponse":
        tags: list[str] = []
        if obj.tags:
            try:
                parsed = json.loads(obj.tags)
                if isinstance(parsed, list):
                    tags = [str(t) for t in parsed]
            except (json.JSONDecodeError, TypeError):
                tags = [obj.tags]  # fallback plain string
        return cls(
            id=obj.id,
            user_id=obj.user_id,
            date=obj.date,
            mood=obj.mood,
            content=obj.content,
            tags=tags,
            ai_analysis=obj.ai_analysis,
            tree_points=obj.tree_points,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


class JournalCreateRequest(BaseModel):
    date: _date = Field(default_factory=_date.today)
    mood: Optional[int] = Field(default=None, ge=1, le=5)
    content: Optional[str] = Field(default=None, max_length=10000)
    tags: list[str] = Field(default_factory=list)


class JournalPatchRequest(BaseModel):
    mood: Optional[int] = Field(default=None, ge=1, le=5)
    content: Optional[str] = Field(default=None, max_length=10000)
    tags: Optional[list[str]] = None


class JournalListResponse(BaseModel):
    items: list[JournalResponse]
    total: int
    page: int
    page_size: int
    has_next: bool


def _compute_tree_points(mood: Optional[int], content: Optional[str], tags: list[str]) -> int:
    """Tính điểm gamification đơn giản."""
    pts = 0
    if mood is not None:
        pts += 10
    if content and len(content.strip()) >= 20:
        pts += 20
    if tags:
        pts += min(len(tags), 3) * 5
    return pts


def _get_entry_or_404(db: Session, entry_id: str, user_id: str) -> DailyJournal:
    entry = db.query(DailyJournal).filter(
        DailyJournal.id == entry_id,
        DailyJournal.user_id == user_id,
    ).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "JOURNAL_NOT_FOUND", "message": "Không tìm thấy nhật ký"},
        )
    return entry


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=JournalListResponse)
def list_journals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    from_date: Optional[_date] = Query(default=None),
    to_date: Optional[_date] = Query(default=None),
) -> JournalListResponse:
    """Lấy danh sách nhật ký (mới nhất trước)."""
    q = db.query(DailyJournal).filter(DailyJournal.user_id == current_user.id)
    if from_date:
        q = q.filter(DailyJournal.date >= from_date)
    if to_date:
        q = q.filter(DailyJournal.date <= to_date)

    total = q.count()
    offset = (page - 1) * page_size
    entries = q.order_by(DailyJournal.date.desc()).offset(offset).limit(page_size).all()

    return JournalListResponse(
        items=[JournalResponse.from_orm_with_tags(e) for e in entries],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(offset + page_size) < total,
    )


@router.get("/{entry_id}", response_model=JournalResponse)
def get_journal(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JournalResponse:
    entry = _get_entry_or_404(db, entry_id, current_user.id)
    return JournalResponse.from_orm_with_tags(entry)


@router.post("", response_model=JournalResponse, status_code=201)
def create_journal(
    payload: JournalCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JournalResponse:
    """Tạo nhật ký mới. Nếu đã có entry cho ngày đó thì báo lỗi 409."""
    existing = db.query(DailyJournal).filter(
        DailyJournal.user_id == current_user.id,
        DailyJournal.date == payload.date,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "JOURNAL_ALREADY_EXISTS",
                "message": f"Đã có nhật ký ngày {payload.date}. Dùng PATCH để cập nhật.",
            },
        )

    points = _compute_tree_points(payload.mood, payload.content, payload.tags)
    entry = DailyJournal(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        date=payload.date,
        mood=payload.mood,
        content=payload.content,
        tags=json.dumps(payload.tags, ensure_ascii=False),
        tree_points=points,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return JournalResponse.from_orm_with_tags(entry)


@router.patch("/{entry_id}", response_model=JournalResponse)
def patch_journal(
    entry_id: str,
    payload: JournalPatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JournalResponse:
    entry = _get_entry_or_404(db, entry_id, current_user.id)
    update = payload.model_dump(exclude_unset=True)

    if "mood" in update:
        entry.mood = update["mood"]
    if "content" in update:
        entry.content = update["content"]
    if "tags" in update:
        entry.tags = json.dumps(update["tags"], ensure_ascii=False)

    entry.tree_points = _compute_tree_points(
        entry.mood,
        entry.content,
        json.loads(entry.tags) if entry.tags else [],
    )
    entry.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(entry)
    return JournalResponse.from_orm_with_tags(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journal(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    entry = _get_entry_or_404(db, entry_id, current_user.id)
    db.delete(entry)
    db.commit()
