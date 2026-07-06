from __future__ import annotations

from typing import Any

from app.render.plan.models import RenderPlan
from app.render.plan.render_step_builder import RenderStepBuilder


class RenderPlanBuilder:
    def __init__(self):
        self.step_builder = RenderStepBuilder()

    def build(
        self,
        production_id: str,
        render_instructions: dict[str, Any],
    ) -> RenderPlan:
        instructions = render_instructions.get("instructions", [])

        if not isinstance(instructions, list):
            instructions = []

        steps = self.step_builder.build_steps_from_instructions(
            instructions=[
                instruction
                for instruction in instructions
                if isinstance(instruction, dict)
            ]
        )

        return RenderPlan(
            production_id=production_id,
            steps=steps,
            metadata={
                "builder": "render_plan_builder",
                "source": "render_instructions",
                "instruction_count": len(instructions),
                "step_count": len(steps),
                "has_decode_step": any(
                    step.operation == "decode_source_video"
                    for step in steps
                ),
                "has_encode_step": any(
                    step.operation == "encode_output"
                    for step in steps
                ),
            },
        )