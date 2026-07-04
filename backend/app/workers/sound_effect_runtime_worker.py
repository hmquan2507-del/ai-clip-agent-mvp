from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.queue_job import QueueJob
from app.services.sound_effect_service import SoundEffectService
from app.workers.base_runtime_worker import BaseRuntimeWorker


class SoundEffectRuntimeWorker(BaseRuntimeWorker):
    worker_name = "sound_effect_runtime"

    def __init__(self, db: Session | None = None):
        super().__init__(db=db)

    def run(self, job: QueueJob) -> dict:
        if self.db is None:
            return self.skipped_response(
                job,
                "Sound Effect worker requires database session.",
            )

        service = SoundEffectService(self.db)

        plan = service.generate_sound_effect_plan(
            production_id=job.production_id,
        )

        return self.completed_response(
            job,
            sound_effect_plan_id=str(plan.id),
        )