from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EditingDecision:
    decision_type: str
    start_time: float
    end_time: float
    priority: str
    target: str
    action: str
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)
    source_segment_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_type": self.decision_type,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "priority": self.priority,
            "target": self.target,
            "action": self.action,
            "reason": self.reason,
            "metadata": self.metadata,
            "source_segment_id": self.source_segment_id,
        }


@dataclass
class DecisionEngineResult:
    production_id: str
    decisions: list[EditingDecision]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "decisions": [decision.to_dict() for decision in self.decisions],
            "metadata": self.metadata,
        }