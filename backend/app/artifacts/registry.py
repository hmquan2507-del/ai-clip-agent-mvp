from __future__ import annotations

from typing import Any


class ArtifactRegistry:
    def __init__(self):
        self._artifacts: dict[str, Any] = {}

    def register(self, artifact_key: str, artifact_type: Any) -> None:
        if not artifact_key:
            raise ValueError("Artifact key is required")

        self._artifacts[artifact_key] = artifact_type

    def get(self, artifact_key: str) -> Any | None:
        return self._artifacts.get(artifact_key)

    def has(self, artifact_key: str) -> bool:
        return artifact_key in self._artifacts

    def keys(self) -> list[str]:
        return list(self._artifacts.keys())