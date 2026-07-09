from __future__ import annotations

from sqlalchemy.orm import Session

from app.asset.memory import (
    AssetMemoryRecordRequest,
    ProductionAssetUsage,
    build_production_asset_memory_runtime,
)
from app.asset.resolver import AssetResolveRequest, AssetResolverRuntime
from app.asset.workflow import MediaWorkflowRequest, MediaWorkflowRuntime
from app.timeline.asset_injector.models import (
    TimelineAssetClip,
    TimelineAssetInjectionRequest,
    TimelineAssetInjectionResult,
)


class TimelineAssetInjectionRuntime:
    def __init__(
        self,
        db: Session,
        asset_resolver: AssetResolverRuntime | None = None,
        media_workflow: MediaWorkflowRuntime | None = None,
        asset_memory=None,
    ):
        self.db = db
        self.asset_resolver = asset_resolver or AssetResolverRuntime(db=db)
        self.media_workflow = media_workflow or MediaWorkflowRuntime()
        self.asset_memory = asset_memory or build_production_asset_memory_runtime()

    def inject(
        self,
        request: TimelineAssetInjectionRequest,
    ) -> TimelineAssetInjectionResult:
        clips: list[TimelineAssetClip] = []
        failed: list[dict] = []

        for instruction in request.instructions:
            try:
                workflow = self.media_workflow.build_workflow(
                    MediaWorkflowRequest(
                        query=instruction.query,
                        asset_type=instruction.asset_type,
                        track_type=instruction.track_type,
                        preferred_duration=(
                            instruction.preferred_duration or instruction.duration
                        ),
                        preferred_orientation=instruction.preferred_orientation,
                        commercial_use=instruction.commercial_use,
                        per_page=5,
                        metadata=instruction.metadata,
                    )
                )

                provider_keys = (
                    instruction.provider_keys
                    if instruction.provider_keys
                    else workflow.provider_keys
                )

                resolved = self.asset_resolver.resolve(
                    AssetResolveRequest(
                        query=instruction.query,
                        asset_type=instruction.asset_type,
                        preferred_duration=(
                            instruction.preferred_duration or instruction.duration
                        ),
                        preferred_orientation=instruction.preferred_orientation,
                        commercial_use=instruction.commercial_use,
                        provider_keys=provider_keys,
                        metadata={
                            **instruction.metadata,
                            "production_id": request.production_id,
                            "track_type": instruction.track_type,
                            "start_time": instruction.start_time,
                            "end_time": instruction.end_time,
                            "workflow_key": workflow.workflow_key,
                            "workflow_provider_keys": provider_keys,
                        },
                    )
                )

                payload = resolved.payload

                clip = TimelineAssetClip(
                    asset_id=str(resolved.asset_id),
                    asset_type=instruction.asset_type,
                    track_type=instruction.track_type,
                    start_time=instruction.start_time,
                    end_time=instruction.end_time,
                    layer=instruction.layer,
                    local_path=payload.get("local_path"),
                    title=payload.get("title"),
                    volume=instruction.volume,
                    opacity=instruction.opacity,
                    speed=instruction.speed,
                    metadata={
                        "source": resolved.source,
                        "ranking_score": resolved.ranking_score,
                        "resolver_metadata": resolved.metadata,
                        "workflow_key": workflow.workflow_key,
                        "workflow_provider_keys": provider_keys,
                        "instruction": instruction.metadata,
                        "provider_key": payload.get("provider_key"),
                        "provider_asset_id": payload.get("provider_asset_id"),
                        "license": payload.get("license"),
                    },
                )

                clips.append(clip)

                self.asset_memory.record(
                    AssetMemoryRecordRequest(
                        production_id=request.production_id,
                        usages=[
                            ProductionAssetUsage(
                                production_id=request.production_id,
                                asset_id=clip.asset_id,
                                provider_key=payload.get("provider_key"),
                                provider_asset_id=payload.get("provider_asset_id"),
                                asset_type=instruction.asset_type,
                                track_type=instruction.track_type,
                                start_time=instruction.start_time,
                                end_time=instruction.end_time,
                                query=instruction.query,
                                local_path=payload.get("local_path"),
                                metadata={
                                    "title": payload.get("title"),
                                    "license": payload.get("license"),
                                },
                            )
                        ],
                    )
                )

            except Exception as error:
                failed.append(
                    {
                        "query": instruction.query,
                        "asset_type": instruction.asset_type,
                        "track_type": instruction.track_type,
                        "start_time": instruction.start_time,
                        "end_time": instruction.end_time,
                        "error": str(error),
                    }
                )

        return TimelineAssetInjectionResult(
            production_id=request.production_id,
            asset_clips=clips,
            failed_instructions=failed,
            metadata={
                "instruction_count": len(request.instructions),
                "asset_clip_count": len(clips),
                "failed_count": len(failed),
            },
        )