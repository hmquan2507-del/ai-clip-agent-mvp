from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.enums import QueueType
from app.db.session import get_db
from app.repositories.production_repository import ProductionRepository
from app.repositories.queue_repository import QueueRepository
from app.services.timeline_service import TimelineService

router = APIRouter(
    prefix="/timeline",
    tags=["Timeline"],
)

@router.post(
    "/{production_id}",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_timeline_job(
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
        queue_type=QueueType.TIMELINE,
        payload=json.dumps({}),
    )

    return {
        "message": "Timeline generation queued.",
        "job_id": str(job.id),
        "status": job.status,
    }
@router.get("/{production_id}")
def get_timeline(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    service = TimelineService(db)
    return service.get_latest_timeline(production_id)

@router.delete(
    "/{production_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_timeline(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    TimelineService(db).delete_latest_timeline(production_id)



@router.post(
    "/{production_id}",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_timeline_job(
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
        queue_type=QueueType.TIMELINE,
        payload=json.dumps({}),
    )

    return {
        "message": "Timeline generation queued.",
        "job_id": str(job.id),
        "status": job.status,
    }
@router.get("/{production_id}")
def get_timeline(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    service = TimelineService(db)
    return service.get_latest_timeline(production_id)

@router.delete(
    "/{production_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_timeline(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    TimelineService(db).delete_latest_timeline(production_id)

