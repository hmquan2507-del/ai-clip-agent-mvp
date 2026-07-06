from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.ai_engine_runtime_service import AIEngineRuntimeService

router = APIRouter(
    prefix="/productions",
    tags=["AI Brain"],
)


@router.post("/{production_id}/ai-brain/run")
def run_ai_brain(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = AIEngineRuntimeService(db)

    return service.run_pipeline(
        production_id=production_id,
        engine_keys=[
            "hook_detection",
            "story_engine",
            "emotion_engine",
            "editing_style_engine",
            "decision_engine",
            "editing_execution_planner",
        ],
    )