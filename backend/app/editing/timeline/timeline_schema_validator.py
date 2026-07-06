from __future__ import annotations

from app.editing.timeline.models import EditableTimeline


class TimelineSchemaValidator:
    def validate(self, timeline: EditableTimeline) -> list[str]:
        errors: list[str] = []

        if not timeline.production_id:
            errors.append("production_id_required")

        for track in timeline.tracks:
            if not track.name:
                errors.append("track_name_required")

            for event in track.events:
                if event.start_time < 0:
                    errors.append("event_start_time_negative")

                if event.end_time < event.start_time:
                    errors.append("event_end_before_start")

                if not event.operation:
                    errors.append("event_operation_required")

                if not event.track:
                    errors.append("event_track_required")

        return errors