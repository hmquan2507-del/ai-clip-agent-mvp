from __future__ import annotations

from app.subtitle.timing.runtime import SubtitleTimingOptimizer


def build_subtitle_timing_optimizer() -> SubtitleTimingOptimizer:
    return SubtitleTimingOptimizer()