from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.enums import QueueType
from app.db.session import get_db
from app.repositories.production_repository import ProductionRepository
from app.repositories.queue_repository import QueueRepository
from app.schemas.content_graph import ContentGraphResponse
from app.services.content_understanding_service import (
    ContentUnderstandingService,
)

router = APIRouter(
    prefix="/content-understanding",
    tags=["Content Understanding"],
)


@router.post(
    "/{production_id}",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_content_graph(
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
        queue_type=QueueType.CONTENT_UNDERSTANDING,
        payload=json.dumps({}),
    )

    return {
        "message": "Content understanding queued.",
        "job_id": str(job.id),
        "status": job.status,
    }


@router.get(
    "/{production_id}",
    response_model=ContentGraphResponse,
)
def get_content_graph(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    return ContentUnderstandingService(
        db
    ).get_latest_content_graph(
        production_id,
    )


@router.delete(
    "/{production_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_content_graph(
    production_id: UUID,
    db: Session = Depends(get_db),
):
    ContentUnderstandingService(
        db
    ).delete_latest_content_graph(
        production_id,
    )