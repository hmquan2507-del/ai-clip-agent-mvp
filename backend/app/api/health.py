from fastapi import APIRouter

from app.core.config import settings
from app.db.session import engine
from app.storage.factory import get_storage_provider

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "environment": settings.environment,
        "version": settings.app_version,
    }


@router.get("/storage")
def storage_health():
    storage = get_storage_provider()

    return {
        "status": "healthy",
        "provider": storage.__class__.__name__,
        "storage_provider": settings.storage_provider,
    }


@router.get("/ready")
def ready():
    database_ready = True

    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
    except Exception:
        database_ready = False

    storage = get_storage_provider()

    return {
        "status": "ready" if database_ready else "not_ready",
        "database": "ready" if database_ready else "not_ready",
        "storage": storage.__class__.__name__,
    }