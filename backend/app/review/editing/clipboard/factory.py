from __future__ import annotations

from app.review.editing.clipboard.runtime import TimelineClipboardRuntime
from app.review.editing.history.runtime import TimelineCommandHistoryRuntime
from app.review.editing.models import EditableTimeline
from app.review.editing.runtime import TimelineMutationRuntime
from app.review.editing.state.factory import build_timeline_runtime_store
from app.review.editing.state.store import TimelineRuntimeStore


def build_timeline_clipboard_runtime(
    timeline: EditableTimeline,
    *,
    history_runtime: TimelineCommandHistoryRuntime | None = None,
    maximum_history_size: int = 20,
) -> TimelineClipboardRuntime:
    if history_runtime is not None:
        return TimelineClipboardRuntime(
            timeline=timeline,
            store=history_runtime.store,
            history_runtime=history_runtime,
            maximum_history_size=maximum_history_size,
        )

    store = build_timeline_runtime_store(timeline)
    return build_clipboard_from_store(
        store,
        maximum_history_size=maximum_history_size,
    )


def build_clipboard_from_store(
    store: TimelineRuntimeStore,
    *,
    history_runtime: TimelineCommandHistoryRuntime | None = None,
    maximum_history_size: int = 20,
) -> TimelineClipboardRuntime:
    return TimelineClipboardRuntime(
        store=store,
        history_runtime=history_runtime,
        maximum_history_size=maximum_history_size,
    )


def build_clipboard_from_history_runtime(
    history_runtime: TimelineCommandHistoryRuntime,
    *,
    maximum_history_size: int = 20,
) -> TimelineClipboardRuntime:
    return build_clipboard_from_store(
        history_runtime.store,
        history_runtime=history_runtime,
        maximum_history_size=maximum_history_size,
    )


def build_clipboard_from_mutation_runtime(
    mutation_runtime: TimelineMutationRuntime,
    *,
    maximum_history_size: int = 20,
) -> TimelineClipboardRuntime:
    return build_clipboard_from_store(
        mutation_runtime.store,
        maximum_history_size=maximum_history_size,
    )