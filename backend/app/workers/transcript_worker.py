from app.db.models.queue_job import QueueJob
from app.workers.base import BaseWorker


class TranscriptWorker(BaseWorker):
    def run(self, job: QueueJob) -> dict:
        return {
            "worker": "transcript",
            "job_id": str(job.id),
            "status": "completed",
            "message": "Transcript worker skeleton completed.",
        }