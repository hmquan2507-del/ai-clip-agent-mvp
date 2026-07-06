from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.editing.track.video.layer_models import VideoLayer


@dataclass
class VideoTrack:
    production_id: str
    layers: list[VideoLayer] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "layers": [layer.to_dict() for layer in self.layers],
            "metadata": self.metadata,
        }