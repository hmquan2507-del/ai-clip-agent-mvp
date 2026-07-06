from __future__ import annotations

from typing import Any

from app.ai.base.base_engine import BaseAIEngine
from app.ai.execution.instruction_builder import InstructionBuilder
from app.ai.execution.models import ExecutionPlanResult, TimelineInstruction
from app.ai.runtime.ai_context import AIContext


class EditingExecutionPlanner(BaseAIEngine):
    engine_name = "rule_based_editing_execution_planner"

    def __init__(self, max_instructions: int = 120):
        self.max_instructions = max_instructions
        self.builder = InstructionBuilder()

    def run(self, context: AIContext) -> ExecutionPlanResult:
        decision_result = context.get_runtime_result("decision_engine", {})
        decisions = self._safe_list(decision_result.get("decisions"))

        instructions: list[TimelineInstruction] = []

        for decision in decisions:
            instructions.extend(self.builder.build(decision))

        instructions = self._deduplicate(instructions)
        instructions = self._sort(instructions)

        return ExecutionPlanResult(
            production_id=context.production_id,
            instructions=instructions[: self.max_instructions],
            metadata={
                "engine": self.engine_name,
                "total_decisions": len(decisions),
                "total_instructions": len(instructions),
                "max_instructions": self.max_instructions,
                "used_context": {
                    "has_decision_engine": bool(decision_result),
                },
            },
        )

    def _safe_list(self, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []

        return [item for item in value if isinstance(item, dict)]

    def _sort(
        self,
        instructions: list[TimelineInstruction],
    ) -> list[TimelineInstruction]:
        priority_order = {
            "high": 0,
            "medium": 1,
            "low": 2,
        }

        return sorted(
            instructions,
            key=lambda item: (
                item.start_time,
                priority_order.get(item.priority, 99),
                item.track,
                item.operation,
            ),
        )

    def _deduplicate(
        self,
        instructions: list[TimelineInstruction],
    ) -> list[TimelineInstruction]:
        seen: set[tuple[str, float, float, str, str | None]] = set()
        unique: list[TimelineInstruction] = []

        for item in instructions:
            key = (
                item.operation,
                round(item.start_time, 2),
                round(item.end_time, 2),
                item.track,
                item.source_segment_id,
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(item)

        return unique