from __future__ import annotations

import json

from app.db.enums import SoundEffectType


class SoundEffectEngine:
    def build_from_timeline(self, timeline) -> dict:
        cues: list[dict] = []

        sound_track = next(
            (
                track
                for track in timeline.tracks
                if track.type.value == "sound_effect"
            ),
            None,
        )

        if sound_track is None:
            return {
                "cues": [],
                "metadata": {
                    "source": "timeline",
                    "reason": "No sound effect track found",
                },
            }

        for clip in sound_track.clips:
            metadata = self.loads_metadata(clip.metadata_json)

            cues.append(
                {
                    "start_time": clip.timeline_start,
                    "end_time": clip.timeline_end,
                    "effect_type": self.detect_effect_type(metadata),
                    "prompt": self.build_prompt(metadata),
                    "keyword": self.build_keyword(metadata),
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

    def detect_effect_type(self, metadata: dict) -> SoundEffectType:
        reason = (metadata.get("reason") or "").lower()

        if "transition" in reason:
            return SoundEffectType.TRANSITION

        if "impact" in reason:
            return SoundEffectType.IMPACT

        if "click" in reason:
            return SoundEffectType.CLICK

        if "pop" in reason:
            return SoundEffectType.POP

        if "whoosh" in reason or "swipe" in reason:
            return SoundEffectType.WHOOSH

        if "ambient" in reason or "background" in reason:
            return SoundEffectType.AMBIENT

        return SoundEffectType.CUSTOM

    def build_prompt(self, metadata: dict) -> str:
        reason = metadata.get("reason") or "support the video moment"
        return f"Create a short sound effect to {reason}."

    def build_keyword(self, metadata: dict) -> str:
        reason = metadata.get("reason") or ""

        words = [
            word.strip(".,!?;:").lower()
            for word in reason.split()
            if len(word.strip(".,!?;:")) > 3
        ]

        if not words:
            return "sound-effect"

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