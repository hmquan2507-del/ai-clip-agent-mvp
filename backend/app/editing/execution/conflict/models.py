from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Conflict:
    conflict_id: str
    conflict_type: str
    severity: str
    left_node_id: str
    right_node_id: str | None = None
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "conflict_type": self.conflict_type,
            "severity": self.severity,
            "left_node_id": self.left_node_id,
            "right_node_id": self.right_node_id,
            "reason": self.reason,
            "metadata": self.metadata,
        }


@dataclass
class ConflictResolution:
    conflict_id: str
    action: str
    target_node_id: str | None = None
    replacement_node_id: str | None = None
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "action": self.action,
            "target_node_id": self.target_node_id,
            "replacement_node_id": self.replacement_node_id,
            "reason": self.reason,
            "metadata": self.metadata,
        }