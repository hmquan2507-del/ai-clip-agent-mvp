from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.enums import QueueType, SubtitleStyle
from app.db.session import get_db
from app.repositories.production_repository import ProductionRepository
from app.repositories.queue_repository import QueueRepository
from app.schemas.subtitle import SubtitleResponse
from app.services.subtitle_service import SubtitleService


router = APIRouter(
    prefix="/subtitle",
    tags=["Subtitle"],
)


@router.post(
    "/{production_id}",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_subtitle_job(
    production_id: UUID,
    style: SubtitleStyle = SubtitleStyle.DEFAULT,
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
        queue_type=QueueType.SUBTITLE_RUNTIME,
        payload=json.dumps({"style": style.value}),
    )

    return {
        "message": "Subtitle generation queued.",
        "job_id": str(job.id),
        "production_id": str(production_id),
        "type": job.type,
        "status": job.status,
    }


@router.get(
    "/{production_id}",
    response_model=SubtitleResponse,
)
def get_subtitle(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    return SubtitleService(db).get_latest_subtitle(production_id)


@router.delete(
    "/{production_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_subtitle(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    SubtitleService(db).delete_latest_subtitle(production_id)