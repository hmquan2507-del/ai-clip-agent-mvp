from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.db.enums import SubtitleStyle
from app.db.models.queue_job import QueueJob
from app.services.subtitle_service import SubtitleService
from app.workers.base import BaseWorker


class SubtitleWorker(BaseWorker):
    def __init__(self, db: Session | None = None):
        self.db = db

    def run(self, job: QueueJob) -> dict:
        if self.db is None:
            return {
                "worker": "subtitle",
                "job_id": str(job.id),
                "status": "skipped",
                "message": "Subtitle worker requires database session.",
            }

        payload = self._parse_payload(job.payload)
        style = SubtitleStyle(payload.get("style", SubtitleStyle.DEFAULT.value))

        service = SubtitleService(self.db)

        subtitle = service.generate_subtitle(
            production_id=job.production_id,
            style=style,
        )

        return {
            "worker": "subtitle",
            "job_id": str(job.id),
            "status": "completed",
            "subtitle_id": str(subtitle.id),
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