from __future__ import annotations

from typing import Any

from app.editing.track.models import TrackContext
from app.editing.track.track_result import TrackRuntimeResult


class TrackRuntime:
    def run_composer(
        self,
        track_key: str,
        composer: Any,
        context: TrackContext,
        **kwargs: Any,
    ) -> TrackRuntimeResult:
        raw_result = composer.compose(
            context=context,
            **kwargs,
        )

        if hasattr(raw_result, "to_dict"):
            payload = raw_result.to_dict()
        elif isinstance(raw_result, dict):
            payload = raw_result
        else:
            payload = {"value": raw_result}

        return TrackRuntimeResult(
            production_id=context.production_id,
            track_key=track_key,
            payload=payload,
            metadata={
                "composer": getattr(
                    composer,
                    "track_name",
                    composer.__class__.__name__,
                )
            },
        )