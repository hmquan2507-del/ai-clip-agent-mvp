from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.review.editing.models import (
    EditableTimeline,
)


def utc_now_iso() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


@dataclass(frozen=True)
class TimelineStateChange:
    production_id: str
    previous_revision: int
    current_revision: int
    reason: str

    created_at: str = field(
        default_factory=utc_now_iso
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "previous_revision": (
                self.previous_revision
            ),
            "current_revision": (
                self.current_revision
            ),
            "reason": self.reason,
            "created_at": self.created_at,
            "metadata": deepcopy(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class TimelineStateResult:
    success: bool
    timeline: EditableTimeline

    change: TimelineStateChange | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "timeline": self.timeline.to_dict(),
            "change": (
                self.change.to_dict()
                if self.change
                else None
            ),
            "error": self.error,
        }
