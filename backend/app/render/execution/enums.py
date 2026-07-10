from __future__ import annotations

from enum import StrEnum


class RenderNodeStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class RenderStage(StrEnum):
    PREPARE = "prepare"
    DECODE = "decode"
    VIDEO = "video"
    AUDIO = "audio"
    SUBTITLE = "subtitle"
    EFFECT = "effect"
    ENCODE = "encode"
    FINALIZE = "finalize"


class RenderNodeType(StrEnum):
    PREPARE_INPUTS = "prepare_inputs"
    DECODE_VIDEO = "decode_video"
    DECODE_AUDIO = "decode_audio"
    COMPOSE_PRIMARY_VIDEO = "compose_primary_video"
    OVERLAY_BROLL = "overlay_broll"
    APPLY_EFFECTS = "apply_effects"
    APPLY_TRANSITIONS = "apply_transitions"
    DRAW_SUBTITLES = "draw_subtitles"
    MIX_AUDIO = "mix_audio"
    ENCODE_VIDEO = "encode_video"
    WRITE_ARTIFACTS = "write_artifacts"


class RenderArtifactType(StrEnum):
    TEMP_VIDEO = "temp_video"
    TEMP_AUDIO = "temp_audio"
    PROXY_VIDEO = "proxy_video"
    PREVIEW_VIDEO = "preview_video"
    FINAL_VIDEO = "final_video"
    THUMBNAIL = "thumbnail"
    WAVEFORM = "waveform"
    RENDER_REPORT = "render_report"