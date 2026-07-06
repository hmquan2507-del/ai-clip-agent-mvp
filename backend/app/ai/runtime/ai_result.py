from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AIResult:
    production_id: str
    key: str
    data: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "key": self.key,
            "data": self.data,
            "metadata": self.metadata,
        }