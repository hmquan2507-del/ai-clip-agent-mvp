from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VideoLayerEvent:
    start_time: float
    end_time: float
    operation: str
    parameters: dict[str, Any] = field(default_factory=dict)
    priority: str = "medium"
    source_node_id: str | None = None
    source_segment_id: str | None = None
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "operation": self.operation,
            "parameters": self.parameters,
            "priority": self.priority,
            "source_node_id": self.source_node_id,
            "source_segment_id": self.source_segment_id,
            "reason": self.reason,
        }


@dataclass
class VideoLayer:
    layer_name: str
    layer_type: str
    events: list[VideoLayerEvent] = field(default_factory=list)

    def add_event(self, event: VideoLayerEvent) -> None:
        self.events.append(event)

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer_name": self.layer_name,
            "layer_type": self.layer_type,
            "events": [event.to_dict() for event in self.events],
        }