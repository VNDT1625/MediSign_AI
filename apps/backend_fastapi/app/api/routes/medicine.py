from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.database.cloud_models import User
from app.schemas.medicine import (
    CabinetItemCreate,
    CabinetItemResponse,
    CabinetItemUpdate,
    CabinetListResponse,
    DoseHistoryResponse,
    MedicineImageScanResponse,
    MedicineScanRequest,
    MedicineScanResponse,
    TakeDoseRequest,
    TodayScheduleResponse,
    UpcomingResponse,
)
from app.services.cabinet_service import (
    add_to_cabinet,
    delete_cabinet_item,
    get_dose_history,
    get_today_schedule,
    get_upcoming,
    list_cabinet,
    record_dose_taken,
    update_cabinet_item,
)
from app.services.medicine_service import scan_medicine
from app.services.medicine_vision_service import scan_medicine_from_image

router = APIRouter(prefix="/medicine", tags=["medicine"])


# ---------------------------------------------------------------------------
# Scan endpoints
# ---------------------------------------------------------------------------


@router.post("/scan", response_model=MedicineScanResponse)
def medicine_scan(payload: MedicineScanRequest) -> MedicineScanResponse:
    """Text-based drug scan — OCR text input."""
    return scan_medicine(payload)


@router.post("/scan-image", response_model=MedicineImageScanResponse)
async def medicine_scan_image(
    file: UploadFile = File(..., description="Ảnh nhãn thuốc (JPEG/PNG, tối đa 10 MB)"),
    current_medications: str = Form(
        default="[]",
        description="JSON array tên thuốc đang dùng, ví dụ: [\"Aspirin\", \"Ibuprofen\"]",
    ),
) -> MedicineImageScanResponse:
    """Image-based drug scan — upload ảnh nhãn thuốc, MedGemma 4B đọc tên.

    Multipart/form-data:
      - file: ảnh nhãn thuốc (JPEG hoặc PNG, ≤ 10 MB)
      - current_medications: JSON string danh sách thuốc đang dùng (tuỳ chọn)

    Luồng:
      Ảnh → MedGemma 4B vision → tên thuốc → drug database lookup → cảnh báo tương tác
    """
    import json

    # Parse current_medications JSON string
    try:
        meds: list[str] = json.loads(current_medications)
        if not isinstance(meds, list):
            meds = []
    except (json.JSONDecodeError, ValueError):
        meds = []

    image_bytes = await file.read()
    return await scan_medicine_from_image(
        image_bytes=image_bytes,
        content_type=file.content_type,
        current_medications=meds,
    )


# ---------------------------------------------------------------------------
# Cabinet CRUD (authentication required)
# ---------------------------------------------------------------------------


@router.get("/cabinet", response_model=CabinetListResponse)
def get_cabinet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CabinetListResponse:
    """Retrieve all active medicines in the authenticated user's cabinet."""
    return list_cabinet(current_user.id, db)


@router.post("/cabinet", response_model=CabinetItemResponse, status_code=201)
def add_cabinet_item(
    payload: CabinetItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CabinetItemResponse:
    """Add a medicine to the authenticated user's cabinet."""
    return add_to_cabinet(current_user.id, payload, db)


@router.patch("/cabinet/{item_id}", response_model=CabinetItemResponse)
def update_item(
    item_id: str,
    payload: CabinetItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CabinetItemResponse:
    """Partially update a cabinet item (dosage, remaining_pills, notes, etc.)."""
    return update_cabinet_item(item_id, current_user.id, payload, db)


@router.delete("/cabinet/{item_id}", status_code=204)
def delete_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Remove a medicine from the cabinet."""
    delete_cabinet_item(item_id, current_user.id, db)


@router.post("/cabinet/{item_id}/dose", response_model=CabinetItemResponse)
def take_dose(
    item_id: str,
    payload: TakeDoseRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CabinetItemResponse:
    """Record that a dose of this medicine was taken.

    - Decrements remaining_pills
    - Appends an entry to dose_logs (history + adherence tracking)
    - Optional body: scheduled_at (which scheduled slot was taken) + note
    """
    return record_dose_taken(
        item_id,
        current_user.id,
        db,
        scheduled_at=payload.scheduled_at if payload else None,
        note=payload.note if payload else None,
    )


# ---------------------------------------------------------------------------
# Schedule / Reminder endpoints
# ---------------------------------------------------------------------------


@router.get("/cabinet/today", response_model=TodayScheduleResponse)
def get_today(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TodayScheduleResponse:
    """Today's full medication schedule.

    Returns:
      - total_doses: tổng số lần uống lập lịch hôm nay
      - taken_count: đã uống
      - remaining_count: còn phải uống
      - next_dose: liều kế tiếp cần uống (null nếu hôm nay xong)
      - slots: list đầy đủ các lệnh uống trong ngày + trạng thái taken/overdue
    """
    return get_today_schedule(current_user.id, db)


@router.get("/cabinet/upcoming", response_model=UpcomingResponse)
def get_cabinet_upcoming(
    hours: int = Query(default=6, ge=1, le=48,
                       description="Cửa sổ thời gian (giờ) — default 6"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UpcomingResponse:
    """Liều thuốc trong N giờ tới (cho push notification scheduler).

    Mobile/web có thể poll endpoint này định kỳ (e.g. mỗi 1h) hoặc dùng kết quả
    để schedule local notification. Server không tự push — đây là pull-based.
    """
    return get_upcoming(current_user.id, db, window_hours=hours)


@router.get("/cabinet/{item_id}/history", response_model=DoseHistoryResponse)
def get_cabinet_history(
    item_id: str,
    limit: int = Query(default=50, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DoseHistoryResponse:
    """Lịch sử uống thuốc của một item — dùng cho dashboard adherence."""
    return get_dose_history(item_id, current_user.id, db, limit=limit)
