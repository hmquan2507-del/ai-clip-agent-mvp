from __future__ import annotations

from typing import Any

from app.editing.execution.graph.models import ExecutionEdge, ExecutionGraph, ExecutionNode


class ExecutionGraphBuilder:
    def build(
        self,
        production_id: str,
        editable_timeline: dict[str, Any],
    ) -> ExecutionGraph:
        nodes = self._build_nodes(editable_timeline)
        edges = self._build_edges(nodes)

        return ExecutionGraph(
            production_id=production_id,
            nodes=nodes,
            edges=edges,
            metadata={
                "builder": "execution_graph_builder",
                "node_count": len(nodes),
                "edge_count": len(edges),
            },
        )

    def _build_nodes(
        self,
        editable_timeline: dict[str, Any],
    ) -> list[ExecutionNode]:
        nodes: list[ExecutionNode] = []

        tracks = editable_timeline.get("tracks", [])
        if not isinstance(tracks, list):
            return nodes

        index = 0

        for track in tracks:
            if not isinstance(track, dict):
                continue

            track_name = str(track.get("name") or "unknown")
            events = track.get("events", [])

            if not isinstance(events, list):
                continue

            for event in events:
                if not isinstance(event, dict):
                    continue

                priority = str(event.get("priority") or "medium")

                node = ExecutionNode(
                    node_id=f"node_{index}",
                    node_type=str(event.get("event_type") or "unknown"),
                    track=str(event.get("track") or track_name),
                    operation=str(event.get("operation") or ""),
                    start_time=self._safe_float(event.get("start_time", 0.0)),
                    end_time=self._safe_float(event.get("end_time", 0.0)),
                    priority=priority,
                    weight=self._priority_weight(priority),
                    parameters=event.get("parameters")
                    if isinstance(event.get("parameters"), dict)
                    else {},
                    source_segment_id=event.get("source_segment_id"),
                    reason=str(event.get("reason") or ""),
                )

                if node.operation:
                    nodes.append(node)
                    index += 1

        return nodes

    def _build_edges(
        self,
        nodes: list[ExecutionNode],
    ) -> list[ExecutionEdge]:
        edges: list[ExecutionEdge] = []

        for source in nodes:
            for target in nodes:
                if source.node_id == target.node_id:
                    continue

                dependency_type = self._detect_dependency(source, target)

                if dependency_type is None:
                    continue

                edges.append(
                    ExecutionEdge(
                        edge_id=f"edge_{len(edges)}",
                        from_node_id=source.node_id,
                        to_node_id=target.node_id,
                        dependency_type=dependency_type,
                        reason=f"{source.operation}_before_{target.operation}",
                    )
                )

        return edges

    def _detect_dependency(
        self,
        source: ExecutionNode,
        target: ExecutionNode,
    ) -> str | None:
        if source.track == "global" and target.track != "global":
            return "global_style_dependency"

        if source.track == "timeline" and target.track != "timeline":
            return "timeline_pacing_dependency"

        if source.track == "subtitle" and target.track == "subtitle":
            if self._overlap(source, target):
                return "same_track_overlap"

        if source.track == "audio" and target.track == "sfx":
            if self._overlap(source, target):
                return "audio_ducking_dependency"

        if source.track == "video" and target.track in {"camera_motion", "broll"}:
            if self._overlap(source, target):
                return "video_effect_dependency"

        if source.track == "broll" and target.track == "camera_motion":
            if self._overlap(source, target):
                return "visual_priority_dependency"

        return None

    def _overlap(
        self,
        left: ExecutionNode,
        right: ExecutionNode,
    ) -> bool:
        return left.start_time < right.end_time and right.start_time < left.end_time

    def _priority_weight(self, priority: str) -> float:
        return {
            "high": 0.90,
            "medium": 0.60,
            "low": 0.30,
        }.get(priority, 0.50)

    def _safe_float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0