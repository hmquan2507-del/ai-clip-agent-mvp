from app.db.models.queue_job import QueueJob
from app.workers.base import BaseWorker


class SubtitleWorker(BaseWorker):
    def run(self, job: QueueJob) -> dict:
        return {
            "worker": "subtitle",
            "job_id": str(job.id),
            "status": "completed",
            "message": "Subtitle worker skeleton completed.",
        }