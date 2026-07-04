from __future__ import annotations

import json

from app.db.enums import SubtitleStyle


class SubtitleEngine:
    def build_from_timeline(
        self,
        timeline,
        style: SubtitleStyle = SubtitleStyle.DEFAULT,
    ) -> dict:
        cues: list[dict] = []

        subtitle_track = next(
            (
                track
                for track in timeline.tracks
                if track.type.value == "subtitle"
            ),
            None,
        )

        if subtitle_track is None:
            return {
                "style": style,
                "language": "vi",
                "cues": [],
            }

        for clip in subtitle_track.clips:
            cues.append(
                {
                    "start_time": clip.timeline_start,
                    "end_time": clip.timeline_end,
                    "text": clip.text or "",
                    "style_json": self.dumps_style(
                        {
                            "style": style.value,
                        }
                    ),
                }
            )

        return {
            "style": style,
            "language": "vi",
            "cues": cues,
        }

    @staticmethod
    def dumps_style(style_dict: dict | None) -> str | None:
        if style_dict is None:
            return None

        return json.dumps(
            style_dict,
            ensure_ascii=False,
        )