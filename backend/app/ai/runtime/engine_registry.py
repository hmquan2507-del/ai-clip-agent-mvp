from __future__ import annotations

from typing import Any


class EngineRegistry:
    def __init__(self):
        self._engines: dict[str, Any] = {}

    def register(self, key: str, engine: Any) -> None:
        if not key:
            raise ValueError("Engine key is required")

        self._engines[key] = engine

    def get(self, key: str) -> Any:
        engine = self._engines.get(key)

        if engine is None:
            raise ValueError(f"Engine not registered: {key}")

        return engine

    def has(self, key: str) -> bool:
        return key in self._engines

    def keys(self) -> list[str]:
        return list(self._engines.keys())