from __future__ import annotations

from sqlalchemy.orm import Session

from app.asset.orchestrator.models import (
    AssetOrchestrationRequest,
    AssetOrchestrationResult,
)
from app.timeline.asset_injector import (
    TimelineAssetInjectionRequest,
    TimelineAssetInstruction,
    TimelineAssetInjectionRuntime,
)


class AssetOrchestratorRuntime:
    def __init__(
        self,
        db: Session,
        injection_runtime: TimelineAssetInjectionRuntime | None = None,
    ):
        self.db = db
        self.injection_runtime = injection_runtime or TimelineAssetInjectionRuntime(db=db)

    def run(
        self,
        request: AssetOrchestrationRequest,
    ) -> AssetOrchestrationResult:
        instructions = [
            TimelineAssetInstruction(
                query=item.query,
                asset_type=item.asset_type,
                track_type=item.track_type,
                start_time=item.start_time,
                end_time=item.end_time,
                preferred_orientation=item.preferred_orientation,
                preferred_duration=item.preferred_duration,
                layer=item.layer,
                volume=item.volume,
                opacity=item.opacity,
                speed=item.speed,
                commercial_use=item.commercial_use,
                provider_keys=item.provider_keys,
                metadata=item.metadata,
            )
            for item in request.plan_items
        ]

        injection_result = self.injection_runtime.inject(
            TimelineAssetInjectionRequest(
                production_id=request.production_id,
                instructions=instructions,
                metadata=request.metadata,
            )
        )

        return AssetOrchestrationResult(
            production_id=request.production_id,
            asset_clips=injection_result.asset_clips,
            failed_items=injection_result.failed_instructions,
            metadata={
                "plan_item_count": len(request.plan_items),
                "asset_clip_count": len(injection_result.asset_clips),
                "failed_count": len(injection_result.failed_instructions),
                "injection_metadata": injection_result.metadata,
            },
        )