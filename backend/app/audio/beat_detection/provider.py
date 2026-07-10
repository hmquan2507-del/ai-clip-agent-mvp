from __future__ import annotations

from abc import ABC, abstractmethod

from app.audio.beat_detection.models import (
    BeatDetectionRequest,
    BeatDetectionResult,
)


class BaseBeatDetectionProvider(ABC):
    provider_key = "base"

    @abstractmethod
    def detect(
        self,
        request: BeatDetectionRequest,
    ) -> BeatDetectionResult:
        raise NotImplementedError