from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.enums import QueueStatus, QueueType
from app.repositories.production_repository import ProductionRepository
from app.repositories.queue_repository import QueueRepository


class QueueService:

    def __init__(self, db: Session):
        self.production_repo = ProductionRepository(db)
        self.queue_repo = QueueRepository(db)

    def create_job(
        self,
        production_id: UUID,
        queue_type: QueueType,
        payload: str | None = None,
    ):
        production = self.production_repo.get_by_id(production_id)

        if production is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Production not found",
            )

        return self.queue_repo.create(
            production_id=production_id,
            queue_type=queue_type,
            payload=payload,
        )

    def get(self, queue_id: UUID):
        job = self.queue_repo.get_by_id(queue_id)

        if job is None:
            raise HTTPException(
                status_code=404,
                detail="Queue job not found",
            )

        return job

    def list(self, production_id: UUID):
        return self.queue_repo.list_by_production(production_id)

    def start(self, queue_id: UUID):
        job = self.get(queue_id)

        job.status = QueueStatus.RUNNING
        job.started_at = datetime.utcnow()

        return self.queue_repo.update(job)

    def complete(self, queue_id: UUID):
        job = self.get(queue_id)

        job.status = QueueStatus.COMPLETED
        job.progress = 100
        job.finished_at = datetime.utcnow()

        return self.queue_repo.update(job)

    def fail(
        self,
        queue_id: UUID,
        error: str,
    ):
        job = self.get(queue_id)

        job.status = QueueStatus.FAILED
        job.error_message = error
        job.finished_at = datetime.utcnow()

        return self.queue_repo.update(job)

    def retry(self, queue_id: UUID):
        job = self.get(queue_id)

        job.status = QueueStatus.PENDING
        job.progress = 0
        job.error_message = None
        job.started_at = None
        job.finished_at = None

        return self.queue_repo.update(job)