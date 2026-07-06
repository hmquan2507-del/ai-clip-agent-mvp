from __future__ import annotations

from typing import Any

from app.render.plan.models import RenderPlanStep


class RenderStepBuilder:
    def build_steps_from_instructions(
        self,
        instructions: list[dict[str, Any]],
    ) -> list[RenderPlanStep]:
        steps: list[RenderPlanStep] = []

        for instruction in instructions:
            if not isinstance(instruction, dict):
                continue

            operation = str(instruction.get("operation") or "")
            instruction_type = str(instruction.get("instruction_type") or "generic")

            if not operation:
                continue

            steps.append(
                RenderPlanStep(
                    step_id=f"step_{len(steps)}",
                    step_type=self._step_type_from_instruction_type(
                        instruction_type
                    ),
                    operation=operation,
                    inputs=instruction.get("inputs")
                    if isinstance(instruction.get("inputs"), dict)
                    else {},
                    outputs=instruction.get("outputs")
                    if isinstance(instruction.get("outputs"), dict)
                    else {},
                    parameters=instruction.get("parameters")
                    if isinstance(instruction.get("parameters"), dict)
                    else {},
                    priority=str(instruction.get("priority") or "medium"),
                    start_time=self._safe_float_or_none(
                        instruction.get("start_time")
                    ),
                    end_time=self._safe_float_or_none(
                        instruction.get("end_time")
                    ),
                )
            )

        return steps

    def _step_type_from_instruction_type(
        self,
        instruction_type: str,
    ) -> str:
        if instruction_type in {"decode", "encode"}:
            return instruction_type

        if instruction_type in {
            "camera_motion",
            "video_effect",
            "visual_overlay",
            "transition",
        }:
            return "video"

        if instruction_type == "subtitle":
            return "subtitle"

        if instruction_type in {
            "audio_mix",
            "audio_ducking",
            "audio_mastering",
        }:
            return "audio"

        return "generic"

    def _safe_float_or_none(self, value: Any) -> float | None:
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None