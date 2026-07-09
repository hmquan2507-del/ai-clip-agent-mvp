from __future__ import annotations

from app.timeline.broll_placement.models import BrollPlacementResult
from app.timeline.transition_planning.models import (
    TransitionPlan,
    TransitionPlanningResult,
)


class TransitionPlanningRuntime:
    def plan(
        self,
        production_id: str,
        placements: BrollPlacementResult,
    ) -> TransitionPlanningResult:
        transitions: list[TransitionPlan] = []

        for placement in placements.placements:
            transition_type = placement.transition_hint or "none"

            if transition_type == "none":
                continue

            transitions.append(
                TransitionPlan(
                    segment_id=placement.segment_id,
                    target_id=placement.asset_id,
                    transition_type=transition_type,
                    at_time=placement.start_time,
                    duration=self._duration(transition_type),
                    intensity=self._intensity(transition_type),
                    metadata={
                        "placement_type": placement.placement_type,
                        "local_path": placement.local_path,
                        "reason": placement.reason,
                    },
                )
            )

        return TransitionPlanningResult(
            production_id=production_id,
            transitions=transitions,
            metadata={
                "runtime": "TransitionPlanningRuntime",
                "placement_count": len(placements.placements),
                "transition_count": len(transitions),
            },
        )

    def _duration(self, transition_type: str) -> float:
        if transition_type in {"impact_cut", "quick_cut"}:
            return 0.12

        if transition_type in {"smooth_cut"}:
            return 0.25

        if transition_type in {"clean_cut"}:
            return 0.18

        return 0.2

    def _intensity(self, transition_type: str) -> str:
        if transition_type in {"impact_cut", "quick_cut"}:
            return "high"

        if transition_type in {"smooth_cut"}:
            return "medium"

        return "low"