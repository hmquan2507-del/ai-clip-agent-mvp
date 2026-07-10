from __future__ import annotations

from app.timeline.finalizer.runtime import TimelineFinalizerRuntime


def build_timeline_finalizer_runtime() -> TimelineFinalizerRuntime:
    return TimelineFinalizerRuntime()