from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TimelineEvent:
    event_type: str
    start_time: float
    end_time: float
    track: str
    operation: str
    parameters: dict[str, Any] = field(default_factory=dict)
    priority: str = "medium"
    source_instruction_type: str | None = None
    source_segment_id: str | None = None
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "track": self.track,
            "operation": self.operation,
            "parameters": self.parameters,
            "priority": self.priority,
            "source_instruction_type": self.source_instruction_type,
            "source_segment_id": self.source_segment_id,
            "reason": self.reason,
        }


@dataclass
class TimelineTrack:
    name: str
    track_type: str
    events: list[TimelineEvent] = field(default_factory=list)

    def add_event(self, event: TimelineEvent) -> None:
        self.events.append(event)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "track_type": self.track_type,
            "events": [event.to_dict() for event in self.events],
        }


@dataclass
class EditableTimeline:
    production_id: str
    duration: float | None = None
    tracks: list[TimelineTrack] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "duration": self.duration,
            "tracks": [track.to_dict() for track in self.tracks],
            "metadata": self.metadata,
        }