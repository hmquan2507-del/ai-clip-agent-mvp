from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SubtitleEvent:
    start_time: float
    end_time: float
    text: str
    style: dict[str, Any] = field(default_factory=dict)
    animation: str = "none"
    priority: str = "medium"
    source_segment_id: str | None = None
    source_node_id: str | None = None
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "text": self.text,
            "style": self.style,
            "animation": self.animation,
            "priority": self.priority,
            "source_segment_id": self.source_segment_id,
            "source_node_id": self.source_node_id,
            "reason": self.reason,
        }


@dataclass
class SubtitleTrack:
    production_id: str
    events: list[SubtitleEvent] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "events": [event.to_dict() for event in self.events],
            "metadata": self.metadata,
        }