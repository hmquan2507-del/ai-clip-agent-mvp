from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.queue_job import QueueJob
from app.services.timeline_service import TimelineService
from app.workers.base import BaseWorker


class TimelineWorker(BaseWorker):
    def __init__(self, db: Session | None = None):
        self.db = db

    def run(self, job: QueueJob) -> dict:
        if self.db is None:
            return {
                "worker": "timeline",
                "job_id": str(job.id),
                "status": "skipped",
                "message": "Timeline worker requires database session.",
            }

        service = TimelineService(self.db)

        timeline = service.generate_timeline(
            production_id=job.production_id,
        )

        return {
            "worker": "timeline",
            "job_id": str(job.id),
            "status": "completed",
            "timeline_id": str(timeline.id),
            "production_id": str(job.production_id),
        }