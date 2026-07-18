from __future__ import annotations

from typing import Any, Iterable, Mapping

from app.review.suggestions.models import (
    AISuggestionReadModel,
)
from app.review.suggestions.read_model import (
    AISuggestionReadModelBuilder,
    RawSuggestion,
)
from app.review.suggestions.runtime import (
    AISuggestionLifecycleEventCallback,
    AISuggestionLifecycleRuntime,
)
from app.review.suggestions.store import (
    AISuggestionLifecycleStore,
)


def build_ai_suggestion_read_model(
    *,
    production_id: str,
    timeline_revision: int,
    raw_suggestions: Iterable[
        RawSuggestion
    ] = (),
    ai_metadata: Mapping[str, Any] | None = None,
    selected_suggestion_id: str | None = None,
) -> AISuggestionReadModel:
    return AISuggestionReadModelBuilder().build(
        production_id=production_id,
        timeline_revision=timeline_revision,
        raw_suggestions=raw_suggestions,
        ai_metadata=ai_metadata,
        selected_suggestion_id=(
            selected_suggestion_id
        ),
    )


def build_ai_suggestion_lifecycle_store(
    read_model: AISuggestionReadModel,
    *,
    maximum_changes: int = 100,
) -> AISuggestionLifecycleStore:
    return AISuggestionLifecycleStore(
        read_model,
        maximum_changes=maximum_changes,
    )


def build_ai_suggestion_lifecycle_runtime(
    read_model: AISuggestionReadModel,
    *,
    maximum_changes: int = 100,
    maximum_events: int = 100,
    event_callback: (
        AISuggestionLifecycleEventCallback
        | None
    ) = None,
) -> AISuggestionLifecycleRuntime:
    store = build_ai_suggestion_lifecycle_store(
        read_model,
        maximum_changes=maximum_changes,
    )
    return AISuggestionLifecycleRuntime(
        store,
        maximum_events=maximum_events,
        event_callback=event_callback,
    )


def build_ai_suggestion_lifecycle_runtime_from_store(
    store: AISuggestionLifecycleStore,
    *,
    maximum_events: int = 100,
    event_callback: (
        AISuggestionLifecycleEventCallback
        | None
    ) = None,
) -> AISuggestionLifecycleRuntime:
    return AISuggestionLifecycleRuntime(
        store,
        maximum_events=maximum_events,
        event_callback=event_callback,
    )
