from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.track_context_service import TrackContextService

router = APIRouter(
    prefix="/productions",
    tags=["Track Context"],
)


@router.post("/{production_id}/track-context/run")
def run_track_context(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = TrackContextService(db)
    return service.run(production_id=production_id)