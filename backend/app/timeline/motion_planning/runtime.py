from __future__ import annotations

from app.timeline.broll_placement.models import BrollPlacementResult
from app.timeline.motion_planning.models import MotionPlan, MotionPlanningResult


class MotionPlanningRuntime:
    def plan(
        self,
        production_id: str,
        placements: BrollPlacementResult,
    ) -> MotionPlanningResult:
        motions: list[MotionPlan] = []

        for placement in placements.placements:
            motion_type = placement.motion_hint or "none"

            if motion_type == "none":
                continue

            motions.append(
                MotionPlan(
                    segment_id=placement.segment_id,
                    target_id=placement.asset_id,
                    start_time=placement.start_time,
                    end_time=placement.end_time,
                    motion_type=motion_type,
                    intensity=self._intensity(motion_type),
                    easing=self._easing(motion_type),
                    metadata={
                        "placement_type": placement.placement_type,
                        "local_path": placement.local_path,
                        "reason": placement.reason,
                    },
                )
            )

        return MotionPlanningResult(
            production_id=production_id,
            motions=motions,
            metadata={
                "runtime": "MotionPlanningRuntime",
                "placement_count": len(placements.placements),
                "motion_count": len(motions),
            },
        )

    def _intensity(self, motion_type: str) -> str:
        if motion_type in {"zoom_in", "pop_zoom", "scale_up"}:
            return "high"

        if motion_type in {"slow_push"}:
            return "medium"

        return "low"

    def _easing(self, motion_type: str) -> str:
        if motion_type in {"zoom_in", "scale_up"}:
            return "ease_out"

        if motion_type in {"slow_push"}:
            return "linear"

        return "ease_in_out"