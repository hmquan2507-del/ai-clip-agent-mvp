from __future__ import annotations

from app.editing.execution.conflict.conflict_rules import ConflictRules
from app.editing.execution.conflict.models import Conflict, ConflictResolution
from app.editing.execution.graph.models import ExecutionGraph


class ConflictResolver:
    def __init__(self):
        self.rules = ConflictRules()

    def resolve(
        self,
        graph: ExecutionGraph,
        conflicts: list[Conflict],
    ) -> tuple[ExecutionGraph, list[ConflictResolution]]:
        resolutions: list[ConflictResolution] = []
        removed_node_ids: set[str] = set()

        for conflict in conflicts:
            resolution = self.rules.resolve(graph, conflict)
            resolutions.append(resolution)

            if resolution.action == "remove_node" and resolution.target_node_id:
                removed_node_ids.add(resolution.target_node_id)

        graph.nodes = [
            node for node in graph.nodes if node.node_id not in removed_node_ids
        ]

        graph.edges = [
            edge
            for edge in graph.edges
            if edge.from_node_id not in removed_node_ids
            and edge.to_node_id not in removed_node_ids
        ]

        return graph, resolutions