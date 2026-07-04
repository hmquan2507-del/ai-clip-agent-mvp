from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from app.db.session import get_db
from app.schemas.editing_plan import EditingPlanResponse
from app.services.editing_service import EditingService
import json

from app.db.enums import QueueType
from app.repositories.production_repository import ProductionRepository
from app.repositories.queue_repository import QueueRepository

router = APIRouter(
    prefix="/editing",
    tags=["AI Editing"],
)


@router.post(
    "/{production_id}",
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_editing_job(
    production_id: UUID,
    provider: str | None = "mock",
    target_duration_seconds: int | None = None,
    db: Session = Depends(get_db),
):
    production_repo = ProductionRepository(db)
    production = production_repo.get_by_id(production_id)

    if production is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production not found",
        )

    queue_repo = QueueRepository(db)

    job = queue_repo.create(
        production_id=production_id,
        queue_type=QueueType.AI_EDITING,
        payload=json.dumps(
            {
                "provider": provider,
                "target_duration_seconds": target_duration_seconds,
            }
        ),
    )

    return {
        "message": "AI editing job created.",
        "job_id": str(job.id),
        "production_id": str(production_id),
        "type": job.type,
        "status": job.status,
    }
async def generate_editing_plan(
    production_id: UUID,
    provider: str | None = "mock",
    target_duration_seconds: int | None = None,
    db: Session = Depends(get_db),
):
    service = EditingService(db)

    return await service.generate_editing_plan(
        production_id=production_id,
        provider=provider,
        target_duration_seconds=target_duration_seconds,
    )


@router.get(
    "/{production_id}",
    response_model=EditingPlanResponse,
)
def get_editing_plan(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    service = EditingService(db)
    return service.get_latest_plan(production_id)


@router.delete(
    "/{production_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_editing_plan(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    service = EditingService(db)
    service.delete_latest_plan(production_id)
    return None