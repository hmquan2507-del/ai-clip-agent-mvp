from __future__ import annotations

from app.timeline.compiler.runtime import (
    TimelineCompilerRuntime,
)


def build_timeline_compiler_runtime() -> (
    TimelineCompilerRuntime
):
    return TimelineCompilerRuntime()