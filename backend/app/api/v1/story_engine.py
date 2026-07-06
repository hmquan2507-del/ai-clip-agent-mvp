from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.story_engine_service import StoryEngineService

router = APIRouter(
    prefix="/productions",
    tags=["Story Engine"],
)


@router.post("/{production_id}/story-engine/run")
def run_story_engine(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = StoryEngineService(db)
    return service.run(production_id=production_id)