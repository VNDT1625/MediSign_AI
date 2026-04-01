from fastapi import APIRouter

from app.schemas.medicine import MedicineScanRequest, MedicineScanResponse
from app.services.medicine_service import scan_medicine

router = APIRouter(prefix="/medicine", tags=["medicine"])


@router.post("/scan", response_model=MedicineScanResponse)
def medicine_scan(payload: MedicineScanRequest) -> MedicineScanResponse:
    return scan_medicine(payload)
