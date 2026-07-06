from __future__ import annotations

from typing import Any


class SegmentLoader:
    def build_segments(self, graph: Any) -> list[dict[str, Any]]:
        segments: list[dict[str, Any]] = []

        for segment in getattr(graph, "segments", []) or []:
            segments.append(
                {
                    "id": str(segment.id),
                    "start_time": segment.start_time,
                    "end_time": segment.end_time,
                    "text": segment.text,
                    "topic": segment.topic,
                    "importance_score": segment.importance_score,
                    "viral_potential_score": segment.viral_potential_score,
                    "order_index": segment.order_index,
                }
            )

        return segments