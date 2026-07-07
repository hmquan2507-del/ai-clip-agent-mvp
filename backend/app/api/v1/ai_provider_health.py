from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.services.ai_provider_health_service import AIProviderHealthService

router = APIRouter(
    prefix="/ai",
    tags=["AI Provider Health"],
)


@router.get("/providers/health")
def get_ai_provider_health() -> dict[str, Any]:
    service = AIProviderHealthService()
    return service.run()