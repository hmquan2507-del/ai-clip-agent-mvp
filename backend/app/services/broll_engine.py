from __future__ import annotations

import json


class BrollEngine:
    def build_from_timeline(self, timeline) -> dict:
        cues: list[dict] = []

        broll_track = next(
            (
                track
                for track in timeline.tracks
                if track.type.value == "broll"
            ),
            None,
        )

        if broll_track is None:
            return {
                "cues": [],
                "metadata": {
                    "source": "timeline",
                    "reason": "No B-roll track found",
                },
            }

        for clip in broll_track.clips:
            metadata = self.loads_metadata(clip.metadata_json)

            cues.append(
                {
                    "start_time": clip.timeline_start,
                    "end_time": clip.timeline_end,
                    "prompt": self._build_prompt(metadata),
                    "keyword": self._build_keyword(metadata),
                    "reason": metadata.get("reason"),
                    "metadata_json": self.dumps_metadata(metadata),
                }
            )

        return {
            "cues": cues,
            "metadata": {
                "source": "timeline",
                "count": len(cues),
            },
        }

    def _build_prompt(self, metadata: dict) -> str:
        reason = metadata.get("reason") or "support the main content visually"
        return f"Create relevant B-roll footage to {reason}."

    def _build_keyword(self, metadata: dict) -> str:
        reason = metadata.get("reason") or ""
        words = [
            word.strip(".,!?;:").lower()
            for word in reason.split()
            if len(word.strip(".,!?;:")) > 3
        ]

        if not words:
            return "b-roll"

        return words[0]

    @staticmethod
    def loads_metadata(metadata_json: str | None) -> dict:
        if not metadata_json:
            return {}

        try:
            result = json.loads(metadata_json)
        except Exception:
            return {}

        return result if isinstance(result, dict) else {}

    @staticmethod
    def dumps_metadata(metadata: dict | None) -> str | None:
        if metadata is None:
            return None

        return json.dumps(metadata, ensure_ascii=False)