from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionNode:
    node_id: str
    node_type: str
    track: str
    operation: str
    start_time: float
    end_time: float
    priority: str = "medium"
    weight: float = 0.5
    parameters: dict[str, Any] = field(default_factory=dict)
    source_segment_id: str | None = None
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "track": self.track,
            "operation": self.operation,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "priority": self.priority,
            "weight": self.weight,
            "parameters": self.parameters,
            "source_segment_id": self.source_segment_id,
            "reason": self.reason,
        }


@dataclass
class ExecutionEdge:
    edge_id: str
    from_node_id: str
    to_node_id: str
    dependency_type: str
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "from_node_id": self.from_node_id,
            "to_node_id": self.to_node_id,
            "dependency_type": self.dependency_type,
            "reason": self.reason,
        }


@dataclass
class ExecutionGraph:
    production_id: str
    nodes: list[ExecutionNode] = field(default_factory=list)
    edges: list[ExecutionEdge] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "metadata": self.metadata,
        }