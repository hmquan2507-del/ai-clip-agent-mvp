from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.queue_job import QueueJob
from app.services.content_understanding_service import (
    ContentUnderstandingService,
)
from app.workers.base_runtime_worker import BaseRuntimeWorker


class ContentUnderstandingWorker(BaseRuntimeWorker):
    worker_name = "content_understanding"

    def __init__(self, db: Session | None = None):
        super().__init__(db=db)

    def run(self, job: QueueJob) -> dict:
        if self.db is None:
            return self.skipped_response(
                job,
                "Content Understanding worker requires database session.",
            )

        graph = ContentUnderstandingService(
            self.db
        ).generate_content_graph(
            production_id=job.production_id,
        )

        return self.completed_response(
            job,
            content_graph_id=str(graph.id),
        )