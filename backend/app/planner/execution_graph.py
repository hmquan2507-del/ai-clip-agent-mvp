from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.planner.models import EditingPlan, PlannerInstructionType


@dataclass
class PlannerExecutionNode:
    node_id: str
    node_type: str
    instruction_index: int
    depends_on: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlannerExecutionGraph:
    production_id: str
    nodes: list[PlannerExecutionNode]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "nodes": [node.__dict__ for node in self.nodes],
            "metadata": self.metadata,
        }


class PlannerExecutionGraphBuilder:
    def build(self, plan: EditingPlan) -> PlannerExecutionGraph:
        nodes: list[PlannerExecutionNode] = []

        for index, instruction in enumerate(plan.instructions):
            node_type = self._node_type_for_instruction(instruction.instruction_type)
            node_id = f"{node_type}_{index}"

            depends_on = []

            if instruction.instruction_type in {
                PlannerInstructionType.BROLL,
                PlannerInstructionType.MUSIC,
                PlannerInstructionType.SOUND_EFFECT,
            }:
                depends_on.append("asset_resolver")

            if instruction.instruction_type in {
                PlannerInstructionType.SUBTITLE_STYLE,
                PlannerInstructionType.FONT,
            }:
                depends_on.append("presentation_runtime")

            nodes.append(
                PlannerExecutionNode(
                    node_id=node_id,
                    node_type=node_type,
                    instruction_index=index,
                    depends_on=depends_on,
                    metadata={
                        "instruction_type": instruction.instruction_type.value,
                        "track_type": instruction.track_type,
                        "start_time": instruction.start_time,
                        "end_time": instruction.end_time,
                    },
                )
            )

        return PlannerExecutionGraph(
            production_id=plan.production_id,
            nodes=nodes,
            metadata={
                "node_count": len(nodes),
                "builder": "PlannerExecutionGraphBuilder",
            },
        )

    def _node_type_for_instruction(
        self,
        instruction_type: PlannerInstructionType,
    ) -> str:
        if instruction_type in {
            PlannerInstructionType.BROLL,
            PlannerInstructionType.MUSIC,
            PlannerInstructionType.SOUND_EFFECT,
        }:
            return "asset_instruction"

        if instruction_type in {
            PlannerInstructionType.SUBTITLE_STYLE,
            PlannerInstructionType.FONT,
        }:
            return "presentation_instruction"

        return "timeline_instruction"