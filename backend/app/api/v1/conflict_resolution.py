from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.conflict_resolution_service import ConflictResolutionService

router = APIRouter(
    prefix="/productions",
    tags=["Conflict Resolution"],
)


@router.post("/{production_id}/conflict-resolution/run")
def run_conflict_resolution(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = ConflictResolutionService(db)
    return service.run(production_id=production_id)