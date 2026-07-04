from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.db.models.queue_job import QueueJob
from app.workers.base import BaseWorker


class BaseRuntimeWorker(BaseWorker):
    worker_name = "runtime"

    def __init__(self, db: Session | None = None):
        self.db = db

    def require_db(self) -> Session | None:
        return self.db

    def parse_payload(self, payload: str | None) -> dict:
        if not payload:
            return {}

        try:
            result = json.loads(payload)
        except Exception:
            return {}

        if not isinstance(result, dict):
            return {}

        return result

    def skipped_response(self, job: QueueJob, message: str) -> dict:
        return {
            "worker": self.worker_name,
            "job_id": str(job.id),
            "status": "skipped",
            "message": message,
        }

    def completed_response(
        self,
        job: QueueJob,
        **extra,
    ) -> dict:
        return {
            "worker": self.worker_name,
            "job_id": str(job.id),
            "status": "completed",
            "production_id": str(job.production_id),
            **extra,
        }