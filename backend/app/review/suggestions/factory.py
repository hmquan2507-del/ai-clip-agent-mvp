from __future__ import annotations

from typing import Any, Iterable, Mapping

from app.review.suggestions.models import (
    AISuggestionReadModel,
)
from app.review.suggestions.read_model import (
    AISuggestionReadModelBuilder,
    RawSuggestion,
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
