from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.ffmpeg_runtime_service import FFmpegRuntimeService

router = APIRouter(
    prefix="/productions",
    tags=["FFmpeg Runtime"],
)


@router.post("/{production_id}/ffmpeg-command-plan/run")
def run_ffmpeg_command_plan(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = FFmpegRuntimeService(db)
    return service.run(production_id=production_id)