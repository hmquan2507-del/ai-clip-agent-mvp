from __future__ import annotations

from typing import Any

from app.product.adapters.models import (
    ProductTimelineSummary,
)
from app.product.adapters.utils import (
    float_or_none,
    normalize,
    read_value,
    value_of,
)


class ProductTimelineAdapter:
    def adapt(
        self,
        timeline: Any | None,
        *,
        include_tracks: bool = True,
    ) -> ProductTimelineSummary:
        if timeline is None:
            return ProductTimelineSummary(
                available=False,
                metadata={
                    "adapter": "ProductTimelineAdapter",
                },
            )

        tracks = list(
            read_value(
                timeline,
                "tracks",
                [],
            )
            or []
        )

        effects = list(
            read_value(
                timeline,
                "effects",
                [],
            )
            or []
        )

        transitions = list(
            read_value(
                timeline,
                "transitions",
                [],
            )
            or []
        )

        clip_count = sum(
            len(
                read_value(
                    track,
                    "clips",
                    [],
                )
                or []
            )
            for track in tracks
        )

        canvas = normalize(
            read_value(
                timeline,
                "canvas",
                {},
            )
        )

        return ProductTimelineSummary(
            available=True,
            version=value_of(
                read_value(
                    timeline,
                    "version",
                )
            ),
            duration=float_or_none(
                read_value(
                    timeline,
                    "duration",
                )
            ),
            track_count=len(tracks),
            clip_count=clip_count,
            effect_count=len(effects),
            transition_count=len(transitions),
            canvas=canvas,
            tracks=(
                normalize(tracks)
                if include_tracks
                else []
            ),
            metadata={
                "adapter": "ProductTimelineAdapter",
                "production_id": str(
                    read_value(
                        timeline,
                        "production_id",
                        "",
                    )
                ),
                "tracks_included": include_tracks,
            },
        )