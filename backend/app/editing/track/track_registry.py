from __future__ import annotations

from typing import Any


class TrackComposerRegistry:
    def __init__(self):
        self._composers: dict[str, Any] = {}

    def register(self, track_name: str, composer: Any) -> None:
        if not track_name:
            raise ValueError("Track name is required")

        self._composers[track_name] = composer

    def get(self, track_name: str) -> Any:
        composer = self._composers.get(track_name)

        if composer is None:
            raise ValueError(f"Track composer not registered: {track_name}")

        return composer

    def has(self, track_name: str) -> bool:
        return track_name in self._composers

    def keys(self) -> list[str]:
        return list(self._composers.keys())