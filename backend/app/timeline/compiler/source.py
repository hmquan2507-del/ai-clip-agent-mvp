from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TimelineSourceMedia:
    asset_id: str | None
    local_path: str
    storage_key: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate_path(self) -> Path:
        path = Path(self.local_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Source video does not exist: {self.local_path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Source video path is not a file: {self.local_path}"
            )

        return path