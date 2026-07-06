from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.timeline_composer_service import TimelineComposerService

router = APIRouter(
    prefix="/productions",
    tags=["Timeline Composer"],
)


@router.post("/{production_id}/timeline-composer/run")
def run_timeline_composer(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = TimelineComposerService(db)
    return service.run(production_id=production_id)