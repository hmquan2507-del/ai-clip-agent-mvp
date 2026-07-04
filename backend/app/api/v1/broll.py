from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.enums import QueueType
from app.db.session import get_db
from app.repositories.production_repository import ProductionRepository
from app.repositories.queue_repository import QueueRepository
from app.schemas.broll import BrollPlanResponse
from app.services.broll_service import BrollService


router = APIRouter(
    prefix="/broll",
    tags=["B-roll"],
)


@router.post(
    "/{production_id}",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_broll_job(
    production_id: UUID,
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
        queue_type=QueueType.BROLL_RUNTIME,
        payload=json.dumps({}),
    )

    return {
        "message": "B-roll generation queued.",
        "job_id": str(job.id),
        "production_id": str(production_id),
        "type": job.type,
        "status": job.status,
    }


@router.get(
    "/{production_id}",
    response_model=BrollPlanResponse,
)
def get_broll_plan(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    return BrollService(db).get_latest_broll_plan(production_id)


@router.delete(
    "/{production_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_broll_plan(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    BrollService(db).delete_latest_broll_plan(production_id)