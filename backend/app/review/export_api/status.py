from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from app.services.queue_service import QueueService


def _serialize_datetime(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _serialize_enum(value: Any) -> str:
    return str(getattr(value, "value", value))


class ExportRenderStatusService:
    """Read-only Export Workspace projection over render queue jobs."""

    def __init__(self, queue_service: QueueService):
        self.queue_service = queue_service

    def get_status(self, queue_job_id: UUID) -> dict[str, Any]:
        job = self.queue_service.get(queue_job_id)

        return {
            "queue_job_id": str(getattr(job, "id", queue_job_id)),
            "production_id": str(getattr(job, "production_id", "")),
            "queue_type": _serialize_enum(getattr(job, "queue_type", "")),
            "status": _serialize_enum(getattr(job, "status", "")),
            "progress": int(getattr(job, "progress", 0) or 0),
            "error": getattr(job, "error_message", None),
            "created_at": _serialize_datetime(getattr(job, "created_at", None)),
            "started_at": _serialize_datetime(getattr(job, "started_at", None)),
            "finished_at": _serialize_datetime(getattr(job, "finished_at", None)),
            "updated_at": _serialize_datetime(getattr(job, "updated_at", None)),
        }
