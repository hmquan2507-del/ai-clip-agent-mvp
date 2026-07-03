from fastapi import APIRouter

from app.storage.factory import get_storage_provider

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health():
    storage = get_storage_provider()

    return {
        "status": "healthy",
        "storage": storage.__class__.__name__,
    }


@router.get("/storage")
def storage_health():
    storage = get_storage_provider()

    return {
        "status": "healthy",
        "provider": storage.__class__.__name__,
    }


@router.get("/ready")
def ready():
    return {
        "status": "ready",
    }