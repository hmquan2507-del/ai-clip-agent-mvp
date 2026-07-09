from __future__ import annotations

from app.planner.models import EditingPlan, PlannerInstruction, PlannerInstructionType


class PlannerOptimizer:
    def __init__(
        self,
        max_broll_per_time_bucket: int = 1,
        time_bucket_seconds: float = 4.0,
    ):
        self.max_broll_per_time_bucket = max_broll_per_time_bucket
        self.time_bucket_seconds = time_bucket_seconds

    def optimize(
        self,
        plan: EditingPlan,
    ) -> EditingPlan:
        optimized: list[PlannerInstruction] = []
        broll_bucket_counts: dict[int, int] = {}

        for instruction in plan.instructions:
            if instruction.instruction_type != PlannerInstructionType.BROLL:
                optimized.append(instruction)
                continue

            bucket = self._bucket(instruction.start_time)
            current_count = broll_bucket_counts.get(bucket, 0)

            if current_count >= self.max_broll_per_time_bucket:
                continue

            broll_bucket_counts[bucket] = current_count + 1
            optimized.append(instruction)

        optimized = self._sort_timeline_order(optimized)

        return EditingPlan(
            production_id=plan.production_id,
            planner_version=plan.planner_version,
            instructions=optimized,
            metadata={
                **plan.metadata,
                "optimizer": "PlannerOptimizer",
                "optimizer_original_instruction_count": len(plan.instructions),
                "optimizer_instruction_count": len(optimized),
                "optimizer_removed_instruction_count": len(plan.instructions) - len(optimized),
                "max_broll_per_time_bucket": self.max_broll_per_time_bucket,
                "time_bucket_seconds": self.time_bucket_seconds,
            },
        )

    def _bucket(
        self,
        start_time: float,
    ) -> int:
        return int(start_time // self.time_bucket_seconds)

    def _sort_timeline_order(
        self,
        instructions: list[PlannerInstruction],
    ) -> list[PlannerInstruction]:
        return sorted(
            instructions,
            key=lambda item: (
                item.start_time,
                item.layer,
                item.instruction_type.value,
            ),
        )