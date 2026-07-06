from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.editing.track.audio.layer_models import AudioLayer


@dataclass
class AudioTrack:
    production_id: str
    layers: list[AudioLayer] = field(default_factory=list)
    mix_order: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "layers": [layer.to_dict() for layer in self.layers],
            "mix_order": self.mix_order,
            "metadata": self.metadata,
        }