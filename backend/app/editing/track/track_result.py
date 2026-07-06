from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TrackRuntimeResult:
    production_id: str
    track_key: str
    payload: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "track_key": self.track_key,
            "payload": self.payload,
            "metadata": self.metadata,
        }