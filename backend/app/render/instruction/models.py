from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RenderInstruction:
    instruction_id: str
    instruction_type: str
    operation: str
    layer_key: str | None = None
    layer_type: str | None = None
    track_key: str | None = None
    start_time: float | None = None
    end_time: float | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    priority: str = "medium"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "instruction_id": self.instruction_id,
            "instruction_type": self.instruction_type,
            "operation": self.operation,
            "layer_key": self.layer_key,
            "layer_type": self.layer_type,
            "track_key": self.track_key,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "parameters": self.parameters,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "priority": self.priority,
            "metadata": self.metadata,
        }


@dataclass
class RenderInstructionSet:
    production_id: str
    instructions: list[RenderInstruction] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "instructions": [
                instruction.to_dict() for instruction in self.instructions
            ],
            "metadata": self.metadata,
        }