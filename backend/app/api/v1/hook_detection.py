from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.hook_detection_service import HookDetectionService

router = APIRouter(
    prefix="/productions",
    tags=["Hook Detection"],
)


@router.post("/{production_id}/hook-detection/run")
def run_hook_detection(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = HookDetectionService(db)
    return service.run(production_id=production_id)