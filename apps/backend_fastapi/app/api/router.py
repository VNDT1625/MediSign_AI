from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.consult import router as consult_router
from app.api.routes.health import router as health_router
from app.api.routes.medicine import router as medicine_router
from app.api.routes.admin import router as admin_router
from app.api.routes.ai import router as ai_router
from app.api.routes.conversations import router as conversations_router
from app.api.routes.summary import router as summary_router
from app.api.routes.profile import router as profile_router
from app.api.routes.journal import router as journal_router
from app.routers.drug_router import router as drug_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(profile_router)
api_router.include_router(journal_router)
api_router.include_router(consult_router)
api_router.include_router(medicine_router)
api_router.include_router(ai_router)
api_router.include_router(conversations_router)
api_router.include_router(summary_router)
api_router.include_router(admin_router)
api_router.include_router(drug_router)
