from __future__ import annotations

from app.review.editing.clipboard.runtime import (
    TimelineClipboardRuntime,
)
from app.review.editing.history.runtime import (
    TimelineCommandHistoryRuntime,
)
from app.review.editing.models import (
    EditableTimeline,
)
from app.review.editing.runtime import (
    TimelineMutationRuntime,
)


def build_timeline_clipboard_runtime(
    timeline: EditableTimeline,
    *,
    history_runtime: (
        TimelineCommandHistoryRuntime
        | None
    ) = None,
    maximum_history_size: int = 20,
) -> TimelineClipboardRuntime:
    return TimelineClipboardRuntime(
        timeline=timeline,
        history_runtime=history_runtime,
        maximum_history_size=(
            maximum_history_size
        ),
    )


def build_clipboard_from_history_runtime(
    history_runtime: (
        TimelineCommandHistoryRuntime
    ),
    *,
    maximum_history_size: int = 20,
) -> TimelineClipboardRuntime:
    return TimelineClipboardRuntime(
        timeline=history_runtime.timeline,
        history_runtime=history_runtime,
        maximum_history_size=(
            maximum_history_size
        ),
    )


def build_clipboard_from_mutation_runtime(
    mutation_runtime: (
        TimelineMutationRuntime
    ),
    *,
    maximum_history_size: int = 20,
) -> TimelineClipboardRuntime:
    return TimelineClipboardRuntime(
        timeline=mutation_runtime.snapshot(),
        maximum_history_size=(
            maximum_history_size
        ),
    )