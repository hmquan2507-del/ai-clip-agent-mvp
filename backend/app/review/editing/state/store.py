from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from threading import RLock
from typing import Any

from app.review.editing.models import (
    EditableTimeline,
)
from app.review.editing.state.models import (
    TimelineStateChange,
    TimelineStateResult,
)


TimelineStateListener = Callable[
    [TimelineStateChange],
    None,
]


class TimelineRuntimeStore:
    def __init__(
        self,
        timeline: EditableTimeline,
    ):
        self._timeline = timeline.clone()
        self._initial_timeline = timeline.clone()

        self._lock = RLock()

        self._changes: list[
            TimelineStateChange
        ] = []

        self._listeners: list[
            TimelineStateListener
        ] = []

    @property
    def production_id(self) -> str:
        return self._timeline.production_id

    @property
    def revision(self) -> int:
        return self._timeline.revision

    @property
    def changes(
        self,
    ) -> list[TimelineStateChange]:
        with self._lock:
            return deepcopy(self._changes)

    def snapshot(self) -> EditableTimeline:
        with self._lock:
            return self._timeline.clone()

    def initial_snapshot(
        self,
    ) -> EditableTimeline:
        with self._lock:
            return self._initial_timeline.clone()

    def replace(
        self,
        timeline: EditableTimeline,
        *,
        reason: str,
        metadata: dict[str, Any] | None = None,
    ) -> TimelineStateResult:
        with self._lock:
            if (
                timeline.production_id
                != self.production_id
            ):
                return TimelineStateResult(
                    success=False,
                    timeline=self.snapshot(),
                    error=(
                        "Timeline production_id "
                        "does not match runtime store."
                    ),
                )

            previous_revision = (
                self._timeline.revision
            )

            self._timeline = timeline.clone()

            change = TimelineStateChange(
                production_id=self.production_id,
                previous_revision=(
                    previous_revision
                ),
                current_revision=(
                    self._timeline.revision
                ),
                reason=reason,
                metadata=dict(
                    metadata or {}
                ),
            )

            self._record_change(change)

            return TimelineStateResult(
                success=True,
                timeline=self.snapshot(),
                change=change,
            )

    def commit(
        self,
        timeline: EditableTimeline,
        *,
        reason: str,
        metadata: dict[str, Any] | None = None,
    ) -> TimelineStateResult:
        return self.replace(
            timeline,
            reason=reason,
            metadata=metadata,
        )

    def reset(self) -> TimelineStateResult:
        return self.replace(
            self._initial_timeline,
            reason="reset",
        )

    def subscribe(
        self,
        listener: TimelineStateListener,
    ) -> None:
        if listener not in self._listeners:
            self._listeners.append(listener)

    def unsubscribe(
        self,
        listener: TimelineStateListener,
    ) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _record_change(
        self,
        change: TimelineStateChange,
    ) -> None:
        self._changes.append(
            deepcopy(change)
        )

        for listener in list(
            self._listeners
        ):
            listener(
                deepcopy(change)
            )