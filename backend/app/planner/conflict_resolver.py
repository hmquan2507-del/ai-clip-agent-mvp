from __future__ import annotations

from dataclasses import replace

from app.planner.models import EditingPlan, PlannerInstruction, PlannerInstructionType


class PlannerConflictResolver:
    def resolve(self, plan: EditingPlan) -> EditingPlan:
        resolved: list[PlannerInstruction] = []

        sorted_items = sorted(
            plan.instructions,
            key=lambda item: (
                item.start_time,
                item.layer,
                item.instruction_type.value,
            ),
        )

        for instruction in sorted_items:
            instruction = self._fix_track_type(instruction)
            instruction = self._fix_layer(instruction)

            if self._has_same_track_overlap(resolved, instruction):
                instruction = replace(
                    instruction,
                    layer=instruction.layer + 1,
                    metadata={
                        **instruction.metadata,
                        "conflict_resolved": True,
                        "conflict_strategy": "layer_increment",
                    },
                )

            resolved.append(instruction)

        return EditingPlan(
            production_id=plan.production_id,
            planner_version=plan.planner_version,
            instructions=resolved,
            metadata={
                **plan.metadata,
                "conflict_resolver": "PlannerConflictResolver",
                "resolved_instruction_count": len(resolved),
            },
        )

    def _fix_track_type(self, instruction: PlannerInstruction) -> PlannerInstruction:
        if instruction.track_type:
            return instruction

        mapping = {
            PlannerInstructionType.BROLL: "broll",
            PlannerInstructionType.MUSIC: "music",
            PlannerInstructionType.SOUND_EFFECT: "sfx",
            PlannerInstructionType.SUBTITLE_STYLE: "subtitle",
            PlannerInstructionType.FONT: "subtitle",
            PlannerInstructionType.MOTION: "motion",
            PlannerInstructionType.TRANSITION: "transition",
            PlannerInstructionType.CTA: "cta",
            PlannerInstructionType.STICKER: "sticker",
        }

        return replace(
            instruction,
            track_type=mapping.get(instruction.instruction_type),
        )

    def _fix_layer(self, instruction: PlannerInstruction) -> PlannerInstruction:
        if instruction.layer > 0:
            return instruction

        return replace(instruction, layer=1)

    def _has_same_track_overlap(
        self,
        existing: list[PlannerInstruction],
        item: PlannerInstruction,
    ) -> bool:
        for other in existing:
            if other.track_type != item.track_type:
                continue

            if other.layer != item.layer:
                continue

            if self._overlaps(other, item):
                return True

        return False

    def _overlaps(
        self,
        left: PlannerInstruction,
        right: PlannerInstruction,
    ) -> bool:
        return left.start_time < right.end_time and right.start_time < left.end_time