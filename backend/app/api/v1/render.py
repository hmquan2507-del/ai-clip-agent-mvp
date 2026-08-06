from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.enums import QueueType
from app.db.session import get_db
from app.repositories.production_repository import ProductionRepository
from app.repositories.queue_repository import QueueRepository
from app.schemas.render_plan import RenderPlanResponse
from app.services.render_service import RenderService
from app.services.worker_service import WorkerService

from pydantic import BaseModel

class RenderJobCreateContract(BaseModel):
    production_id: str
    snapshot_id: str | None = None
    checksum: str | None = None

router = APIRouter(
    prefix="/render",
    tags=["Render"],
)


def _queue_and_run_render(
    db: Session,
    production_id: UUID,
) -> dict:
    production = ProductionRepository(db).get_by_id(production_id)

    if production is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production not found",
        )

    job = QueueRepository(db).create(
        production_id=production_id,
        queue_type=QueueType.RENDER_RUNTIME,
        payload=json.dumps({}),
    )

    # No background worker process exists in this app (single-operator,
    # local-first) - run inline so submitting a render actually renders.
    # WorkerService.run_job records the real outcome on the job row
    # itself (COMPLETED/FAILED + progress), which is what callers should
    # trust, not a status fabricated at submission time.
    job = WorkerService(db).run_job(job.id)

    return {
        "job_id": str(job.id),
        "production_id": str(production_id),
        "status": job.status,
        "progress": job.progress,
        "error_message": job.error_message,
    }


@router.post(
    "/jobs",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_render_job_contract(
    payload: RenderJobCreateContract,
    db: Session = Depends(get_db),
):
    return _queue_and_run_render(
        db, UUID(payload.production_id)
    )


@router.post(
    "/{production_id}",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_render_job(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    result = _queue_and_run_render(db, production_id)
    return {
        "message": (
            "Render completed."
            if result["status"] == "completed"
            else "Render failed."
        ),
        **result,
    }


@router.get(
    "/{production_id}",
    response_model=RenderPlanResponse,
)
def get_render_plan(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    return RenderService(db).get_latest_render_plan(production_id)


@router.delete(
    "/{production_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_render_plan(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    RenderService(db).delete_latest_render_plan(production_id)