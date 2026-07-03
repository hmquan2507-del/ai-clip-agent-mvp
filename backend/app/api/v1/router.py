from fastapi import APIRouter

from app.api.v1.productions import router as productions_router
from app.api.v1.uploads import router as uploads_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(productions_router)
api_router.include_router(uploads_router)