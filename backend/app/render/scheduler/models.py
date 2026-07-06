from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScheduledRenderStep:
    schedule_id: str
    node_id: str
    operation: str
    order_index: int
    can_run_parallel: bool = False
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schedule_id": self.schedule_id,
            "node_id": self.node_id,
            "operation": self.operation,
            "order_index": self.order_index,
            "can_run_parallel": self.can_run_parallel,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "parameters": self.parameters,
        }


@dataclass
class RenderSchedule:
    production_id: str
    steps: list[ScheduledRenderStep] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "steps": [step.to_dict() for step in self.steps],
            "metadata": self.metadata,
        }