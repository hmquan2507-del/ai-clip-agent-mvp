from __future__ import annotations

from enum import StrEnum


class RenderQualityStatus(StrEnum):
    APPROVED = "approved"
    WARNING = "warning"
    REJECTED = "rejected"


class RenderQualityCheckStatus(StrEnum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    SKIPPED = "skipped"


class RenderQualityCheckType(StrEnum):
    MEDIA_VALIDATION = "media_validation"
    FILE_INTEGRITY = "file_integrity"
    DURATION = "duration"
    RESOLUTION = "resolution"
    FPS = "fps"
    VIDEO_CODEC = "video_codec"
    AUDIO_CODEC = "audio_codec"
    BLACK_FRAME = "black_frame"
    SILENCE = "silence"
    ARTIFACT_INTEGRITY = "artifact_integrity"