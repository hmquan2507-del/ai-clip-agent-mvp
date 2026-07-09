from __future__ import annotations

from dataclasses import replace

from app.planner.models import EditingPlan, PlannerInstruction, PlannerInstructionType


class PlannerDiversityGuard:
    def apply(self, plan: EditingPlan) -> EditingPlan:
        kept: list[PlannerInstruction] = []
        seen_query_slots: set[tuple[str, str, int, int]] = set()

        for instruction in plan.instructions:
            if instruction.instruction_type not in {
                PlannerInstructionType.BROLL,
                PlannerInstructionType.MUSIC,
                PlannerInstructionType.SOUND_EFFECT,
            }:
                kept.append(instruction)
                continue

            key = self._dedup_key(instruction)

            if key in seen_query_slots:
                continue

            seen_query_slots.add(key)

            kept.append(
                self._diversify_query_if_needed(
                    instruction=instruction,
                    existing=kept,
                )
            )

        return EditingPlan(
            production_id=plan.production_id,
            planner_version=plan.planner_version,
            instructions=kept,
            metadata={
                **plan.metadata,
                "diversity_guard": "PlannerDiversityGuard",
                "original_instruction_count": len(plan.instructions),
                "deduped_instruction_count": len(kept),
                "removed_instruction_count": len(plan.instructions) - len(kept),
            },
        )

    def _dedup_key(
        self,
        instruction: PlannerInstruction,
    ) -> tuple[str, str, int, int]:
        query = (instruction.query or "").strip().lower()
        instruction_type = instruction.instruction_type.value
        start_bucket = int(instruction.start_time)
        end_bucket = int(instruction.end_time)

        return (
            instruction_type,
            query,
            start_bucket,
            end_bucket,
        )

    def _diversify_query_if_needed(
        self,
        instruction: PlannerInstruction,
        existing: list[PlannerInstruction],
    ) -> PlannerInstruction:
        if instruction.instruction_type != PlannerInstructionType.BROLL:
            return instruction

        if not instruction.query:
            return instruction

        same_query_count = sum(
            1
            for item in existing
            if item.instruction_type == PlannerInstructionType.BROLL
            and (item.query or "").strip().lower()
            == instruction.query.strip().lower()
        )

        if same_query_count == 0:
            return instruction

        alternatives = [
            "creator working on laptop",
            "office worker using computer",
            "person editing video timeline",
            "content creator workspace",
            "artificial intelligence technology interface",
        ]

        alternative = alternatives[same_query_count % len(alternatives)]

        return replace(
            instruction,
            query=alternative,
            metadata={
                **instruction.metadata,
                "diversity_query_rewrite": True,
                "original_query": instruction.query,
                "rewritten_query": alternative,
            },
        )