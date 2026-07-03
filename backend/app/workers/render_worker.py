from app.db.models.queue_job import QueueJob
from app.workers.base import BaseWorker


class RenderWorker(BaseWorker):
    def run(self, job: QueueJob) -> dict:
        return {
            "worker": "render",
            "job_id": str(job.id),
            "status": "completed",
            "message": "Render worker skeleton completed.",
        }