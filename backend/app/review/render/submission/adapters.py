from __future__ import annotations

import json
import logging
from copy import deepcopy
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.enums import QueueType
from app.services.queue_service import QueueService

logger = logging.getLogger(__name__)


class QueueServiceRenderSubmissionAdapter:
    """Adapter from the 16.8.2 queue port to the existing QueueService."""

    def __init__(
        self,
        queue_service: QueueService,
        *,
        db: Session | None = None,
    ):
        self.queue_service = queue_service
        self.db = db
        self._idempotency_index: dict[str, str] = {}

    def find_by_idempotency_key(self, idempotency_key: str) -> str | None:
        return self._idempotency_index.get(idempotency_key)

    def submit_render(
        self,
        *,
        production_id: str,
        payload: dict[str, Any],
        idempotency_key: str,
    ) -> str:
        job = self.queue_service.create_job(
            production_id=UUID(production_id),
            queue_type=QueueType.RENDER_RUNTIME,
            payload=json.dumps(deepcopy(payload), ensure_ascii=False, sort_keys=True),
        )
        queue_job_id = str(job.id)
        self._idempotency_index[idempotency_key] = queue_job_id

        # This app has no background worker process (single-operator,
        # local-first) - run the job inline so a submission actually
        # renders instead of sitting queued forever. WorkerService.run_job
        # already records success/failure on the job row itself, so any
        # exception here is just belt-and-suspenders for a truly broken
        # dispatch (e.g. missing worker registration) - it must never
        # break the submission response, since the queued job id is
        # already valid and its status is independently pollable.
        if self.db is not None:
            from app.services.worker_service import WorkerService

            try:
                WorkerService(self.db).run_job(job.id)
            except Exception:
                logger.exception(
                    "Inline render worker run failed for queue job %s",
                    queue_job_id,
                )

        return queue_job_id
