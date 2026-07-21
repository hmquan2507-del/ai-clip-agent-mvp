from __future__ import annotations

import json
from copy import deepcopy
from typing import Any
from uuid import UUID

from app.db.enums import QueueType
from app.services.queue_service import QueueService


class QueueServiceRenderSubmissionAdapter:
    """Adapter from the 16.8.2 queue port to the existing QueueService."""

    def __init__(self, queue_service: QueueService):
        self.queue_service = queue_service
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
        return queue_job_id
