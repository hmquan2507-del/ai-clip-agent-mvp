from __future__ import annotations


TRACK_VIDEO = "video"
TRACK_SUBTITLE = "subtitle"
TRACK_AUDIO = "audio"
TRACK_SFX = "sfx"
TRACK_BROLL = "broll"
TRACK_CAMERA = "camera_motion"
TRACK_TIMELINE = "timeline"
TRACK_GLOBAL = "global"

DEFAULT_TRACKS = [
    TRACK_GLOBAL,
    TRACK_TIMELINE,
    TRACK_VIDEO,
    TRACK_CAMERA,
    TRACK_SUBTITLE,
    TRACK_BROLL,
    TRACK_AUDIO,
    TRACK_SFX,
]


TRACK_TYPE_MAP = {
    TRACK_GLOBAL: "global",
    TRACK_TIMELINE: "timeline",
    TRACK_VIDEO: "video",
    TRACK_CAMERA: "video_effect",
    TRACK_SUBTITLE: "subtitle",
    TRACK_BROLL: "visual_overlay",
    TRACK_AUDIO: "audio",
    TRACK_SFX: "audio_effect",
}