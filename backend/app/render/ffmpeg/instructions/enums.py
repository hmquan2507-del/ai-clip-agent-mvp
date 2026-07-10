from __future__ import annotations

from enum import StrEnum


class FFmpegInstructionType(StrEnum):
    INPUT = "input"

    TRIM_VIDEO = "trim_video"
    TRIM_AUDIO = "trim_audio"

    SCALE = "scale"
    CROP = "crop"
    SET_PTS = "set_pts"
    SET_AUDIO_PTS = "set_audio_pts"

    OVERLAY = "overlay"
    DRAW_SUBTITLE = "draw_subtitle"

    APPLY_VIDEO_EFFECT = "apply_video_effect"
    APPLY_TRANSITION = "apply_transition"

    VOLUME = "volume"
    AUDIO_DELAY = "audio_delay"
    AUDIO_MIX = "audio_mix"

    CONCAT_VIDEO = "concat_video"
    CONCAT_AUDIO = "concat_audio"

    ENCODE = "encode"
    MAP_OUTPUT = "map_output"


class FFmpegStreamType(StrEnum):
    VIDEO = "video"
    AUDIO = "audio"
    SUBTITLE = "subtitle"
    OUTPUT = "output"


class FFmpegInstructionStatus(StrEnum):
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"