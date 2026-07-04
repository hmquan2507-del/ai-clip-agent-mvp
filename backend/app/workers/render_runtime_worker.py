from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.queue_job import QueueJob
from app.services.render_service import RenderService
from app.workers.base_runtime_worker import BaseRuntimeWorker


class RenderRuntimeWorker(BaseRuntimeWorker):
    worker_name = "render_runtime"

    def __init__(self, db: Session | None = None):
        super().__init__(db=db)

    def run(self, job: QueueJob) -> dict:
        if self.db is None:
            return self.skipped_response(
                job,
                "Render worker requires database session.",
            )

        plan = RenderService(self.db).generate_render_plan(
            production_id=job.production_id,
        )

        return self.completed_response(
            job,
            render_plan_id=str(plan.id),
        )