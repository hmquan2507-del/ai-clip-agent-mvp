from __future__ import annotations

from typing import Any

from app.product.adapters.artifact import (
    ProductArtifactAdapter,
)
from app.product.adapters.models import (
    ProductWorkspaceSnapshot,
)
from app.product.adapters.production import (
    ProductProductionAdapter,
)
from app.product.adapters.quality import (
    ProductQualityAdapter,
)
from app.product.adapters.timeline import (
    ProductTimelineAdapter,
)
from app.product.adapters.utils import normalize
from app.product.contracts import (
    ProductFailure,
    ProductProductionStatus,
    ProductStage,
)


class ProductSnapshotBuilder:
    def __init__(
        self,
        production_adapter: (
            ProductProductionAdapter | None
        ) = None,
        timeline_adapter: (
            ProductTimelineAdapter | None
        ) = None,
        artifact_adapter: (
            ProductArtifactAdapter | None
        ) = None,
        quality_adapter: (
            ProductQualityAdapter | None
        ) = None,
    ):
        self.production_adapter = (
            production_adapter
            or ProductProductionAdapter()
        )
        self.timeline_adapter = (
            timeline_adapter
            or ProductTimelineAdapter()
        )
        self.artifact_adapter = (
            artifact_adapter
            or ProductArtifactAdapter()
        )
        self.quality_adapter = (
            quality_adapter
            or ProductQualityAdapter()
        )

    def build(
        self,
        *,
        production: Any,
        timeline: Any | None = None,
        artifacts: list[Any] | None = None,
        quality_report: Any | None = None,
        ai_summary: dict[str, Any] | None = None,
        issues: list[Any] | None = None,
        status: ProductProductionStatus | str | None = None,
        stage: ProductStage | str | None = None,
        progress: float | None = None,
        progress_message: str | None = None,
        failure: ProductFailure | None = None,
        include_timeline_tracks: bool = True,
    ) -> ProductWorkspaceSnapshot:
        production_snapshot = (
            self.production_adapter.adapt(
                production,
                status=status,
                stage=stage,
                progress=progress,
                progress_message=progress_message,
                failure=failure,
            )
        )

        adapted_artifacts = (
            self.artifact_adapter.adapt_many(
                artifacts
            )
        )

        production_snapshot.artifacts = (
            adapted_artifacts
        )

        return ProductWorkspaceSnapshot(
            production=production_snapshot,
            timeline=self.timeline_adapter.adapt(
                timeline,
                include_tracks=(
                    include_timeline_tracks
                ),
            ),
            preview=(
                self.artifact_adapter.build_preview(
                    artifacts
                )
            ),
            quality=self.quality_adapter.adapt(
                quality_report
            ),
            artifacts=adapted_artifacts,
            ai_summary=normalize(
                ai_summary or {}
            ),
            issues=normalize(
                issues or []
            ),
            metadata={
                "builder": "ProductSnapshotBuilder",
                "contract_version": "16.0.2",
            },
        )