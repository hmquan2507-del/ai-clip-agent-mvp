from __future__ import annotations

from typing import Any

from app.render.graph.models import RenderGraph, RenderGraphEdge, RenderGraphNode


class RenderGraphBuilder:
    def build(
        self,
        production_id: str,
        render_plan: dict[str, Any],
    ) -> RenderGraph:
        nodes = self._build_nodes(render_plan)
        edges = self._build_edges(nodes)

        return RenderGraph(
            production_id=production_id,
            nodes=nodes,
            edges=edges,
            metadata={
                "builder": "render_graph_builder",
                "node_count": len(nodes),
                "edge_count": len(edges),
            },
        )

    def _build_nodes(
        self,
        render_plan: dict[str, Any],
    ) -> list[RenderGraphNode]:
        nodes: list[RenderGraphNode] = []

        steps = render_plan.get("steps", [])
        if not isinstance(steps, list):
            return nodes

        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                continue

            operation = str(step.get("operation") or "")

            if not operation:
                continue

            nodes.append(
                RenderGraphNode(
                    node_id=f"render_node_{index}",
                    node_type=str(step.get("step_type") or "generic"),
                    operation=operation,
                    inputs=step.get("inputs")
                    if isinstance(step.get("inputs"), dict)
                    else {},
                    outputs=step.get("outputs")
                    if isinstance(step.get("outputs"), dict)
                    else {},
                    parameters=step.get("parameters")
                    if isinstance(step.get("parameters"), dict)
                    else {},
                    priority=str(step.get("priority") or "medium"),
                )
            )

        return nodes

    def _build_edges(
        self,
        nodes: list[RenderGraphNode],
    ) -> list[RenderGraphEdge]:
        edges: list[RenderGraphEdge] = []

        decode_nodes = [
            node for node in nodes if node.operation == "decode_source_video"
        ]
        encode_nodes = [
            node for node in nodes if node.operation == "encode_output"
        ]

        decode_node = decode_nodes[0] if decode_nodes else None
        encode_node = encode_nodes[0] if encode_nodes else None

        for node in nodes:
            if decode_node and node.node_id != decode_node.node_id:
                if node.operation != "encode_output":
                    edges.append(
                        self._edge(
                            index=len(edges),
                            from_node_id=decode_node.node_id,
                            to_node_id=node.node_id,
                            dependency_type="decode_dependency",
                            reason="all_render_steps_require_decoded_source",
                        )
                    )

            if encode_node and node.node_id != encode_node.node_id:
                if node.operation != "decode_source_video":
                    edges.append(
                        self._edge(
                            index=len(edges),
                            from_node_id=node.node_id,
                            to_node_id=encode_node.node_id,
                            dependency_type="encode_dependency",
                            reason="encode_requires_all_render_outputs",
                        )
                    )

        edges.extend(
            self._build_type_dependencies(
                nodes=nodes,
                start_index=len(edges),
            )
        )

        return self._deduplicate_edges(edges)

    def _build_type_dependencies(
        self,
        nodes: list[RenderGraphNode],
        start_index: int,
    ) -> list[RenderGraphEdge]:
        edges: list[RenderGraphEdge] = []
        index = start_index

        video_nodes = [
            node
            for node in nodes
            if node.node_type == "video"
        ]
        subtitle_nodes = [
            node
            for node in nodes
            if node.node_type == "subtitle"
        ]
        audio_nodes = [
            node
            for node in nodes
            if node.node_type == "audio"
        ]

        for video_node in video_nodes:
            for subtitle_node in subtitle_nodes:
                edges.append(
                    self._edge(
                        index=index,
                        from_node_id=video_node.node_id,
                        to_node_id=subtitle_node.node_id,
                        dependency_type="video_before_subtitle",
                        reason="subtitle_composited_on_video",
                    )
                )
                index += 1

        for audio_node in audio_nodes:
            for video_node in video_nodes:
                if audio_node.operation in {
                    "apply_audio_ducking",
                    "apply_audio_mastering",
                }:
                    continue

                edges.append(
                    self._edge(
                        index=index,
                        from_node_id=audio_node.node_id,
                        to_node_id=video_node.node_id,
                        dependency_type="audio_sync_dependency",
                        reason="audio_must_align_with_video_timeline",
                    )
                )
                index += 1

        return edges

    def _edge(
        self,
        index: int,
        from_node_id: str,
        to_node_id: str,
        dependency_type: str,
        reason: str,
    ) -> RenderGraphEdge:
        return RenderGraphEdge(
            edge_id=f"render_edge_{index}",
            from_node_id=from_node_id,
            to_node_id=to_node_id,
            dependency_type=dependency_type,
            reason=reason,
        )

    def _deduplicate_edges(
        self,
        edges: list[RenderGraphEdge],
    ) -> list[RenderGraphEdge]:
        seen: set[tuple[str, str, str]] = set()
        unique: list[RenderGraphEdge] = []

        for edge in edges:
            key = (
                edge.from_node_id,
                edge.to_node_id,
                edge.dependency_type,
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(edge)

        for index, edge in enumerate(unique):
            edge.edge_id = f"render_edge_{index}"

        return unique