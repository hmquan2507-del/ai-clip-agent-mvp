from sqlalchemy.orm import Session

from app.db.models.queue_job import QueueJob
from app.services.transcript_service import TranscriptService
from app.workers.base import BaseWorker


class TranscriptWorker(BaseWorker):
    def __init__(self, db: Session | None = None):
        self.db = db

    def run(self, job: QueueJob) -> dict:
        if self.db is None:
            return {
                "worker": "transcript",
                "job_id": str(job.id),
                "status": "skipped",
                "message": "Transcript worker requires database session.",
            }

        service = TranscriptService(self.db)
        updated_job = service.transcribe_production(job)

        return {
            "worker": "transcript",
            "job_id": str(job.id),
            "status": "completed",
            "result": updated_job.result,
        }