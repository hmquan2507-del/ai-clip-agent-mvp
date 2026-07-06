from __future__ import annotations

from typing import Any

from app.editing.track.models import TrackContext, TrackNode


class TrackContextLoader:
    def load(
        self,
        production_id: str,
        payload: dict[str, Any],
    ) -> TrackContext:
        context = TrackContext(production_id=production_id)

        context.global_nodes = self._load_nodes(payload.get("global_nodes"))
        context.timeline_nodes = self._load_nodes(payload.get("timeline_nodes"))
        context.video_nodes = self._load_nodes(payload.get("video_nodes"))
        context.camera_nodes = self._load_nodes(payload.get("camera_nodes"))
        context.subtitle_nodes = self._load_nodes(payload.get("subtitle_nodes"))
        context.broll_nodes = self._load_nodes(payload.get("broll_nodes"))
        context.audio_nodes = self._load_nodes(payload.get("audio_nodes"))
        context.sfx_nodes = self._load_nodes(payload.get("sfx_nodes"))
        context.music_nodes = self._load_nodes(payload.get("music_nodes"))
        custom_nodes = payload.get("custom_nodes", {})
        if isinstance(custom_nodes, dict):
            context.custom_nodes = {
                key: self._load_nodes(value)
                for key, value in custom_nodes.items()
            }

        metadata = payload.get("metadata", {})
        context.metadata = metadata if isinstance(metadata, dict) else {}

        return context

    def _load_nodes(self, value: Any) -> list[TrackNode]:
        if not isinstance(value, list):
            return []

        nodes: list[TrackNode] = []

        for item in value:
            if not isinstance(item, dict):
                continue

            operation = str(item.get("operation") or "")
            if not operation:
                continue

            nodes.append(
                TrackNode(
                    node_id=str(item.get("node_id") or ""),
                    node_type=str(item.get("node_type") or "unknown"),
                    track=str(item.get("track") or "custom"),
                    operation=operation,
                    start_time=self._safe_float(item.get("start_time", 0.0)),
                    end_time=self._safe_float(item.get("end_time", 0.0)),
                    priority=str(item.get("priority") or "medium"),
                    weight=self._safe_float(item.get("weight", 0.5)),
                    parameters=item.get("parameters")
                    if isinstance(item.get("parameters"), dict)
                    else {},
                    source_segment_id=item.get("source_segment_id"),
                    reason=str(item.get("reason") or ""),
                )
            )

        return nodes

    def _safe_float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0