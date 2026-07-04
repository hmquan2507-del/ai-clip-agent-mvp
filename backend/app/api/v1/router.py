from fastapi import APIRouter

from app.api.v1.assets import router as assets_router
from app.api.v1.productions import router as productions_router
from app.api.v1.uploads import router as uploads_router
from app.api.v1.queues import router as queues_router
from app.api.v1.workers import router as workers_router
from app.api.v1.editing import router as editing_router
from app.api.v1.subtitle import router as subtitle_router
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(productions_router)
api_router.include_router(uploads_router)
api_router.include_router(assets_router)
api_router.include_router(queues_router)
api_router.include_router(workers_router)
api_router.include_router(editing_router)
api_router.include_router(subtitle_router)