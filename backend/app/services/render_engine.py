from __future__ import annotations

import json

from app.db.enums import RenderAssetType, RenderTrackType


class RenderEngine:
    def build(
        self,
        timeline,
        subtitle=None,
        broll_plan=None,
        sound_effect_plan=None,
        music_plan=None,
    ) -> dict:
        tracks: list[dict] = []

        duration = float(getattr(timeline, "duration_seconds", 0) or 0)

        tracks.append(self._build_video_track(timeline))

        if subtitle is not None:
            tracks.append(self._build_subtitle_track(subtitle))

        if broll_plan is not None:
            tracks.append(self._build_broll_track(broll_plan))

        if sound_effect_plan is not None:
            tracks.append(self._build_sound_effect_track(sound_effect_plan))

        if music_plan is not None:
            tracks.append(self._build_music_track(music_plan))

        return {
            "duration_seconds": duration,
            "tracks": tracks,
            "metadata": {
                "source": "render_engine",
                "has_subtitle": subtitle is not None,
                "has_broll": broll_plan is not None,
                "has_sound_effect": sound_effect_plan is not None,
                "has_music": music_plan is not None,
            },
        }

    def _build_video_track(self, timeline) -> dict:
        video_track = next(
            (track for track in timeline.tracks if track.type.value == "video"),
            None,
        )

        assets = []

        if video_track is not None:
            for clip in video_track.clips:
                assets.append(
                    {
                        "type": RenderAssetType.SOURCE_VIDEO,
                        "start_time": clip.timeline_start,
                        "end_time": clip.timeline_end,
                        "source_start": clip.source_start,
                        "source_end": clip.source_end,
                        "asset_id": clip.asset_id,
                        "metadata": self.loads_json(clip.metadata_json),
                    }
                )

        return {
            "type": RenderTrackType.VIDEO,
            "name": "Video",
            "position": 0,
            "assets": assets,
        }

    def _build_subtitle_track(self, subtitle) -> dict:
        assets = [
            {
                "type": RenderAssetType.SUBTITLE,
                "start_time": cue.start_time,
                "end_time": cue.end_time,
                "text": cue.text,
                "metadata": self.loads_json(cue.style_json),
            }
            for cue in subtitle.cues
        ]

        return {
            "type": RenderTrackType.SUBTITLE,
            "name": "Subtitles",
            "position": 1,
            "assets": assets,
        }

    def _build_broll_track(self, broll_plan) -> dict:
        assets = [
            {
                "type": RenderAssetType.BROLL,
                "start_time": cue.start_time,
                "end_time": cue.end_time,
                "asset_id": cue.asset_id,
                "prompt": cue.prompt,
                "metadata": {
                    "keyword": cue.keyword,
                    "reason": cue.reason,
                    "source_type": cue.source_type.value,
                    "extra": self.loads_json(cue.metadata_json),
                },
            }
            for cue in broll_plan.cues
        ]

        return {
            "type": RenderTrackType.BROLL,
            "name": "B-roll",
            "position": 2,
            "assets": assets,
        }

    def _build_sound_effect_track(self, sound_effect_plan) -> dict:
        assets = [
            {
                "type": RenderAssetType.SOUND_EFFECT,
                "start_time": cue.start_time,
                "end_time": cue.end_time,
                "asset_id": cue.asset_id,
                "prompt": cue.prompt,
                "metadata": {
                    "keyword": cue.keyword,
                    "reason": cue.reason,
                    "effect_type": cue.effect_type.value,
                    "extra": self.loads_json(cue.metadata_json),
                },
            }
            for cue in sound_effect_plan.cues
        ]

        return {
            "type": RenderTrackType.SOUND_EFFECT,
            "name": "Sound Effects",
            "position": 3,
            "assets": assets,
        }

    def _build_music_track(self, music_plan) -> dict:
        assets = [
            {
                "type": RenderAssetType.MUSIC,
                "start_time": cue.start_time,
                "end_time": cue.end_time,
                "asset_id": cue.asset_id,
                "prompt": cue.prompt,
                "metadata": {
                    "keyword": cue.keyword,
                    "mood": cue.mood.value,
                    "volume": cue.volume,
                    "fade_in": cue.fade_in,
                    "fade_out": cue.fade_out,
                    "extra": self.loads_json(cue.metadata_json),
                },
            }
            for cue in music_plan.cues
        ]

        return {
            "type": RenderTrackType.MUSIC,
            "name": "Background Music",
            "position": 4,
            "assets": assets,
        }

    @staticmethod
    def dumps_json(data: dict | None) -> str | None:
        if data is None:
            return None

        return json.dumps(data, ensure_ascii=False)

    @staticmethod
    def loads_json(data: str | None) -> dict:
        if not data:
            return {}

        try:
            result = json.loads(data)
        except Exception:
            return {}

        return result if isinstance(result, dict) else {}