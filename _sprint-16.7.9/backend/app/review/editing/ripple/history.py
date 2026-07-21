from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from app.review.editing.enums import TimelineEditingOperationType
from app.review.editing.history.runtime import TimelineCommandHistoryRuntime
from app.review.editing.models import TimelineEditingEvent, TimelineMutationResult
from app.review.editing.ripple.enums import RippleEditPolicy
from app.review.editing.ripple.runtime import RippleEditRuntime


class RippleEditHistoryRuntime:
    """Routes ripple edits through the shared history boundary.

    RippleEditRuntime remains the atomic timeline mutation owner. This adapter
    converts its result into the common mutation contract so undo/redo records
    exactly one before/after command.
    """

    def __init__(self, *, ripple_runtime: RippleEditRuntime, history_runtime: TimelineCommandHistoryRuntime):
        if ripple_runtime.store is not history_runtime.store:
            raise ValueError("Ripple and history runtimes must share one TimelineRuntimeStore.")
        self.ripple_runtime = ripple_runtime
        self.history_runtime = history_runtime

    def delete_clips(
        self,
        clip_ids: Iterable[str],
        *,
        policy: RippleEditPolicy = RippleEditPolicy.TRACK,
        anchor_track_id: str | None = None,
        expected_revision: int | None = None,
    ):
        resolved_ids = tuple(clip_ids)
        return self.history_runtime.execute(
            operation_type=TimelineEditingOperationType.RIPPLE_EDIT,
            label="Ripple delete clips",
            mutation=lambda: self._adapt(self.ripple_runtime.delete_clips(
                resolved_ids,
                policy=policy,
                anchor_track_id=anchor_track_id,
                expected_revision=expected_revision,
            )),
            metadata={"ripple_operation": "delete", "clip_ids": list(resolved_ids), "policy": policy.value},
        )

    def close_range(
        self,
        range_start: float,
        range_end: float,
        *,
        policy: RippleEditPolicy = RippleEditPolicy.TRACK,
        anchor_track_id: str | None = None,
        expected_revision: int | None = None,
    ):
        return self.history_runtime.execute(
            operation_type=TimelineEditingOperationType.RIPPLE_EDIT,
            label="Ripple close range",
            mutation=lambda: self._adapt(self.ripple_runtime.close_range(
                range_start,
                range_end,
                policy=policy,
                anchor_track_id=anchor_track_id,
                expected_revision=expected_revision,
            )),
            metadata={"ripple_operation": "close_range", "range_start": range_start, "range_end": range_end, "policy": policy.value},
        )

    @staticmethod
    def _adapt(result) -> TimelineMutationResult:
        if not result.success:
            return TimelineMutationResult(success=False, timeline=result.timeline, error=result.error, metadata=dict(result.metadata))
        metadata: dict[str, Any] = {
            **dict(result.metadata),
            "ripple_operation": result.operation.value,
            "ripple_policy": result.policy.value,
            "removed_clip_ids": list(result.removed_clip_ids),
            "shifted_clip_ids": list(result.shifted_clip_ids),
            "affected_track_ids": list(result.affected_track_ids),
            "ripple_start": result.ripple_start,
            "ripple_end": result.ripple_end,
            "ripple_delta": result.ripple_delta,
        }
        event = TimelineEditingEvent(
            operation_type=TimelineEditingOperationType.RIPPLE_EDIT,
            production_id=result.timeline.production_id,
            revision=result.timeline.revision,
            before=None,
            after=result.timeline.to_dict(),
            metadata=metadata,
        )
        return TimelineMutationResult(success=True, timeline=result.timeline, event=event, metadata=metadata)
