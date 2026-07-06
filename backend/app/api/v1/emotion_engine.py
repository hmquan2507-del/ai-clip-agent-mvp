from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.emotion_engine_service import EmotionEngineService

router = APIRouter(
    prefix="/productions",
    tags=["Emotion Engine"],
)


@router.post("/{production_id}/emotion-engine/run")
def run_emotion_engine(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = EmotionEngineService(db)
    return service.run(production_id=production_id)