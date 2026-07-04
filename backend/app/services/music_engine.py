from __future__ import annotations

import json

from app.db.enums import MusicMood


class MusicEngine:
    def build_from_timeline(
        self,
        timeline,
        mood: MusicMood = MusicMood.CUSTOM,
    ) -> dict:
        duration = float(getattr(timeline, "duration_seconds", 0) or 0)

        if duration <= 0:
            duration = self._infer_duration_from_tracks(timeline)

        selected_mood = self._resolve_mood(timeline, mood)

        cue = {
            "start_time": 0.0,
            "end_time": duration,
            "mood": selected_mood,
            "prompt": self._build_prompt(selected_mood, duration),
            "keyword": selected_mood.value,
            "volume": 0.35,
            "fade_in": min(1.5, duration / 4) if duration > 0 else 0,
            "fade_out": min(1.5, duration / 4) if duration > 0 else 0,
            "metadata_json": self.dumps_metadata(
                {
                    "source": "timeline",
                    "duration_seconds": duration,
                    "mood": selected_mood.value,
                }
            ),
        }

        return {
            "mood": selected_mood,
            "cues": [cue] if duration > 0 else [],
            "metadata": {
                "source": "timeline",
                "duration_seconds": duration,
                "cue_count": 1 if duration > 0 else 0,
            },
        }

    def _infer_duration_from_tracks(self, timeline) -> float:
        max_end = 0.0

        for track in timeline.tracks:
            for clip in track.clips:
                max_end = max(max_end, float(clip.timeline_end or 0))

        return max_end

    def _resolve_mood(
        self,
        timeline,
        mood: MusicMood,
    ) -> MusicMood:
        if mood != MusicMood.CUSTOM:
            return mood

        duration = float(getattr(timeline, "duration_seconds", 0) or 0)

        if duration <= 30:
            return MusicMood.ENERGETIC

        if duration <= 90:
            return MusicMood.INSPIRATIONAL

        return MusicMood.CORPORATE

    def _build_prompt(
        self,
        mood: MusicMood,
        duration: float,
    ) -> str:
        return (
            f"Create background music with a {mood.value} mood "
            f"for a {duration:.1f}-second short-form video."
        )

    @staticmethod
    def dumps_metadata(metadata: dict | None) -> str | None:
        if metadata is None:
            return None

        return json.dumps(metadata, ensure_ascii=False)