from __future__ import annotations

from typing import Any

from app.editing.track.models import TrackNode


class TrackClassifier:
    def classify(self, node: dict[str, Any]) -> str:
        track = str(node.get("track") or "").strip()

        if track:
            return track

        node_type = str(node.get("node_type") or "").strip()
        operation = str(node.get("operation") or "").strip()

        if node_type == "subtitle" or "subtitle" in operation:
            return "subtitle"

        if node_type == "camera_motion" or "zoom" in operation:
            return "camera_motion"

        if node_type == "broll" or "broll" in operation:
            return "broll"

        if node_type == "audio_sfx" or "sound" in operation or "sfx" in operation:
            return "sfx"

        if node_type == "timeline_pacing" or "pacing" in operation:
            return "timeline"

        if node_type == "global_style":
            return "global"
        
        if node_type == "music" or "music" in operation:
            return "music"
        
        return "custom"
       
        
    def to_track_node(self, node: dict[str, Any]) -> TrackNode | None:
        operation = str(node.get("operation") or "")

        if not operation:
            return None

        return TrackNode(
            node_id=str(node.get("node_id") or ""),
            node_type=str(node.get("node_type") or "unknown"),
            track=self.classify(node),
            operation=operation,
            start_time=self._safe_float(node.get("start_time", 0.0)),
            end_time=self._safe_float(node.get("end_time", 0.0)),
            priority=str(node.get("priority") or "medium"),
            weight=self._safe_float(node.get("weight", 0.5)),
            parameters=node.get("parameters")
            if isinstance(node.get("parameters"), dict)
            else {},
            source_segment_id=node.get("source_segment_id"),
            reason=str(node.get("reason") or ""),
        )

    def _safe_float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0