from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AssetMetadata:
    data: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        return dict(self.data)