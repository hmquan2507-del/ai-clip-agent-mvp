from __future__ import annotations

from app.editing.composition.models import CompositionLayer


DEFAULT_RENDER_ORDER = [
    "video_base",
    "video_camera_motion",
    "video_broll",
    "video_overlay",
    "video_transition",
    "subtitle_main",
    "audio_voice",
    "audio_music",
    "audio_sfx",
    "audio_ducking",
    "audio_master",
]


class RenderOrderBuilder:
    def build(
        self,
        layers: list[CompositionLayer],
    ) -> list[str]:
        available = {layer.layer_key for layer in layers}

        ordered = [
            key for key in DEFAULT_RENDER_ORDER if key in available
        ]

        remaining = sorted(
            key for key in available if key not in ordered
        )

        return ordered + remaining