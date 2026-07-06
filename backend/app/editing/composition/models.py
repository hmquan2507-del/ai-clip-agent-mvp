from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TrackArtifact:
    track_key: str
    payload: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "track_key": self.track_key,
            "payload": self.payload,
            "metadata": self.metadata,
        }


@dataclass
class CompositionLayer:
    layer_key: str
    layer_type: str
    track_key: str
    events: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer_key": self.layer_key,
            "layer_type": self.layer_type,
            "track_key": self.track_key,
            "events": self.events,
            "metadata": self.metadata,
        }


@dataclass
class Composition:
    production_id: str
    layers: list[CompositionLayer] = field(default_factory=list)
    render_order: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "layers": [layer.to_dict() for layer in self.layers],
            "render_order": self.render_order,
            "metadata": self.metadata,
        }