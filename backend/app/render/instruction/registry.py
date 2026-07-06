from __future__ import annotations

from typing import Any


class RenderInstructionRegistry:
    def __init__(self):
        self._builders: dict[str, Any] = {}

    def register(self, key: str, builder: Any) -> None:
        if not key:
            raise ValueError("Instruction builder key is required")

        self._builders[key] = builder

    def get(self, key: str) -> Any:
        builder = self._builders.get(key)

        if builder is None:
            raise ValueError(f"Instruction builder not registered: {key}")

        return builder

    def has(self, key: str) -> bool:
        return key in self._builders

    def keys(self) -> list[str]:
        return list(self._builders.keys())