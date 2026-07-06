from __future__ import annotations

from typing import Any


class RenderRuntimeRegistry:
    def __init__(self):
        self._runtimes: dict[str, Any] = {}

    def register(self, key: str, runtime: Any) -> None:
        if not key:
            raise ValueError("Runtime key is required")

        self._runtimes[key] = runtime

    def get(self, key: str) -> Any:
        runtime = self._runtimes.get(key)

        if runtime is None:
            raise ValueError(f"Render runtime not registered: {key}")

        return runtime

    def has(self, key: str) -> bool:
        return key in self._runtimes

    def keys(self) -> list[str]:
        return list(self._runtimes.keys())