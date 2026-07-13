from __future__ import annotations

from app.review.editing.history.runtime import (
    TimelineCommandHistoryRuntime,
)
from app.review.editing.models import (
    EditableTimeline,
)
from app.review.editing.runtime import (
    TimelineMutationRuntime,
    build_timeline_mutation_runtime,
)
from app.review.editing.validator import (
    TimelineEditingValidator,
)


def build_timeline_history_runtime(
    timeline: EditableTimeline,
    *,
    validator: TimelineEditingValidator
    | None = None,
    maximum_history_size: int = 100,
) -> TimelineCommandHistoryRuntime:
    mutation_runtime = (
        build_timeline_mutation_runtime(
            timeline,
            validator=validator,
        )
    )

    return TimelineCommandHistoryRuntime(
        mutation_runtime=mutation_runtime,
        maximum_history_size=(
            maximum_history_size
        ),
    )


def build_history_from_mutation_runtime(
    mutation_runtime: TimelineMutationRuntime,
    *,
    maximum_history_size: int = 100,
) -> TimelineCommandHistoryRuntime:
    return TimelineCommandHistoryRuntime(
        mutation_runtime=mutation_runtime,
        maximum_history_size=(
            maximum_history_size
        ),
    )