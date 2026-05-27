"""Service layer for the personal medicine cabinet (my_medicines table)."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, date, time, timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.database.local_models import MyMedicine, DoseLog
from app.schemas.medicine import (
    CabinetItemCreate,
    CabinetItemResponse,
    CabinetItemUpdate,
    CabinetListResponse,
    DoseLogResponse,
    DoseHistoryResponse,
    DoseSlot,
    MedicineSchedule,
    TodayScheduleResponse,
    UpcomingResponse,
)


# Day code → ISO weekday number (Mon=1..Sun=7)
_DAY_TO_ISO = {
    "mon": 1, "tue": 2, "wed": 3, "thu": 4,
    "fri": 5, "sat": 6, "sun": 7,
}
_ISO_TO_DAY = {v: k for k, v in _DAY_TO_ISO.items()}

# Window for "overdue" — dose is overdue if scheduled_at < now - threshold and not taken
_OVERDUE_THRESHOLD = timedelta(minutes=30)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _parse_schedule(raw: Optional[str]) -> Optional[MedicineSchedule]:
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    try:
        return MedicineSchedule(**data)
    except Exception:
        return None


def _serialize_schedule(s: Optional[MedicineSchedule]) -> Optional[str]:
    if s is None:
        return None
    return json.dumps({"times": s.times, "days": s.days}, ensure_ascii=False)


def _model_to_response(row: MyMedicine) -> CabinetItemResponse:
    """Convert an ORM row to a CabinetItemResponse."""
    warnings: list[str] = []
    if row.warnings_json:
        try:
            parsed = json.loads(row.warnings_json)
            if isinstance(parsed, list):
                warnings = [str(w) for w in parsed]
        except (ValueError, TypeError):
            pass

    return CabinetItemResponse(
        id=row.id,
        name=row.name,
        dosage=row.dosage,
        risk_level=row.risk_level,
        warnings=warnings,
        guidance=row.guidance,
        remaining_pills=row.remaining_pills,
        doctor_notes=row.doctor_notes,
        is_active=row.is_active,
        start_date=row.start_date,
        end_date=row.end_date,
        schedule=_parse_schedule(row.schedule),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


# ---------------------------------------------------------------------------
# CRUD operations
# ---------------------------------------------------------------------------


def list_cabinet(user_id: str, db: Session) -> CabinetListResponse:
    """Return all active medicines in the user's cabinet (newest first)."""
    rows = (
        db.query(MyMedicine)
        .filter(MyMedicine.user_id == user_id, MyMedicine.is_active.is_(True))
        .order_by(MyMedicine.created_at.desc())
        .all()
    )
    return CabinetListResponse(
        items=[_model_to_response(r) for r in rows],
        total=len(rows),
    )


def add_to_cabinet(user_id: str, payload: CabinetItemCreate, db: Session) -> CabinetItemResponse:
    """Insert a new medicine into the user's cabinet."""
    row = MyMedicine(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name=payload.name,
        dosage=payload.dosage,
        risk_level=payload.risk_level,
        warnings_json=json.dumps(payload.warnings),
        guidance=payload.guidance,
        schedule=_serialize_schedule(payload.schedule),
        remaining_pills=payload.remaining_pills,
        doctor_notes=payload.doctor_notes,
        is_active=True,
        start_date=payload.start_date,
        end_date=payload.end_date,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _model_to_response(row)


def update_cabinet_item(
    item_id: str,
    user_id: str,
    payload: CabinetItemUpdate,
    db: Session,
) -> CabinetItemResponse:
    """Partially update a cabinet item owned by `user_id`."""
    row = _get_owned_item(item_id, user_id, db)

    if payload.dosage is not None:
        row.dosage = payload.dosage
    if payload.risk_level is not None:
        row.risk_level = payload.risk_level
    if payload.warnings is not None:
        row.warnings_json = json.dumps(payload.warnings)
    if payload.guidance is not None:
        row.guidance = payload.guidance
    if payload.remaining_pills is not None:
        row.remaining_pills = payload.remaining_pills
    if payload.doctor_notes is not None:
        row.doctor_notes = payload.doctor_notes
    if payload.is_active is not None:
        row.is_active = payload.is_active
    if payload.start_date is not None:
        row.start_date = payload.start_date
    if payload.end_date is not None:
        row.end_date = payload.end_date
    if payload.schedule is not None:
        row.schedule = _serialize_schedule(payload.schedule)

    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return _model_to_response(row)


def delete_cabinet_item(item_id: str, user_id: str, db: Session) -> None:
    """Hard-delete a cabinet item owned by `user_id`."""
    row = _get_owned_item(item_id, user_id, db)
    db.delete(row)
    db.commit()


def record_dose_taken(
    item_id: str,
    user_id: str,
    db: Session,
    scheduled_at: Optional[datetime] = None,
    note: Optional[str] = None,
) -> CabinetItemResponse:
    """Record that a dose was taken.

    - Decrements remaining_pills by 1 (clamps at 0)
    - Appends a row to dose_logs for history
    """
    row = _get_owned_item(item_id, user_id, db)
    if row.remaining_pills is not None and row.remaining_pills > 0:
        row.remaining_pills -= 1
    row.updated_at = datetime.utcnow()

    log = DoseLog(
        id=str(uuid.uuid4()),
        user_id=user_id,
        medicine_id=row.id,
        medicine_name=row.name,
        scheduled_at=scheduled_at,
        taken_at=datetime.utcnow(),
        note=note,
        created_at=datetime.utcnow(),
    )
    db.add(log)
    db.commit()
    db.refresh(row)
    return _model_to_response(row)


def get_dose_history(
    item_id: str,
    user_id: str,
    db: Session,
    limit: int = 50,
) -> DoseHistoryResponse:
    """Get dose history for a cabinet item."""
    # Verify ownership
    _get_owned_item(item_id, user_id, db)

    rows = (
        db.query(DoseLog)
        .filter(DoseLog.user_id == user_id, DoseLog.medicine_id == item_id)
        .order_by(DoseLog.taken_at.desc())
        .limit(limit)
        .all()
    )
    return DoseHistoryResponse(
        item_id=item_id,
        total=len(rows),
        logs=[
            DoseLogResponse(
                id=r.id,
                item_id=r.medicine_id,
                item_name=r.medicine_name,
                scheduled_at=r.scheduled_at,
                taken_at=r.taken_at,
                note=r.note,
            )
            for r in rows
        ],
    )


# ---------------------------------------------------------------------------
# Scheduling logic
# ---------------------------------------------------------------------------


def _expand_dose_slots_for_day(
    medicine: MyMedicine,
    target_date: date,
) -> list[datetime]:
    """Return list of scheduled datetimes for `medicine` on `target_date`.

    Returns [] if:
      - no schedule
      - target_date is outside [start_date, end_date]
      - target_date is not in schedule.days
    """
    sched = _parse_schedule(medicine.schedule)
    if sched is None or not sched.times:
        return []

    # Date window check
    if medicine.start_date and target_date < medicine.start_date:
        return []
    if medicine.end_date and target_date > medicine.end_date:
        return []

    # Day-of-week check
    if sched.days:
        day_code = _ISO_TO_DAY.get(target_date.isoweekday())
        if day_code not in sched.days:
            return []

    slots: list[datetime] = []
    for hhmm in sched.times:
        h, m = hhmm.split(":")
        slots.append(datetime.combine(target_date, time(int(h), int(m))))
    return sorted(slots)


def _logs_for_day(
    user_id: str,
    target_date: date,
    db: Session,
) -> dict[tuple[str, datetime], DoseLog]:
    """Index DoseLog by (medicine_id, scheduled_at) for fast lookup.

    Logs without scheduled_at are matched against the closest slot of the day
    (within ±2h) to avoid double-counting ad-hoc doses.
    """
    start = datetime.combine(target_date, time.min)
    end = datetime.combine(target_date, time.max)

    rows = (
        db.query(DoseLog)
        .filter(
            DoseLog.user_id == user_id,
            DoseLog.taken_at.between(start, end),
        )
        .all()
    )

    by_slot: dict[tuple[str, datetime], DoseLog] = {}
    ad_hoc: list[DoseLog] = []
    for r in rows:
        if r.scheduled_at is not None:
            by_slot[(r.medicine_id, r.scheduled_at)] = r
        else:
            ad_hoc.append(r)
    # ad_hoc logs: caller can match later if needed
    return by_slot


def get_today_schedule(user_id: str, db: Session, now: Optional[datetime] = None) -> TodayScheduleResponse:
    """Compute today's full schedule + which doses are taken."""
    now = now or datetime.utcnow()
    today = now.date()

    medicines = (
        db.query(MyMedicine)
        .filter(MyMedicine.user_id == user_id, MyMedicine.is_active.is_(True))
        .all()
    )
    logs = _logs_for_day(user_id, today, db)

    slots: list[DoseSlot] = []
    for med in medicines:
        for sched_dt in _expand_dose_slots_for_day(med, today):
            log = logs.get((med.id, sched_dt))
            taken = log is not None
            is_overdue = (not taken) and (sched_dt + _OVERDUE_THRESHOLD < now)
            slots.append(DoseSlot(
                item_id=med.id,
                name=med.name,
                dosage=med.dosage,
                scheduled_at=sched_dt,
                is_taken=taken,
                taken_at=(log.taken_at if log else None),
                is_overdue=is_overdue,
            ))

    slots.sort(key=lambda s: s.scheduled_at)

    taken_count = sum(1 for s in slots if s.is_taken)
    remaining = [s for s in slots if not s.is_taken]
    next_dose = remaining[0] if remaining else None

    return TodayScheduleResponse(
        date=today,
        total_doses=len(slots),
        taken_count=taken_count,
        remaining_count=len(remaining),
        next_dose=next_dose,
        slots=slots,
    )


def get_upcoming(
    user_id: str,
    db: Session,
    window_hours: int = 6,
    now: Optional[datetime] = None,
) -> UpcomingResponse:
    """List upcoming doses in the next `window_hours` (covers today + tomorrow)."""
    now = now or datetime.utcnow()
    horizon = now + timedelta(hours=window_hours)

    medicines = (
        db.query(MyMedicine)
        .filter(MyMedicine.user_id == user_id, MyMedicine.is_active.is_(True))
        .all()
    )

    # Window can span midnight, so check today + tomorrow
    days_to_check = [now.date()]
    if horizon.date() != now.date():
        days_to_check.append(horizon.date())

    logs = {}
    for d in days_to_check:
        logs.update(_logs_for_day(user_id, d, db))

    slots: list[DoseSlot] = []
    for med in medicines:
        for d in days_to_check:
            for sched_dt in _expand_dose_slots_for_day(med, d):
                if sched_dt < now or sched_dt > horizon:
                    continue
                log = logs.get((med.id, sched_dt))
                slots.append(DoseSlot(
                    item_id=med.id,
                    name=med.name,
                    dosage=med.dosage,
                    scheduled_at=sched_dt,
                    is_taken=log is not None,
                    taken_at=(log.taken_at if log else None),
                    is_overdue=False,
                ))

    slots.sort(key=lambda s: s.scheduled_at)

    return UpcomingResponse(
        window_hours=window_hours,
        slots=slots,
    )


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------


def _get_owned_item(item_id: str, user_id: str, db: Session) -> MyMedicine:
    row = (
        db.query(MyMedicine)
        .filter(MyMedicine.id == item_id, MyMedicine.user_id == user_id)
        .first()
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CABINET_ITEM_NOT_FOUND", "message": "Không tìm thấy thuốc trong tủ"},
        )
    return row
