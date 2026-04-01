from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.schemas.triage import TriageRequest, TriageResponse
from app.services.triage_service import build_triage_result

router = APIRouter(prefix="/consult", tags=["consult"])


@router.post("/triage", response_model=TriageResponse)
def triage_consult(payload: TriageRequest) -> TriageResponse:
    return build_triage_result(payload)


@router.get("/triage/history", response_model=list[TriageResponse])
def get_triage_history(
    current_user: Annotated[str, Depends(get_current_user)],
) -> list[TriageResponse]:
    """Get triage history for authenticated user (protected endpoint demo)."""
    # TODO: Implement actual database query
    # For now, return empty list as demo
    return []
