from __future__ import annotations

from app.render.execution.models import (
    RenderGraph,
    RenderGraphIssue,
)


class RenderGraphValidator:
    def validate(
        self,
        graph: RenderGraph,
    ) -> RenderGraph:
        issues: list[RenderGraphIssue] = []
        node_ids: set[str] = set()

        for node in graph.nodes:
            if node.node_id in node_ids:
                issues.append(
                    RenderGraphIssue(
                        level="error",
                        code="duplicate_node_id",
                        message=(
                            "Render graph node IDs must be unique."
                        ),
                        node_id=node.node_id,
                    )
                )
            else:
                node_ids.add(node.node_id)

        for node in graph.nodes:
            for dependency in node.dependencies:
                if dependency not in node_ids:
                    issues.append(
                        RenderGraphIssue(
                            level="error",
                            code="missing_dependency",
                            message=(
                                "Render node dependency "
                                "does not exist."
                            ),
                            node_id=node.node_id,
                            metadata={
                                "dependency": dependency,
                            },
                        )
                    )

                if dependency == node.node_id:
                    issues.append(
                        RenderGraphIssue(
                            level="error",
                            code="self_dependency",
                            message=(
                                "Render node cannot depend "
                                "on itself."
                            ),
                            node_id=node.node_id,
                        )
                    )

        if self._has_cycle(graph):
            issues.append(
                RenderGraphIssue(
                    level="error",
                    code="graph_cycle_detected",
                    message=(
                        "Render graph must be a directed "
                        "acyclic graph."
                    ),
                )
            )

        required_nodes = {
            "prepare_inputs",
            "decode_video",
            "compose_primary_video",
            "encode_video",
            "write_artifacts",
        }

        missing_required = required_nodes.difference(
            node_ids
        )

        for node_id in sorted(missing_required):
            issues.append(
                RenderGraphIssue(
                    level="error",
                    code="required_node_missing",
                    message=(
                        f"Required render node is missing: "
                        f"{node_id}"
                    ),
                    node_id=node_id,
                )
            )

        graph.issues = issues
        graph.metadata = {
            **graph.metadata,
            "issue_count": len(issues),
            "valid": not any(
                issue.level == "error"
                for issue in issues
            ),
        }

        return graph

    def _has_cycle(
        self,
        graph: RenderGraph,
    ) -> bool:
        dependencies = {
            node.node_id: list(node.dependencies)
            for node in graph.nodes
        }

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node_id: str) -> bool:
            if node_id in visiting:
                return True

            if node_id in visited:
                return False

            visiting.add(node_id)

            for dependency in dependencies.get(
                node_id,
                [],
            ):
                if dependency in dependencies:
                    if visit(dependency):
                        return True

            visiting.remove(node_id)
            visited.add(node_id)

            return False

        return any(
            visit(node_id)
            for node_id in dependencies
            if node_id not in visited
        )