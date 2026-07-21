from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from app.review.editing.models import EditableTimeline
from app.review.editing.ripple.enums import RippleEditOperation, RippleEditPolicy


@dataclass(frozen=True)
class RippleEditRequest:
    operation: RippleEditOperation
    policy: RippleEditPolicy
    clip_ids: tuple[str, ...] = ()
    range_start: float | None = None
    range_end: float | None = None
    anchor_track_id: str | None = None
    expected_revision: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "operation", RippleEditOperation(self.operation))
        object.__setattr__(self, "policy", RippleEditPolicy(self.policy))
        normalized = tuple(dict.fromkeys(str(item).strip() for item in self.clip_ids if str(item).strip()))
        object.__setattr__(self, "clip_ids", normalized)
        object.__setattr__(self, "metadata", deepcopy(self.metadata))


@dataclass(frozen=True)
class RippleEditResult:
    success: bool
    timeline: EditableTimeline
    operation: RippleEditOperation
    policy: RippleEditPolicy
    removed_clip_ids: tuple[str, ...] = ()
    shifted_clip_ids: tuple[str, ...] = ()
    affected_track_ids: tuple[str, ...] = ()
    ripple_start: float | None = None
    ripple_end: float | None = None
    ripple_delta: float = 0.0
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "operation": self.operation.value,
            "policy": self.policy.value,
            "removed_clip_ids": list(self.removed_clip_ids),
            "shifted_clip_ids": list(self.shifted_clip_ids),
            "affected_track_ids": list(self.affected_track_ids),
            "ripple_start": self.ripple_start,
            "ripple_end": self.ripple_end,
            "ripple_delta": self.ripple_delta,
            "revision": self.timeline.revision,
            "dirty": self.timeline.dirty,
            "error": self.error,
            "metadata": deepcopy(self.metadata),
        }
