from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.enums import MusicMood
from app.db.models.queue_job import QueueJob
from app.services.music_service import MusicService
from app.workers.base_runtime_worker import BaseRuntimeWorker


class MusicRuntimeWorker(BaseRuntimeWorker):
    worker_name = "music_runtime"

    def __init__(self, db: Session | None = None):
        super().__init__(db=db)

    def run(self, job: QueueJob) -> dict:
        if self.db is None:
            return self.skipped_response(
                job,
                "Music worker requires database session.",
            )

        payload = self.parse_payload(job.payload)

        mood = MusicMood(
            payload.get(
                "mood",
                MusicMood.CUSTOM.value,
            )
        )

        service = MusicService(self.db)

        plan = service.generate_music_plan(
            production_id=job.production_id,
            mood=mood,
        )

        return self.completed_response(
            job,
            music_plan_id=str(plan.id),
        )