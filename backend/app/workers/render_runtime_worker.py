from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.queue_job import QueueJob
from app.services.render_export_service import (
    RenderExportError,
    render_production,
)
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

        try:
            export = render_production(
                self.db,
                job.production_id,
            )
        except RenderExportError as error:
            raise RuntimeError(str(error)) from error

        return self.completed_response(
            job,
            export_id=str(export.id),
            final_video_path=export.storage_path,
        )