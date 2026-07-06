from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TimelineInstruction:
    instruction_type: str
    start_time: float
    end_time: float
    track: str
    operation: str
    parameters: dict[str, Any] = field(default_factory=dict)
    priority: str = "medium"
    reason: str = ""
    source_decision_type: str | None = None
    source_segment_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "instruction_type": self.instruction_type,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "track": self.track,
            "operation": self.operation,
            "parameters": self.parameters,
            "priority": self.priority,
            "reason": self.reason,
            "source_decision_type": self.source_decision_type,
            "source_segment_id": self.source_segment_id,
        }


@dataclass
class ExecutionPlanResult:
    production_id: str
    instructions: list[TimelineInstruction]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "instructions": [item.to_dict() for item in self.instructions],
            "metadata": self.metadata,
        }