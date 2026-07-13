from __future__ import annotations

from app.review.editing.models import (
    EditableTimeline,
)
from app.review.editing.state.store import (
    TimelineRuntimeStore,
)


def build_timeline_runtime_store(
    timeline: EditableTimeline,
) -> TimelineRuntimeStore:
    return TimelineRuntimeStore(
        timeline=timeline
    )