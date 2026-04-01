from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.consult import router as consult_router
from app.api.routes.health import router as health_router
from app.api.routes.medicine import router as medicine_router
from app.api.routes.admin import router as admin_router
from app.routers.drug_router import router as drug_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(consult_router)
api_router.include_router(medicine_router)
api_router.include_router(auth_router)
api_router.include_router(admin_router)
api_router.include_router(drug_router)
