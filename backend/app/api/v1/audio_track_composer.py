from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.audio_track_composer_service import AudioTrackComposerService

router = APIRouter(
    prefix="/productions",
    tags=["Audio Track Composer"],
)


@router.post("/{production_id}/audio-track/run")
def run_audio_track_composer(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = AudioTrackComposerService(db)
    return service.run(production_id=production_id)