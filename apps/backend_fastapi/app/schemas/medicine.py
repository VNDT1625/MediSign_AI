from __future__ import annotations

from datetime import date, datetime, time
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Scan endpoint
# ---------------------------------------------------------------------------

class MedicineScanRequest(BaseModel):
    extracted_text: str = Field(min_length=2, max_length=500)
    current_medications: list[str] = Field(default_factory=list)


class MedicineScanResponse(BaseModel):
    normalized_name: str
    risk_level: str
    warnings: list[str]
    guidance: str


# ---------------------------------------------------------------------------
# Cabinet CRUD
# ---------------------------------------------------------------------------

# Day-of-week codes (ISO: Mon=1..Sun=7)
DayCode = Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

_VALID_DAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
_TIME_RE = r"^([01]?\d|2[0-3]):[0-5]\d$"


class MedicineSchedule(BaseModel):
    """Schedule for taking a medicine.

    times: list of HH:MM strings (24h), e.g. ["08:00", "20:00"]
    days:  list of day codes; empty/None = every day
    """
    times: list[str] = Field(default_factory=list)
    days: Optional[list[DayCode]] = Field(default=None)

    @field_validator("times")
    @classmethod
    def validate_times(cls, v: list[str]) -> list[str]:
        import re
        out: list[str] = []
        for t in v:
            t = t.strip()
            if not re.match(_TIME_RE, t):
                raise ValueError(f"time must be HH:MM (got {t!r})")
            # normalize "8:00" → "08:00"
            h, m = t.split(":")
            out.append(f"{int(h):02d}:{int(m):02d}")
        # dedup + sort
        return sorted(set(out))

    @field_validator("days")
    @classmethod
    def validate_days(cls, v: Optional[list[str]]) -> Optional[list[DayCode]]:
        if v is None:
            return None
        out: list[DayCode] = []
        for d in v:
            d = d.strip().lower()
            if d not in _VALID_DAYS:
                raise ValueError(f"day must be mon/tue/wed/thu/fri/sat/sun (got {d!r})")
            out.append(d)  # type: ignore[arg-type]
        return out or None  # empty list = all days


class CabinetItemCreate(BaseModel):
    """Body for POST /medicine/cabinet — add a new medicine."""
    name: str = Field(min_length=1, max_length=255)
    dosage: Optional[str] = Field(default=None, max_length=50)
    risk_level: Optional[str] = Field(default=None, max_length=20)
    warnings: list[str] = Field(default_factory=list)
    guidance: Optional[str] = Field(default=None)
    remaining_pills: Optional[int] = Field(default=None, ge=0)
    doctor_notes: Optional[str] = Field(default=None)
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    schedule: Optional[MedicineSchedule] = Field(default=None)


class CabinetItemUpdate(BaseModel):
    """Body for PATCH /medicine/cabinet/{id} — partial update."""
    dosage: Optional[str] = Field(default=None, max_length=50)
    risk_level: Optional[str] = Field(default=None, max_length=20)
    warnings: Optional[list[str]] = Field(default=None)
    guidance: Optional[str] = Field(default=None)
    remaining_pills: Optional[int] = Field(default=None, ge=0)
    doctor_notes: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    schedule: Optional[MedicineSchedule] = Field(default=None)


class CabinetItemResponse(BaseModel):
    """Full cabinet item returned by all cabinet endpoints."""
    id: str
    name: str
    dosage: Optional[str]
    risk_level: Optional[str]
    warnings: list[str]
    guidance: Optional[str]
    remaining_pills: Optional[int]
    doctor_notes: Optional[str]
    is_active: bool
    start_date: Optional[date]
    end_date: Optional[date]
    schedule: Optional[MedicineSchedule] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CabinetListResponse(BaseModel):
    items: list[CabinetItemResponse]
    total: int


# ---------------------------------------------------------------------------
# Schedule / Reminder schemas
# ---------------------------------------------------------------------------


class DoseSlot(BaseModel):
    """A scheduled dose at a specific datetime."""
    item_id: str
    name: str
    dosage: Optional[str] = None
    scheduled_at: datetime          # giờ uống dự kiến
    is_taken: bool = False          # đã uống chưa
    taken_at: Optional[datetime] = None
    is_overdue: bool = False        # quá giờ chưa uống


class TodayScheduleResponse(BaseModel):
    """GET /medicine/cabinet/today response."""
    date: date
    total_doses: int                # tổng số lệnh uống hôm nay
    taken_count: int                # đã uống
    remaining_count: int            # còn phải uống
    next_dose: Optional[DoseSlot] = None  # liều kế tiếp
    slots: list[DoseSlot]           # full lịch trong ngày


class UpcomingResponse(BaseModel):
    """GET /medicine/cabinet/upcoming response."""
    window_hours: int                # cửa sổ thời gian (e.g., 6h)
    slots: list[DoseSlot]


class DoseLogResponse(BaseModel):
    """A historical dose log entry."""
    id: str
    item_id: str
    item_name: str
    scheduled_at: Optional[datetime]
    taken_at: datetime
    note: Optional[str] = None


class DoseHistoryResponse(BaseModel):
    """GET /medicine/cabinet/{id}/history response."""
    item_id: str
    total: int
    logs: list[DoseLogResponse]


class TakeDoseRequest(BaseModel):
    """Optional body for POST /medicine/cabinet/{id}/dose."""
    scheduled_at: Optional[datetime] = None  # which scheduled slot was taken
    note: Optional[str] = Field(default=None, max_length=500)


# ---------------------------------------------------------------------------
# Image scan (MedGemma 4B vision)
# ---------------------------------------------------------------------------

class MedicineImageScanResponse(BaseModel):
    """Response from POST /medicine/scan-image endpoint."""

    # ── What MedGemma read from the image ─────────────────────────────────
    extracted_drug_name: Optional[str] = None
    extracted_dosage: Optional[str] = None
    extracted_manufacturer: Optional[str] = None
    raw_ocr_text: Optional[str] = None

    # ── Drug database lookup result ────────────────────────────────────────
    drug_lookup_status: str  # "found" | "suggestions" | "not_found" | "unknown"
    drug_info: Optional[dict] = None          # Full drug record if found
    suggestions: list[dict] = Field(default_factory=list)  # Similar drugs

    # ── Interaction warnings (reuses scan_medicine rule engine) ───────────
    normalized_name: str
    risk_level: str       # "low" | "medium" | "high" | "unknown"
    warnings: list[str] = Field(default_factory=list)
    guidance: str

    # ── Meta ───────────────────────────────────────────────────────────────
    model_used: str
    fallback_used: bool = False  # True when MedGemma was unavailable
