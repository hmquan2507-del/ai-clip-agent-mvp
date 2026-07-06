from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.subtitle_track_composer_service import SubtitleTrackComposerService

router = APIRouter(
    prefix="/productions",
    tags=["Subtitle Track Composer"],
)


@router.post("/{production_id}/subtitle-track/run")
def run_subtitle_track_composer(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = SubtitleTrackComposerService(db)
    return service.run(production_id=production_id)