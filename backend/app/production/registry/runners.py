from __future__ import annotations

from typing import Any
from uuid import UUID

from app.artifacts import keys
from app.production.contracts import (
    PipelineExecutionContext,
    PipelineResult,
    PipelineStage,
    PipelineStatus,
)
from app.production.registry.pipeline_runner import PipelineRunner
from app.services.ai_engine_runtime_service import AIEngineRuntimeService
from app.services.asset_resolver_service import AssetResolverService
from app.services.audio_track_composer_service import AudioTrackComposerService
from app.services.composition_runtime_service import CompositionRuntimeService
from app.services.conflict_resolution_service import ConflictResolutionService
from app.services.execution_graph_service import ExecutionGraphService
from app.services.ffmpeg_runtime_service import FFmpegRuntimeService
from app.services.render_graph_service import RenderGraphService
from app.services.render_instruction_service import RenderInstructionService
from app.services.render_plan_service import RenderPlanService
from app.services.render_schedule_service import RenderScheduleService
from app.services.runtime_artifact_validation_service import (
    RuntimeArtifactValidationService,
)
from app.services.subtitle_track_composer_service import SubtitleTrackComposerService
from app.services.timeline_composer_service import TimelineComposerService
from app.services.track_context_service import TrackContextService
from app.services.video_track_composer_service import VideoTrackComposerService


class ServicePipelineRunner(PipelineRunner):
    service_class: type
    service_method: str = "run"
    stage: PipelineStage
    artifact_key: str | None = None

    def run(
        self,
        context: PipelineExecutionContext,
    ) -> PipelineResult:
        service = self.service_class(context.db)
        method = getattr(service, self.service_method)

        try:
            payload = method(context.production_id)
        except Exception as error:
            return PipelineResult(
                production_id=context.production_id_str,
                stage=self.stage,
                status=PipelineStatus.FAILED,
                payload={},
                artifact_key=self.artifact_key,
                error=str(error),
                metadata={
                    "runner": self.__class__.__name__,
                    "service": self.service_class.__name__,
                },
            )

        status = self._infer_status(payload)

        return PipelineResult(
            production_id=context.production_id_str,
            stage=self.stage,
            status=status,
            payload=payload if isinstance(payload, dict) else {"value": payload},
            artifact_key=self.artifact_key,
            metadata={
                "runner": self.__class__.__name__,
                "service": self.service_class.__name__,
            },
        )

    def _infer_status(
        self,
        payload: dict[str, Any],
    ) -> PipelineStatus:
        if not isinstance(payload, dict):
            return PipelineStatus.COMPLETED

        metadata = payload.get("metadata", {})
        if not isinstance(metadata, dict):
            return PipelineStatus.COMPLETED

        if metadata.get("status") == "skipped":
            return PipelineStatus.SKIPPED

        if metadata.get("status") == "failed":
            return PipelineStatus.FAILED

        return PipelineStatus.COMPLETED


class AIBrainPipelineRunner(PipelineRunner):
    stage = PipelineStage.AI_BRAIN
    artifact_key = keys.EDITING_EXECUTION_PLANNER

    def run(
        self,
        context: PipelineExecutionContext,
    ) -> PipelineResult:
        service = AIEngineRuntimeService(context.db)

        try:
            payload = service.run_pipeline(
                production_id=context.production_id,
                engine_keys=[
                    "hook_detection",
                    "story_engine",
                    "emotion_engine",
                    "editing_style_engine",
                    "decision_engine",
                    "editing_execution_planner",
                ],
            )
        except Exception as error:
            return PipelineResult(
                production_id=context.production_id_str,
                stage=self.stage,
                status=PipelineStatus.FAILED,
                payload={},
                artifact_key=self.artifact_key,
                error=str(error),
                metadata={
                    "runner": self.__class__.__name__,
                    "service": "AIEngineRuntimeService",
                },
            )

        status = PipelineStatus.COMPLETED

        metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
        if isinstance(metadata, dict):
            if metadata.get("status") == "skipped":
                status = PipelineStatus.SKIPPED
            elif metadata.get("status") == "failed":
                status = PipelineStatus.FAILED

        return PipelineResult(
            production_id=context.production_id_str,
            stage=self.stage,
            status=status,
            payload=payload,
            artifact_key=self.artifact_key,
            metadata={
                "runner": self.__class__.__name__,
                "service": "AIEngineRuntimeService",
            },
        )


class TimelinePipelineRunner(ServicePipelineRunner):
    stage = PipelineStage.TIMELINE
    artifact_key = keys.TIMELINE
    service_class = TimelineComposerService


class ExecutionGraphPipelineRunner(ServicePipelineRunner):
    stage = PipelineStage.EXECUTION_GRAPH
    artifact_key = keys.EXECUTION_GRAPH
    service_class = ExecutionGraphService


class ConflictResolutionPipelineRunner(ServicePipelineRunner):
    stage = PipelineStage.CONFLICT_RESOLUTION
    artifact_key = keys.OPTIMIZED_EXECUTION_GRAPH
    service_class = ConflictResolutionService


class TrackContextPipelineRunner(ServicePipelineRunner):
    stage = PipelineStage.TRACK_CONTEXT
    artifact_key = keys.TRACK_CONTEXT
    service_class = TrackContextService


class SubtitleTrackPipelineRunner(ServicePipelineRunner):
    stage = PipelineStage.SUBTITLE_TRACK
    artifact_key = keys.SUBTITLE_TRACK
    service_class = SubtitleTrackComposerService


class VideoTrackPipelineRunner(ServicePipelineRunner):
    stage = PipelineStage.VIDEO_TRACK
    artifact_key = keys.VIDEO_TRACK
    service_class = VideoTrackComposerService


class AudioTrackPipelineRunner(ServicePipelineRunner):
    stage = PipelineStage.AUDIO_TRACK
    artifact_key = keys.AUDIO_TRACK
    service_class = AudioTrackComposerService


class CompositionPipelineRunner(ServicePipelineRunner):
    stage = PipelineStage.COMPOSITION
    artifact_key = keys.COMPOSITION
    service_class = CompositionRuntimeService


class RenderInstructionsPipelineRunner(ServicePipelineRunner):
    stage = PipelineStage.RENDER_INSTRUCTIONS
    artifact_key = keys.RENDER_INSTRUCTIONS
    service_class = RenderInstructionService


class RenderPlanPipelineRunner(ServicePipelineRunner):
    stage = PipelineStage.RENDER_PLAN
    artifact_key = keys.RENDER_PLAN
    service_class = RenderPlanService


class RenderGraphPipelineRunner(ServicePipelineRunner):
    stage = PipelineStage.RENDER_GRAPH
    artifact_key = keys.RENDER_GRAPH
    service_class = RenderGraphService


class RenderSchedulePipelineRunner(ServicePipelineRunner):
    stage = PipelineStage.RENDER_SCHEDULE
    artifact_key = keys.RENDER_SCHEDULE
    service_class = RenderScheduleService


class AssetResolverPipelineRunner(ServicePipelineRunner):
    stage = PipelineStage.ASSET_RESOLVER
    artifact_key = keys.RESOLVED_ASSETS
    service_class = AssetResolverService


class FFmpegCommandPlanPipelineRunner(ServicePipelineRunner):
    stage = PipelineStage.FFMPEG_COMMAND_PLAN
    artifact_key = keys.FFMPEG_COMMAND_PLAN
    service_class = FFmpegRuntimeService


class RuntimeValidationPipelineRunner(ServicePipelineRunner):
    stage = PipelineStage.RUNTIME_VALIDATION
    artifact_key = "runtime_validation"
    service_class = RuntimeArtifactValidationService