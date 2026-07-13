from __future__ import annotations

from app.review.selection.models import (
    TimelineSelectionCatalog,
    TimelineTimeRange,
)


class TimelineSelectionValidator:
    def validate_track(
        self,
        catalog: TimelineSelectionCatalog,
        track_id: str,
    ) -> str | None:
        if not track_id:
            return "track_id is required."

        if track_id not in catalog.track_ids:
            return (
                "Timeline track does not exist: "
                f"{track_id}"
            )

        return None

    def validate_clip(
        self,
        catalog: TimelineSelectionCatalog,
        clip_id: str,
    ) -> str | None:
        if not clip_id:
            return "clip_id is required."

        if clip_id not in catalog.clip_ids:
            return (
                "Timeline clip does not exist: "
                f"{clip_id}"
            )

        return None

    def validate_cursor(
        self,
        catalog: TimelineSelectionCatalog,
        value: float,
    ) -> str | None:
        try:
            time_value = float(value)
        except (TypeError, ValueError):
            return "Cursor time must be numeric."

        if time_value < 0:
            return (
                "Cursor time cannot be negative."
            )

        if time_value > catalog.duration:
            return (
                "Cursor time exceeds timeline "
                f"duration: {catalog.duration}"
            )

        return None

    def validate_range(
        self,
        catalog: TimelineSelectionCatalog,
        time_range: TimelineTimeRange,
    ) -> str | None:
        if time_range.duration <= 0:
            return (
                "Timeline range duration must "
                "be greater than zero."
            )

        if time_range.start_time < 0:
            return (
                "Timeline range cannot start "
                "before zero."
            )

        if (
            time_range.end_time
            > catalog.duration
        ):
            return (
                "Timeline range exceeds timeline "
                f"duration: {catalog.duration}"
            )

        return None

    def validate_track_ids(
        self,
        catalog: TimelineSelectionCatalog,
        track_ids: list[str],
    ) -> str | None:
        missing = [
            item
            for item in track_ids
            if item not in catalog.track_ids
        ]

        if missing:
            return (
                "Timeline tracks do not exist: "
                + ", ".join(missing)
            )

        return None

    def validate_clip_ids(
        self,
        catalog: TimelineSelectionCatalog,
        clip_ids: list[str],
    ) -> str | None:
        missing = [
            item
            for item in clip_ids
            if item not in catalog.clip_ids
        ]

        if missing:
            return (
                "Timeline clips do not exist: "
                + ", ".join(missing)
            )

        return None