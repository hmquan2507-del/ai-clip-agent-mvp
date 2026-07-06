from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TrackNode:
    node_id: str
    node_type: str
    track: str
    operation: str
    start_time: float
    end_time: float
    priority: str = "medium"
    weight: float = 0.5
    parameters: dict[str, Any] = field(default_factory=dict)
    source_segment_id: str | None = None
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "track": self.track,
            "operation": self.operation,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "priority": self.priority,
            "weight": self.weight,
            "parameters": self.parameters,
            "source_segment_id": self.source_segment_id,
            "reason": self.reason,
        }


@dataclass
class TrackContext:
    production_id: str
    global_nodes: list[TrackNode] = field(default_factory=list)
    timeline_nodes: list[TrackNode] = field(default_factory=list)
    video_nodes: list[TrackNode] = field(default_factory=list)
    camera_nodes: list[TrackNode] = field(default_factory=list)
    subtitle_nodes: list[TrackNode] = field(default_factory=list)
    broll_nodes: list[TrackNode] = field(default_factory=list)
    audio_nodes: list[TrackNode] = field(default_factory=list)
    sfx_nodes: list[TrackNode] = field(default_factory=list)
    custom_nodes: dict[str, list[TrackNode]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    music_nodes: list[TrackNode] = field(default_factory=list)

    def all_nodes(self) -> list[TrackNode]:
        nodes: list[TrackNode] = []

        nodes.extend(self.global_nodes)
        nodes.extend(self.timeline_nodes)
        nodes.extend(self.video_nodes)
        nodes.extend(self.camera_nodes)
        nodes.extend(self.subtitle_nodes)
        nodes.extend(self.broll_nodes)
        nodes.extend(self.audio_nodes)
        nodes.extend(self.sfx_nodes)
        nodes.extend(self.music_nodes)

        for custom in self.custom_nodes.values():
            nodes.extend(custom)

        return nodes

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "global_nodes": [node.to_dict() for node in self.global_nodes],
            "timeline_nodes": [node.to_dict() for node in self.timeline_nodes],
            "video_nodes": [node.to_dict() for node in self.video_nodes],
            "camera_nodes": [node.to_dict() for node in self.camera_nodes],
            "subtitle_nodes": [node.to_dict() for node in self.subtitle_nodes],
            "broll_nodes": [node.to_dict() for node in self.broll_nodes],
            "audio_nodes": [node.to_dict() for node in self.audio_nodes],
            "sfx_nodes": [node.to_dict() for node in self.sfx_nodes],
            "custom_nodes": {
                key: [node.to_dict() for node in value]
                for key, value in self.custom_nodes.items()
            },
            "metadata": self.metadata,
            "music_nodes": [node.to_dict() for node in self.music_nodes],
        }