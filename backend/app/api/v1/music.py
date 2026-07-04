from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.enums import MusicMood, QueueType
from app.db.session import get_db
from app.repositories.production_repository import ProductionRepository
from app.repositories.queue_repository import QueueRepository
from app.schemas.music import MusicPlanResponse
from app.services.music_service import MusicService

router = APIRouter(
    prefix="/music",
    tags=["Background Music"],
)


@router.post(
    "/{production_id}",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_music_job(
    production_id: UUID,
    mood: MusicMood = MusicMood.CUSTOM,
    db: Session = Depends(get_db),
):
    production = ProductionRepository(db).get_by_id(production_id)

    if production is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production not found",
        )

    job = QueueRepository(db).create(
        production_id=production_id,
        queue_type=QueueType.MUSIC_RUNTIME,
        payload=json.dumps(
            {
                "mood": mood.value,
            }
        ),
    )

    return {
        "message": "Music generation queued.",
        "job_id": str(job.id),
        "status": job.status,
    }


@router.get(
    "/{production_id}",
    response_model=MusicPlanResponse,
)
def get_music_plan(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    return MusicService(db).get_latest_music_plan(
        production_id,
    )


@router.delete(
    "/{production_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_music_plan(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    MusicService(db).delete_latest_music_plan(
        production_id,
    )