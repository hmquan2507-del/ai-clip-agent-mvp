from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.enums import QueueType
from app.db.session import get_db
from app.repositories.production_repository import ProductionRepository
from app.repositories.queue_repository import QueueRepository
from app.schemas.sound_effect import SoundEffectPlanResponse
from app.services.sound_effect_service import SoundEffectService


router = APIRouter(
    prefix="/sound-effects",
    tags=["Sound Effects"],
)


@router.post(
    "/{production_id}",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_sound_effect_job(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    production = ProductionRepository(db).get_by_id(production_id)

    if production is None:
        raise HTTPException(
            status_code=404,
            detail="Production not found",
        )

    job = QueueRepository(db).create(
        production_id=production_id,
        queue_type=QueueType.SOUND_EFFECT_RUNTIME,
        payload=json.dumps({}),
    )

    return {
        "message": "Sound effect generation queued.",
        "job_id": str(job.id),
        "status": job.status,
    }


@router.get(
    "/{production_id}",
    response_model=SoundEffectPlanResponse,
)
def get_sound_effect_plan(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    return SoundEffectService(db).get_latest_sound_effect_plan(
        production_id,
    )


@router.delete(
    "/{production_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_sound_effect_plan(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    SoundEffectService(db).delete_latest_sound_effect_plan(
        production_id,
    )