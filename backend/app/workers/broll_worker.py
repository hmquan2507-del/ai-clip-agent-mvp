from app.db.models.queue_job import QueueJob
from app.workers.base import BaseWorker


class BrollWorker(BaseWorker):
    def run(self, job: QueueJob) -> dict:
        return {
            "worker": "broll",
            "job_id": str(job.id),
            "status": "completed",
            "message": "B-roll worker skeleton completed.",
        }