from __future__ import annotations

from typing import Any


class SubtitleTextResolver:
    def resolve(
        self,
        node: dict[str, Any],
        segments: list[dict[str, Any]],
    ) -> str:
        source_segment_id = node.get("source_segment_id")

        if source_segment_id:
            for segment in segments:
                if str(segment.get("id")) == str(source_segment_id):
                    return str(segment.get("text") or "")

        start_time = self._safe_float(node.get("start_time", 0.0))
        end_time = self._safe_float(node.get("end_time", start_time))

        matched_texts: list[str] = []

        for segment in segments:
            segment_start = self._safe_float(segment.get("start_time", 0.0))
            segment_end = self._safe_float(segment.get("end_time", segment_start))

            if segment_start < end_time and start_time < segment_end:
                text = str(segment.get("text") or "").strip()

                if text:
                    matched_texts.append(text)

        return " ".join(matched_texts).strip()

    def _safe_float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0