from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AIContext:
    production_id: str
    payload: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    runtime_data: dict[str, Any] = field(default_factory=dict)

    def get_segments(self) -> list[dict[str, Any]]:
        segments = self.payload.get("segments")

        if not isinstance(segments, list):
            return []

        return [segment for segment in segments if isinstance(segment, dict)]

    def get_runtime_result(self, key: str, default: Any = None) -> Any:
        return self.runtime_data.get(key, self.metadata.get(key, default))

    def set_runtime_result(self, key: str, value: Any) -> None:
        self.runtime_data[key] = value