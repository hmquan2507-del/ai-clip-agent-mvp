from __future__ import annotations

from app.production.contracts import PipelineStage
from app.production.registry.pipeline_registry import PipelineRegistry
from app.production.registry.runners import (
    AIBrainPipelineRunner,
    AssetResolverPipelineRunner,
    AudioTrackPipelineRunner,
    CompositionPipelineRunner,
    ConflictResolutionPipelineRunner,
    ExecutionGraphPipelineRunner,
    FFmpegCommandPlanPipelineRunner,
    RenderGraphPipelineRunner,
    RenderInstructionsPipelineRunner,
    RenderPlanPipelineRunner,
    RenderSchedulePipelineRunner,
    RuntimeValidationPipelineRunner,
    SubtitleTrackPipelineRunner,
    TimelinePipelineRunner,
    TrackContextPipelineRunner,
    VideoTrackPipelineRunner,
)


DEFAULT_PIPELINE_STAGES: list[PipelineStage] = [
    PipelineStage.AI_BRAIN,
    PipelineStage.TIMELINE,
    PipelineStage.EXECUTION_GRAPH,
    PipelineStage.CONFLICT_RESOLUTION,
    PipelineStage.TRACK_CONTEXT,
    PipelineStage.SUBTITLE_TRACK,
    PipelineStage.VIDEO_TRACK,
    PipelineStage.AUDIO_TRACK,
    PipelineStage.COMPOSITION,
    PipelineStage.RENDER_INSTRUCTIONS,
    PipelineStage.RENDER_PLAN,
    PipelineStage.RENDER_GRAPH,
    PipelineStage.RENDER_SCHEDULE,
    PipelineStage.ASSET_RESOLVER,
    PipelineStage.FFMPEG_COMMAND_PLAN,
    PipelineStage.RUNTIME_VALIDATION,
]


def build_default_pipeline_registry() -> PipelineRegistry:
    registry = PipelineRegistry()

    registry.register(AIBrainPipelineRunner())
    registry.register(TimelinePipelineRunner())
    registry.register(ExecutionGraphPipelineRunner())
    registry.register(ConflictResolutionPipelineRunner())
    registry.register(TrackContextPipelineRunner())
    registry.register(SubtitleTrackPipelineRunner())
    registry.register(VideoTrackPipelineRunner())
    registry.register(AudioTrackPipelineRunner())
    registry.register(CompositionPipelineRunner())
    registry.register(RenderInstructionsPipelineRunner())
    registry.register(RenderPlanPipelineRunner())
    registry.register(RenderGraphPipelineRunner())
    registry.register(RenderSchedulePipelineRunner())
    registry.register(AssetResolverPipelineRunner())
    registry.register(FFmpegCommandPlanPipelineRunner())
    registry.register(RuntimeValidationPipelineRunner())

    return registry