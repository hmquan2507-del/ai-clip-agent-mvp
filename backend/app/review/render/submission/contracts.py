from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class RenderSubmissionRequest:
    contract_payload: dict[str, Any]
    requested_by: str | None = None
    correlation_id: str | None = None

    @property
    def production_id(self) -> str:
        return str(self.contract_payload["production_id"])

    @property
    def snapshot_id(self) -> str:
        return str(self.contract_payload["snapshot_id"])

    @property
    def checksum(self) -> str:
        return str(self.contract_payload["checksum"])

    @property
    def idempotency_key(self) -> str:
        return f"{self.production_id}:{self.snapshot_id}:{self.checksum}"

    def to_queue_payload(self) -> dict[str, Any]:
        return {
            "submission_version": "16.8.2",
            "idempotency_key": self.idempotency_key,
            "requested_by": self.requested_by,
            "correlation_id": self.correlation_id,
            "submitted_at": utc_now_iso(),
            "review_render_contract": deepcopy(self.contract_payload),
        }


@dataclass(frozen=True)
class RenderSubmissionReceipt:
    queue_job_id: str
    production_id: str
    snapshot_id: str
    timeline_revision: int
    idempotency_key: str
    status: str = "pending"
    duplicate: bool = False
    submitted_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "queue_job_id": self.queue_job_id,
            "production_id": self.production_id,
            "snapshot_id": self.snapshot_id,
            "timeline_revision": self.timeline_revision,
            "idempotency_key": self.idempotency_key,
            "status": self.status,
            "duplicate": self.duplicate,
            "submitted_at": self.submitted_at,
        }


@dataclass(frozen=True)
class RenderSubmissionResult:
    success: bool
    receipt: RenderSubmissionReceipt | None = None
    error_code: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "receipt": self.receipt.to_dict() if self.receipt else None,
            "error_code": self.error_code,
            "error": self.error,
        }
