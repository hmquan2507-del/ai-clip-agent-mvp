from __future__ import annotations

from app.audio.beat_detection.runtime import BeatDetectionRuntime


def build_beat_detection_runtime() -> BeatDetectionRuntime:
    return BeatDetectionRuntime()