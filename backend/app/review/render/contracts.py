from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ReviewRenderContract:
    production_id: str
    timeline_revision: int
    timeline: dict[str, Any]
    snapshot_id: str = field(default_factory=lambda: str(uuid4()))
    contract_version: str = "16.8.1"
    created_at: str = field(default_factory=utc_now_iso)
    render_options: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    checksum: str = ""

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "snapshot_id": self.snapshot_id,
            "production_id": self.production_id,
            "timeline_revision": self.timeline_revision,
            "timeline": deepcopy(self.timeline),
            "render_options": deepcopy(self.render_options),
            "metadata": deepcopy(self.metadata),
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self.canonical_payload()
        payload.update({"created_at": self.created_at, "checksum": self.checksum})
        return payload


@dataclass(frozen=True)
class ReviewRenderHandoffResult:
    success: bool
    contract: ReviewRenderContract | None = None
    error_code: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "contract": self.contract.to_dict() if self.contract else None,
            "error_code": self.error_code,
            "error": self.error,
        }
