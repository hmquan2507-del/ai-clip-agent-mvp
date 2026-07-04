from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.queue_job import QueueJob
from app.services.broll_service import BrollService
from app.workers.base_runtime_worker import BaseRuntimeWorker


class BrollRuntimeWorker(BaseRuntimeWorker):
    worker_name = "broll_runtime"

    def __init__(self, db: Session | None = None):
        super().__init__(db=db)

    def run(self, job: QueueJob) -> dict:
        if self.db is None:
            return self.skipped_response(
                job,
                "B-roll worker requires database session.",
            )

        service = BrollService(self.db)

        plan = service.generate_broll_plan(
            production_id=job.production_id,
        )

        return self.completed_response(
            job,
            broll_plan_id=str(plan.id),
        )