from __future__ import annotations

from app.editing.execution.graph.models import ExecutionEdge, ExecutionGraph


class GraphOptimizer:
    def optimize(self, graph: ExecutionGraph) -> ExecutionGraph:
        self._sort_nodes(graph)
        self._remove_orphan_edges(graph)
        self._sort_edges(graph)

        graph.metadata["optimized"] = True
        graph.metadata["optimized_node_count"] = len(graph.nodes)
        graph.metadata["optimized_edge_count"] = len(graph.edges)

        return graph

    def _sort_nodes(self, graph: ExecutionGraph) -> None:
        graph.nodes.sort(
            key=lambda node: (
                node.start_time,
                self._priority_rank(node.priority),
                node.track,
                node.operation,
            )
        )

    def _remove_orphan_edges(self, graph: ExecutionGraph) -> None:
        node_ids = {node.node_id for node in graph.nodes}

        graph.edges = [
            edge
            for edge in graph.edges
            if edge.from_node_id in node_ids and edge.to_node_id in node_ids
        ]

    def _sort_edges(self, graph: ExecutionGraph) -> None:
        graph.edges.sort(
            key=lambda edge: (
                edge.from_node_id,
                edge.to_node_id,
                edge.dependency_type,
            )
        )

    def _priority_rank(self, priority: str) -> int:
        return {
            "high": 0,
            "medium": 1,
            "low": 2,
        }.get(priority, 99)