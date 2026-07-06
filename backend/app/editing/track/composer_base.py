from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.editing.track.models import TrackContext


class BaseTrackComposer(ABC):
    track_name: str = "base"

    @abstractmethod
    def compose(self, context: TrackContext) -> dict[str, Any]:
        raise NotImplementedError