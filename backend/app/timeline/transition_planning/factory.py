from __future__ import annotations

from app.timeline.transition_planning.runtime import TransitionPlanningRuntime


def build_transition_planning_runtime() -> TransitionPlanningRuntime:
    return TransitionPlanningRuntime()