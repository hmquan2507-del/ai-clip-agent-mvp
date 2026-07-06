from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RenderContext:
    production_id: str
    composition: dict[str, Any]
    assets: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_layers(self) -> list[dict[str, Any]]:
        layers = self.composition.get("layers", [])

        if not isinstance(layers, list):
            return []

        return [layer for layer in layers if isinstance(layer, dict)]


@dataclass
class RenderRuntimeResult:
    production_id: str
    key: str
    payload: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "key": self.key,
            "payload": self.payload,
            "metadata": self.metadata,
        }