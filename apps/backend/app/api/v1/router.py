from fastapi import APIRouter

from app.api.v1.analises import router as analises_router
from app.api.v1.health import router as health_router

api_router = APIRouter()
api_router.include_router(analises_router)
api_router.include_router(health_router)
