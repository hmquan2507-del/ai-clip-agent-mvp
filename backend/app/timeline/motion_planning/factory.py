from __future__ import annotations

from app.timeline.motion_planning.runtime import MotionPlanningRuntime


def build_motion_planning_runtime() -> MotionPlanningRuntime:
    return MotionPlanningRuntime()