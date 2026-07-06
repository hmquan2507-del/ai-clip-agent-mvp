from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RenderPlanStep:
    step_id: str
    step_type: str
    operation: str
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)
    priority: str = "medium"
    start_time: float | None = None
    end_time: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "step_type": self.step_type,
            "operation": self.operation,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "parameters": self.parameters,
            "priority": self.priority,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }


@dataclass
class RenderPlan:
    production_id: str
    steps: list[RenderPlanStep] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "steps": [step.to_dict() for step in self.steps],
            "metadata": self.metadata,
        }