import json
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.enums import QueueStatus
from app.repositories.queue_repository import QueueRepository
from app.workers.dispatcher import WorkerDispatcher


class WorkerService:
    def __init__(self, db: Session):
        self.queue_repository = QueueRepository(db)
        self.dispatcher = WorkerDispatcher()

    def run_job(self, queue_id: UUID):
        job = self.queue_repository.get_by_id(queue_id)

        if job is None:
            raise HTTPException(status_code=404, detail="Queue job not found")

        job.status = QueueStatus.RUNNING
        job.started_at = datetime.utcnow()
        job.progress = 10
        self.queue_repository.update(job)

        try:
            result = self.dispatcher.dispatch(job)

            job.status = QueueStatus.COMPLETED
            job.progress = 100
            job.result = json.dumps(result, ensure_ascii=False)
            job.finished_at = datetime.utcnow()

            return self.queue_repository.update(job)

        except Exception as error:
            job.status = QueueStatus.FAILED
            job.error_message = str(error)
            job.finished_at = datetime.utcnow()

            return self.queue_repository.update(job)