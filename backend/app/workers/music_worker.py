from app.db.models.queue_job import QueueJob
from app.workers.base import BaseWorker


class MusicWorker(BaseWorker):
    def run(self, job: QueueJob) -> dict:
        return {
            "worker": "music",
            "job_id": str(job.id),
            "status": "completed",
            "message": "Music worker skeleton completed.",
        }