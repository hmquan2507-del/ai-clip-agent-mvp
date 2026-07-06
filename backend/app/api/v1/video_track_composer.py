from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.video_track_composer_service import VideoTrackComposerService

router = APIRouter(
    prefix="/productions",
    tags=["Video Track Composer"],
)


@router.post("/{production_id}/video-track/run")
def run_video_track_composer(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = VideoTrackComposerService(db)
    return service.run(production_id=production_id)