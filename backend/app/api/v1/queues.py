from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.enums import QueueType
from app.db.session import get_db
from app.schemas.queue import QueueRead
from app.services.queue_service import QueueService

router = APIRouter(
    prefix="/queues",
    tags=["Queues"],
)


class QueueCreateRequest(BaseModel):
    production_id: UUID
    type: QueueType
    payload: str | None = None


def get_queue_service(db: Session = Depends(get_db)) -> QueueService:
    return QueueService(db)


@router.post(
    "",
    response_model=QueueRead,
)
def create_queue_job(
    payload: QueueCreateRequest,
    service: QueueService = Depends(get_queue_service),
):
    return service.create_job(
        production_id=payload.production_id,
        queue_type=payload.type,
        payload=payload.payload,
    )


@router.get(
    "/{queue_id}",
    response_model=QueueRead,
)
def get_queue_job(
    queue_id: UUID,
    service: QueueService = Depends(get_queue_service),
):
    return service.get(queue_id)


@router.get(
    "/production/{production_id}",
    response_model=list[QueueRead],
)
def list_queue_jobs_by_production(
    production_id: UUID,
    service: QueueService = Depends(get_queue_service),
):
    return service.list(production_id)