from __future__ import annotations

from app.editing.timeline.models import TimelineEvent, TimelineTrack
from app.editing.timeline.schema import DEFAULT_TRACKS, TRACK_TYPE_MAP


class TimelineTrackBuilder:
    def build_tracks(
        self,
        events: list[TimelineEvent],
    ) -> list[TimelineTrack]:
        tracks_by_name: dict[str, TimelineTrack] = {}

        for track_name in DEFAULT_TRACKS:
            tracks_by_name[track_name] = TimelineTrack(
                name=track_name,
                track_type=TRACK_TYPE_MAP.get(track_name, "unknown"),
            )

        for event in events:
            if event.track not in tracks_by_name:
                tracks_by_name[event.track] = TimelineTrack(
                    name=event.track,
                    track_type=TRACK_TYPE_MAP.get(event.track, "custom"),
                )

            tracks_by_name[event.track].add_event(event)

        for track in tracks_by_name.values():
            track.events.sort(
                key=lambda item: (
                    item.start_time,
                    self._priority_rank(item.priority),
                    item.operation,
                )
            )

        return list(tracks_by_name.values())

    def _priority_rank(self, priority: str) -> int:
        return {
            "high": 0,
            "medium": 1,
            "low": 2,
        }.get(priority, 99)