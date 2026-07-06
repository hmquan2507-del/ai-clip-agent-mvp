from __future__ import annotations

from app.editing.execution.graph.models import ExecutionGraph


class DependencyResolver:
    def validate(self, graph: ExecutionGraph) -> list[str]:
        errors: list[str] = []

        node_ids = {node.node_id for node in graph.nodes}

        for edge in graph.edges:
            if edge.from_node_id not in node_ids:
                errors.append(f"missing_from_node:{edge.from_node_id}")

            if edge.to_node_id not in node_ids:
                errors.append(f"missing_to_node:{edge.to_node_id}")

        if self._has_cycle(graph):
            errors.append("execution_graph_has_cycle")

        return errors

    def _has_cycle(self, graph: ExecutionGraph) -> bool:
        adjacency: dict[str, list[str]] = {}

        for edge in graph.edges:
            adjacency.setdefault(edge.from_node_id, []).append(edge.to_node_id)

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node_id: str) -> bool:
            if node_id in visiting:
                return True

            if node_id in visited:
                return False

            visiting.add(node_id)

            for next_node in adjacency.get(node_id, []):
                if visit(next_node):
                    return True

            visiting.remove(node_id)
            visited.add(node_id)

            return False

        return any(visit(node.node_id) for node in graph.nodes)