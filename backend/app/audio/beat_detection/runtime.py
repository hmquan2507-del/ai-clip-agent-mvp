from __future__ import annotations

from app.audio.beat_detection.mock_provider import MockBeatDetectionProvider
from app.audio.beat_detection.models import (
    BeatDetectionRequest,
    BeatDetectionResult,
)
from app.audio.beat_detection.provider import BaseBeatDetectionProvider
from app.audio.beat_detection.models import (
    BeatDetectionRequest,
    BeatDetectionResult,
    BeatPoint,
)

class BeatDetectionRuntime:
    def __init__(
        self,
        provider: BaseBeatDetectionProvider | None = None,
    ):
        self.provider = provider or MockBeatDetectionProvider()

    def detect(
        self,
        request: BeatDetectionRequest,
    ) -> BeatDetectionResult:
        result = self.provider.detect(request)

        self._validate_result(result)

        return result

    def nearest_beat(
        self,
        result: BeatDetectionResult,
        target_time: float,
        max_distance: float | None = None,
        prefer_downbeat: bool = False,
    ) -> BeatPoint | None:
        candidates = result.beats

        if prefer_downbeat:
            downbeats = [
                beat
                for beat in result.beats
                if beat.is_downbeat
            ]

            if downbeats:
                candidates = downbeats

        if not candidates:
            return None

        nearest = min(
            candidates,
            key=lambda beat: abs(beat.time - target_time),
        )

        distance = abs(nearest.time - target_time)

        if max_distance is not None and distance > max_distance:
            return None

        return nearest

    def beats_between(
        self,
        result: BeatDetectionResult,
        start_time: float,
        end_time: float,
    ) -> list[BeatPoint]:
        return [
            beat
            for beat in result.beats
            if start_time <= beat.time <= end_time
        ]

    def _validate_result(
        self,
        result: BeatDetectionResult,
    ) -> None:
        if result.bpm <= 0:
            raise ValueError("Beat detection BPM must be greater than zero.")

        if result.duration < 0:
            raise ValueError("Beat detection duration cannot be negative.")

        previous_time = -1.0

        for beat in result.beats:
            if beat.time < previous_time:
                raise ValueError(
                    "Beat points must be sorted by ascending time."
                )

            previous_time = beat.time