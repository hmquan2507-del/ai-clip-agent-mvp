from __future__ import annotations

from enum import StrEnum


class PipelineStage(StrEnum):
    CONTENT_UNDERSTANDING = "content_understanding"

    AI_BRAIN = "ai_brain"

    TIMELINE = "timeline"
    EXECUTION_GRAPH = "execution_graph"
    CONFLICT_RESOLUTION = "conflict_resolution"
    TRACK_CONTEXT = "track_context"

    SUBTITLE_TRACK = "subtitle_track"
    VIDEO_TRACK = "video_track"
    AUDIO_TRACK = "audio_track"

    COMPOSITION = "composition"

    RENDER_INSTRUCTIONS = "render_instructions"
    RENDER_PLAN = "render_plan"
    RENDER_GRAPH = "render_graph"
    RENDER_SCHEDULE = "render_schedule"

    ASSET_RESOLVER = "asset_resolver"
    FFMPEG_COMMAND_PLAN = "ffmpeg_command_plan"

    RUNTIME_VALIDATION = "runtime_validation"