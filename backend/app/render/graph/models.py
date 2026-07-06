from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RenderGraphNode:
    node_id: str
    node_type: str
    operation: str
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)
    priority: str = "medium"

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "operation": self.operation,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "parameters": self.parameters,
            "priority": self.priority,
        }


@dataclass
class RenderGraphEdge:
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
class RenderGraph:
    production_id: str
    nodes: list[RenderGraphNode] = field(default_factory=list)
    edges: list[RenderGraphEdge] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "metadata": self.metadata,
        }