from __future__ import annotations

from time import perf_counter
from typing import Any

from app.product.adapters import (
    ProductSnapshotBuilder,
    ProductWorkspaceSnapshot,
)
from app.product.contracts import (
    ProductFailure,
    ProductProductionStatus,
    ProductStage,
)
from app.product.workspace.cache import (
    ProductWorkspaceCache,
)
from app.product.workspace.errors import (
    ProductWorkspaceLoadError,
    ProductWorkspaceNotFoundError,
)
from app.product.workspace.interfaces import (
    AISummaryWorkspaceLoader,
    ArtifactWorkspaceLoader,
    IssueWorkspaceLoader,
    ProductionWorkspaceLoader,
    QualityWorkspaceLoader,
    TimelineWorkspaceLoader,
)
from app.product.workspace.models import (
    ProductWorkspaceLoadResult,
    ProductWorkspaceSources,
)


class ProductWorkspaceService:
    def __init__(
        self,
        *,
        production_loader: ProductionWorkspaceLoader,
        timeline_loader: TimelineWorkspaceLoader,
        artifact_loader: ArtifactWorkspaceLoader,
        quality_loader: QualityWorkspaceLoader,
        ai_summary_loader: AISummaryWorkspaceLoader,
        issue_loader: IssueWorkspaceLoader,
        snapshot_builder: (
            ProductSnapshotBuilder | None
        ) = None,
        cache: ProductWorkspaceCache | None = None,
    ):
        self.production_loader = (
            production_loader
        )
        self.timeline_loader = (
            timeline_loader
        )
        self.artifact_loader = (
            artifact_loader
        )
        self.quality_loader = (
            quality_loader
        )
        self.ai_summary_loader = (
            ai_summary_loader
        )
        self.issue_loader = issue_loader

        self.snapshot_builder = (
            snapshot_builder
            or ProductSnapshotBuilder()
        )

        self.cache = (
            cache
            or ProductWorkspaceCache()
        )

    def load_workspace(
        self,
        production_id: str,
        *,
        force_refresh: bool = False,
        include_timeline_tracks: bool = True,
        status: (
            ProductProductionStatus
            | str
            | None
        ) = None,
        stage: ProductStage | str | None = None,
        progress: float | None = None,
        progress_message: str | None = None,
        failure: ProductFailure | None = None,
    ) -> ProductWorkspaceSnapshot:
        if not production_id:
            raise ValueError(
                "production_id is required."
            )

        if not force_refresh:
            cached = self.cache.get(
                production_id
            )

            if cached is not None:
                return cached

        sources = self.load_sources(
            production_id
        )

        snapshot = self.snapshot_builder.build(
            production=sources.production,
            timeline=sources.timeline,
            artifacts=sources.artifacts,
            quality_report=(
                sources.quality_report
            ),
            ai_summary=sources.ai_summary,
            issues=sources.issues,
            status=status,
            stage=stage,
            progress=progress,
            progress_message=(
                progress_message
            ),
            failure=failure,
            include_timeline_tracks=(
                include_timeline_tracks
            ),
        )

        snapshot.metadata = {
            **snapshot.metadata,
            "workspace_service": (
                "ProductWorkspaceService"
            ),
            "source_metadata": (
                sources.metadata
            ),
        }

        self.cache.set(
            production_id,
            snapshot,
        )

        return snapshot

    def load_workspace_result(
        self,
        production_id: str,
        *,
        force_refresh: bool = False,
        include_timeline_tracks: bool = True,
        **kwargs: Any,
    ) -> ProductWorkspaceLoadResult:
        started = perf_counter()

        cache_hit = (
            not force_refresh
            and self.cache.get(
                production_id
            )
            is not None
        )

        try:
            snapshot = self.load_workspace(
                production_id,
                force_refresh=force_refresh,
                include_timeline_tracks=(
                    include_timeline_tracks
                ),
                **kwargs,
            )

            return ProductWorkspaceLoadResult(
                production_id=production_id,
                success=True,
                snapshot=snapshot,
                cache_hit=cache_hit,
                metadata={
                    "duration_seconds": round(
                        perf_counter() - started,
                        6,
                    ),
                },
            )

        except Exception as error:
            return ProductWorkspaceLoadResult(
                production_id=production_id,
                success=False,
                snapshot=None,
                cache_hit=False,
                errors=[str(error)],
                metadata={
                    "duration_seconds": round(
                        perf_counter() - started,
                        6,
                    ),
                    "error_type": (
                        error.__class__.__name__
                    ),
                },
            )

    def load_sources(
        self,
        production_id: str,
    ) -> ProductWorkspaceSources:
        try:
            production = (
                self.production_loader
                .load_production(
                    production_id
                )
            )

            if production is None:
                raise (
                    ProductWorkspaceNotFoundError(
                        "Production was not found: "
                        f"{production_id}"
                    )
                )

            timeline = (
                self.timeline_loader
                .load_timeline(
                    production_id
                )
            )

            artifacts = (
                self.artifact_loader
                .load_artifacts(
                    production_id
                )
            )

            quality_report = (
                self.quality_loader
                .load_quality_report(
                    production_id
                )
            )

            ai_summary = (
                self.ai_summary_loader
                .load_ai_summary(
                    production_id
                )
            )

            issues = (
                self.issue_loader
                .load_issues(
                    production_id
                )
            )

            return ProductWorkspaceSources(
                production=production,
                timeline=timeline,
                artifacts=list(
                    artifacts or []
                ),
                quality_report=(
                    quality_report
                ),
                ai_summary=dict(
                    ai_summary or {}
                ),
                issues=list(
                    issues or []
                ),
                metadata={
                    "timeline_loaded": (
                        timeline is not None
                    ),
                    "artifact_count": len(
                        artifacts or []
                    ),
                    "quality_loaded": (
                        quality_report
                        is not None
                    ),
                    "ai_summary_loaded": bool(
                        ai_summary
                    ),
                    "issue_count": len(
                        issues or []
                    ),
                },
            )

        except ProductWorkspaceNotFoundError:
            raise

        except Exception as error:
            raise ProductWorkspaceLoadError(
                "Failed to load product workspace "
                f"for production {production_id}: "
                f"{error}"
            ) from error

    def refresh_workspace(
        self,
        production_id: str,
        **kwargs: Any,
    ) -> ProductWorkspaceSnapshot:
        self.cache.invalidate(
            production_id
        )

        return self.load_workspace(
            production_id,
            force_refresh=True,
            **kwargs,
        )

    def invalidate_workspace(
        self,
        production_id: str,
    ) -> None:
        self.cache.invalidate(
            production_id
        )