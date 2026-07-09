from __future__ import annotations

from app.timeline.camera_movement.models import (
    CameraMovementPlan,
    CameraMovementResult,
)
from app.timeline.motion_planning.models import MotionPlanningResult


class CameraMovementRuntime:
    def build(
        self,
        production_id: str,
        motion_result: MotionPlanningResult,
    ) -> CameraMovementResult:
        movements: list[CameraMovementPlan] = []

        for motion in motion_result.motions:
            movements.append(
                self._movement_from_motion(
                    production_id=production_id,
                    motion=motion,
                )
            )

        return CameraMovementResult(
            production_id=production_id,
            movements=movements,
            metadata={
                "runtime": "CameraMovementRuntime",
                "motion_count": len(motion_result.motions),
                "movement_count": len(movements),
            },
        )

    def _movement_from_motion(
        self,
        production_id: str,
        motion,
    ) -> CameraMovementPlan:
        if motion.motion_type == "zoom_in":
            return CameraMovementPlan(
                segment_id=motion.segment_id,
                target_id=motion.target_id,
                start_time=motion.start_time,
                end_time=motion.end_time,
                movement_type="ken_burns_zoom_in",
                scale_from=1.0,
                scale_to=1.12,
                metadata={
                    **motion.metadata,
                    "source_motion_type": motion.motion_type,
                },
            )

        if motion.motion_type == "slow_push":
            return CameraMovementPlan(
                segment_id=motion.segment_id,
                target_id=motion.target_id,
                start_time=motion.start_time,
                end_time=motion.end_time,
                movement_type="slow_push_in",
                scale_from=1.02,
                scale_to=1.08,
                metadata={
                    **motion.metadata,
                    "source_motion_type": motion.motion_type,
                },
            )

        if motion.motion_type == "scale_up":
            return CameraMovementPlan(
                segment_id=motion.segment_id,
                target_id=motion.target_id,
                start_time=motion.start_time,
                end_time=motion.end_time,
                movement_type="cta_scale_up",
                scale_from=1.0,
                scale_to=1.1,
                metadata={
                    **motion.metadata,
                    "source_motion_type": motion.motion_type,
                },
            )

        return CameraMovementPlan(
            segment_id=motion.segment_id,
            target_id=motion.target_id,
            start_time=motion.start_time,
            end_time=motion.end_time,
            movement_type="static",
            scale_from=1.0,
            scale_to=1.0,
            metadata={
                **motion.metadata,
                "source_motion_type": motion.motion_type,
            },
        )