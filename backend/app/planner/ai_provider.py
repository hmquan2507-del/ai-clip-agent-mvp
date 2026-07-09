from __future__ import annotations

from abc import ABC, abstractmethod

from app.planner.models import PlannerContext, PlannerHint, PlannerInstruction, PlannerRequest


class BasePlannerAIProvider(ABC):
    @abstractmethod
    def build_plan(
        self,
        request: PlannerRequest,
        hints: list[PlannerHint],
        prompt: str,
    ) -> list[PlannerInstruction]:
        raise NotImplementedError


class MockPlannerAIProvider(BasePlannerAIProvider):
    def build_plan(
        self,
        request: PlannerRequest,
        hints: list[PlannerHint],
        prompt: str,
    ) -> list[PlannerInstruction]:
        instructions: list[PlannerInstruction] = []

        for hint in hints:
            start_time = hint.start_time
            end_time = hint.end_time

            if start_time is None or end_time is None:
                first_segment = request.segments[0] if request.segments else None
                start_time = first_segment.start_time if first_segment else 0.0
                end_time = first_segment.end_time if first_segment else 5.0

            instructions.append(
                PlannerInstruction(
                    instruction_type=hint.instruction_type,
                    query=hint.query,
                    start_time=start_time,
                    end_time=end_time,
                    priority=hint.priority,
                    reason=hint.reason,
                    track_type=hint.track_type,
                    layer=hint.layer,
                    preferred_duration=hint.preferred_duration,
                    preferred_orientation=hint.preferred_orientation,
                    volume=hint.volume,
                    opacity=hint.opacity,
                    style_key=hint.style_key,
                    font_family=hint.font_family,
                    confidence=0.85,
                    metadata={
                        **hint.metadata,
                        "source": "mock_planner_ai_provider",
                    },
                )
            )

        return instructions