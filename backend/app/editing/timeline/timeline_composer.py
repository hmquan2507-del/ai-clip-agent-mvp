from __future__ import annotations

from typing import Any

from app.editing.timeline.instruction_normalizer import TimelineInstructionNormalizer
from app.editing.timeline.models import EditableTimeline
from app.editing.timeline.timeline_schema_validator import TimelineSchemaValidator
from app.editing.timeline.track_builder import TimelineTrackBuilder


class TimelineComposer:
    def __init__(self):
        self.normalizer = TimelineInstructionNormalizer()
        self.track_builder = TimelineTrackBuilder()
        self.validator = TimelineSchemaValidator()

    def compose(
        self,
        production_id: str,
        instructions: list[dict[str, Any]],
        duration: float | None = None,
    ) -> EditableTimeline:
        events = self.normalizer.normalize_many(instructions)
        tracks = self.track_builder.build_tracks(events)

        timeline = EditableTimeline(
            production_id=production_id,
            duration=duration,
            tracks=tracks,
            metadata={
                "composer": "timeline_composer",
                "instruction_count": len(instructions),
                "event_count": len(events),
                "track_count": len(tracks),
            },
        )

        errors = self.validator.validate(timeline)
        timeline.metadata["validation_errors"] = errors
        timeline.metadata["is_valid"] = len(errors) == 0

        return timeline