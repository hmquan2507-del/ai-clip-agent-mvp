from __future__ import annotations

import asyncio
import json

from sqlalchemy.orm import Session

from app.db.models.queue_job import QueueJob
from app.services.editing_service import EditingService
from app.workers.base import BaseWorker


class EditingWorker(BaseWorker):
    def __init__(self, db: Session | None = None):
        self.db = db

    def run(self, job: QueueJob) -> dict:
        if self.db is None:
            return {
                "worker": "ai_editing",
                "job_id": str(job.id),
                "status": "skipped",
                "message": "Editing worker requires database session.",
            }

        payload = self._parse_payload(job.payload)

        provider = payload.get("provider", "mock")
        target_duration_seconds = payload.get("target_duration_seconds")

        service = EditingService(self.db)

        plan = asyncio.run(
            service.generate_editing_plan(
                production_id=job.production_id,
                provider=provider,
                target_duration_seconds=target_duration_seconds,
            )
        )

        return {
            "worker": "ai_editing",
            "job_id": str(job.id),
            "status": "completed",
            "editing_plan_id": str(plan.id),
            "production_id": str(job.production_id),
        }

    def _parse_payload(self, payload: str | None) -> dict:
        if not payload:
            return {}

        try:
            result = json.loads(payload)
        except Exception:
            return {}

        if not isinstance(result, dict):
            return {}

        return result