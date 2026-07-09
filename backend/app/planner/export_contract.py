from __future__ import annotations

from app.asset.orchestrator import AssetPlanItem
from app.planner.execution_graph import PlannerExecutionGraph
from app.planner.models import EditingPlan, PlannerInstructionType


class PlannerExportContract:
    def to_asset_plan_items(self, plan: EditingPlan) -> list[AssetPlanItem]:
        items: list[AssetPlanItem] = []

        for instruction in plan.instructions:
            if instruction.instruction_type not in {
                PlannerInstructionType.BROLL,
                PlannerInstructionType.MUSIC,
                PlannerInstructionType.SOUND_EFFECT,
            }:
                continue

            if not instruction.query:
                continue

            items.append(
                AssetPlanItem(
                    query=instruction.query,
                    asset_type=instruction.instruction_type.value,
                    track_type=instruction.track_type or instruction.instruction_type.value,
                    start_time=instruction.start_time,
                    end_time=instruction.end_time,
                    preferred_orientation=instruction.preferred_orientation,
                    preferred_duration=instruction.preferred_duration,
                    layer=instruction.layer,
                    volume=instruction.volume,
                    opacity=instruction.opacity,
                    commercial_use=True,
                    metadata={
                        **instruction.metadata,
                        "planner_reason": instruction.reason,
                        "planner_priority": instruction.priority.value,
                        "planner_confidence": instruction.confidence,
                    },
                )
            )

        return items

    def to_payload(
        self,
        plan: EditingPlan,
        graph: PlannerExecutionGraph,
    ) -> dict:
        return {
            "production_id": plan.production_id,
            "planner_version": plan.planner_version,
            "plan": plan.to_dict(),
            "execution_graph": graph.to_dict(),
            "asset_plan_items": [
                item.__dict__ for item in self.to_asset_plan_items(plan)
            ],
            "metadata": {
                "export_contract": "PlannerExportContract",
            },
        }