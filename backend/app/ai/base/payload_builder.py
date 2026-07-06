from __future__ import annotations

from typing import Any


class ContentGraphPayloadBuilder:
    @staticmethod
    def build(graph: Any) -> dict[str, Any]:
        return {
            "content_graph": {
                "id": str(graph.id),
                "production_id": str(graph.production_id),
                "language": graph.language,
                "summary": graph.summary,
                "topic_json": graph.topic_json,
                "speaker_json": graph.speaker_json,
                "metadata_json": graph.metadata_json,
            },
            "segments": [
                {
                    "id": str(segment.id),
                    "start_time": segment.start_time,
                    "end_time": segment.end_time,
                    "text": segment.text,
                    "type": str(segment.type),
                    "emotion": str(segment.emotion),
                    "topic": segment.topic,
                    "importance_score": segment.importance_score,
                    "viral_potential_score": segment.viral_potential_score,
                    "speaker_id": segment.speaker_id,
                    "order_index": segment.order_index,
                    "metadata_json": segment.metadata_json,
                }
                for segment in graph.segments
            ],
        }