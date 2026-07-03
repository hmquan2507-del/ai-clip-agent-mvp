from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.queue import QueueRead
from app.services.worker_service import WorkerService

router = APIRouter(
    prefix="/workers",
    tags=["Workers"],
)


def get_worker_service(db: Session = Depends(get_db)) -> WorkerService:
    return WorkerService(db)


@router.post(
    "/run/{queue_id}",
    response_model=QueueRead,
)
def run_queue_job(
    queue_id: UUID,
    service: WorkerService = Depends(get_worker_service),
):
    return service.run_job(queue_id)