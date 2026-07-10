from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FinalTimelineClip:
    clip_id: str
    track_type: str
    start_time: float
    end_time: float
    layer: int

    asset_id: str | None = None
    local_path: str | None = None
    content: str | None = None

    volume: float | None = None
    opacity: float | None = None
    speed: float | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "track_type": self.track_type,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "layer": self.layer,
            "asset_id": self.asset_id,
            "local_path": self.local_path,
            "content": self.content,
            "volume": self.volume,
            "opacity": self.opacity,
            "speed": self.speed,
            "metadata": self.metadata,
        }


@dataclass
class FinalTimelineEffect:
    effect_id: str
    target_id: str
    effect_type: str
    start_time: float
    end_time: float
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "effect_id": self.effect_id,
            "target_id": self.target_id,
            "effect_type": self.effect_type,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "parameters": self.parameters,
            "metadata": self.metadata,
        }


@dataclass
class FinalTimelineTransition:
    transition_id: str
    target_id: str
    transition_type: str
    at_time: float
    duration: float
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "target_id": self.target_id,
            "transition_type": self.transition_type,
            "at_time": self.at_time,
            "duration": self.duration,
            "parameters": self.parameters,
            "metadata": self.metadata,
        }


@dataclass
class FinalTimelineTrack:
    track_id: str
    track_type: str
    layer: int
    clips: list[FinalTimelineClip] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "track_id": self.track_id,
            "track_type": self.track_type,
            "layer": self.layer,
            "clips": [clip.to_dict() for clip in self.clips],
            "metadata": self.metadata,
        }


@dataclass
class FinalTimeline:
    production_id: str
    version: str
    duration: float
    width: int
    height: int
    fps: float

    tracks: list[FinalTimelineTrack]
    effects: list[FinalTimelineEffect]
    transitions: list[FinalTimelineTransition]

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "version": self.version,
            "duration": self.duration,
            "canvas": {
                "width": self.width,
                "height": self.height,
                "fps": self.fps,
            },
            "tracks": [track.to_dict() for track in self.tracks],
            "effects": [effect.to_dict() for effect in self.effects],
            "transitions": [
                transition.to_dict()
                for transition in self.transitions
            ],
            "metadata": self.metadata,
        }