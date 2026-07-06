from __future__ import annotations

from app.render.graph.models import RenderGraph


class RenderGraphValidator:
    def validate(self, graph: RenderGraph) -> list[str]:
        errors: list[str] = []

        node_ids = {node.node_id for node in graph.nodes}

        if not graph.nodes:
            errors.append("render_graph_has_no_nodes")

        if not any(node.operation == "decode_source_video" for node in graph.nodes):
            errors.append("decode_node_missing")

        if not any(node.operation == "encode_output" for node in graph.nodes):
            errors.append("encode_node_missing")

        for edge in graph.edges:
            if edge.from_node_id not in node_ids:
                errors.append(f"missing_from_node:{edge.from_node_id}")

            if edge.to_node_id not in node_ids:
                errors.append(f"missing_to_node:{edge.to_node_id}")

        if self._has_cycle(graph):
            errors.append("render_graph_has_cycle")

        return errors

    def _has_cycle(self, graph: RenderGraph) -> bool:
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

        for node in graph.nodes:
            if visit(node.node_id):
                return True

        return False