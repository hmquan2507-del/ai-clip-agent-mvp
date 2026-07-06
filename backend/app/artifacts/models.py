from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuntimeArtifactPayload:
    production_id: str
    artifact_key: str
    payload: dict[str, Any]
    artifact_version: int | None = None
    checksum: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "artifact_key": self.artifact_key,
            "artifact_version": self.artifact_version,
            "checksum": self.checksum,
            "payload": self.payload,
            "metadata": self.metadata,
        }