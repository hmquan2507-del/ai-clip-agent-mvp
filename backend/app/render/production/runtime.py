from __future__ import annotations

from pathlib import Path
from time import perf_counter
from typing import Any

from app.render.execution import (
    RenderArchitectureRuntime,
    RenderExecutionRuntime,
    RenderQualityGate,
    RenderSchedulerRuntime,
)
from app.render.production.models import (
    ProductionRenderIssue,
    ProductionRenderResult,
)
from app.timeline.compiler.models import (
    ExecutionTimeline,
)


class ProductionRenderRuntime:
    def __init__(
        self,
        architecture_runtime: (
            RenderArchitectureRuntime | None
        ) = None,
        scheduler_runtime: (
            RenderSchedulerRuntime | None
        ) = None,
        execution_runtime: (
            RenderExecutionRuntime | None
        ) = None,
        quality_gate: RenderQualityGate | None = None,
    ):
        from app.render.execution import (
            build_render_architecture_runtime,
            build_render_execution_runtime,
            build_render_quality_gate,
            build_render_scheduler_runtime,
        )

        self.architecture_runtime = (
            architecture_runtime
            or build_render_architecture_runtime()
        )

        self.scheduler_runtime = (
            scheduler_runtime
            or build_render_scheduler_runtime()
        )

        self.execution_runtime = (
            execution_runtime
            or build_render_execution_runtime(
                delay_seconds=0.0
            )
        )

        self.quality_gate = (
            quality_gate
            or build_render_quality_gate()
        )

    def render(
        self,
        execution_timeline: ExecutionTimeline,
        storage_root: str = "storage/production_render",
    ) -> ProductionRenderResult:
        started_counter = perf_counter()

        issues: list[ProductionRenderIssue] = []

        context = None
        execution_plan = None
        execution_summary = None
        quality_report = None

        final_video_path: str | None = None
        thumbnail_path: str | None = None
        render_report_path: str | None = None
        artifact_manifest_path: str | None = None
        quality_report_path: str | None = None
        recovery_diagnostics_path: str | None = None

        try:
            context = (
                self.architecture_runtime.build_context(
                    execution_timeline=execution_timeline,
                    storage_root=storage_root,
                )
            )

            if context.graph is None:
                raise RuntimeError(
                    "Render graph was not created."
                )

            if not context.graph.metadata.get(
                "valid",
                False,
            ):
                issues.append(
                    ProductionRenderIssue(
                        level="error",
                        code="render_graph_invalid",
                        message=(
                            "Render graph validation failed."
                        ),
                        stage="architecture",
                        metadata={
                            "issues": [
                                item.to_dict()
                                for item
                                in context.graph.issues
                            ],
                        },
                    )
                )

                return self._result(
                    execution_timeline=execution_timeline,
                    success=False,
                    execution_plan=None,
                    execution_summary=None,
                    quality_report=None,
                    final_video_path=None,
                    thumbnail_path=None,
                    render_report_path=None,
                    artifact_manifest_path=None,
                    quality_report_path=None,
                    recovery_diagnostics_path=None,
                    issues=issues,
                    started_counter=started_counter,
                    context=context,
                )

            execution_plan = (
                self.scheduler_runtime.schedule(
                    context
                )
            )

            if not execution_plan.metadata.get(
                "scheduled",
                False,
            ):
                issues.append(
                    ProductionRenderIssue(
                        level="error",
                        code="render_schedule_failed",
                        message=(
                            "Render execution plan could "
                            "not be scheduled."
                        ),
                        stage="scheduler",
                        metadata={
                            "issues": [
                                item.to_dict()
                                for item
                                in execution_plan.issues
                            ],
                        },
                    )
                )

                return self._result(
                    execution_timeline=execution_timeline,
                    success=False,
                    execution_plan=execution_plan,
                    execution_summary=None,
                    quality_report=None,
                    final_video_path=None,
                    thumbnail_path=None,
                    render_report_path=None,
                    artifact_manifest_path=None,
                    quality_report_path=None,
                    recovery_diagnostics_path=None,
                    issues=issues,
                    started_counter=started_counter,
                    context=context,
                )

            execution_summary = (
                self.execution_runtime.run(
                    context=context,
                    plan=execution_plan,
                )
            )

            if not execution_summary.success:
                issues.append(
                    ProductionRenderIssue(
                        level="error",
                        code="render_execution_failed",
                        message=(
                            execution_summary.error
                            or "Render execution failed."
                        ),
                        stage="execution",
                        metadata={
                            "failed_node_id": (
                                execution_summary
                                .failed_node_id
                            ),
                            "failed_node_count": (
                                execution_summary
                                .failed_node_count
                            ),
                            "skipped_node_count": (
                                execution_summary
                                .skipped_node_count
                            ),
                        },
                    )
                )

                recovery_diagnostics_path = (
                    context.metadata.get(
                        "recovery_diagnostics_path"
                    )
                )

                return self._result(
                    execution_timeline=execution_timeline,
                    success=False,
                    execution_plan=execution_plan,
                    execution_summary=execution_summary,
                    quality_report=None,
                    final_video_path=None,
                    thumbnail_path=None,
                    render_report_path=None,
                    artifact_manifest_path=(
                        context.metadata.get(
                            "render_artifact_manifest"
                        )
                    ),
                    quality_report_path=None,
                    recovery_diagnostics_path=(
                        recovery_diagnostics_path
                    ),
                    issues=issues,
                    started_counter=started_counter,
                    context=context,
                )

            artifact_map = {
                artifact.artifact_id: artifact
                for artifact in context.artifacts
            }

            final_artifact = artifact_map.get(
                "final_video"
            )
            thumbnail_artifact = artifact_map.get(
                "thumbnail"
            )
            render_report_artifact = (
                artifact_map.get("render_report")
            )

            if final_artifact is None:
                issues.append(
                    ProductionRenderIssue(
                        level="error",
                        code="final_artifact_missing",
                        message=(
                            "Render execution completed "
                            "without a final video artifact."
                        ),
                        stage="artifact",
                    )
                )

                return self._result(
                    execution_timeline=execution_timeline,
                    success=False,
                    execution_plan=execution_plan,
                    execution_summary=execution_summary,
                    quality_report=None,
                    final_video_path=None,
                    thumbnail_path=(
                        thumbnail_artifact.local_path
                        if thumbnail_artifact
                        else None
                    ),
                    render_report_path=(
                        render_report_artifact.local_path
                        if render_report_artifact
                        else None
                    ),
                    artifact_manifest_path=(
                        context.metadata.get(
                            "render_artifact_manifest"
                        )
                    ),
                    quality_report_path=None,
                    recovery_diagnostics_path=(
                        context.metadata.get(
                            "recovery_diagnostics_path"
                        )
                    ),
                    issues=issues,
                    started_counter=started_counter,
                    context=context,
                )

            final_video_path = (
                final_artifact.local_path
            )

            thumbnail_path = (
                thumbnail_artifact.local_path
                if thumbnail_artifact
                else None
            )

            render_report_path = (
                render_report_artifact.local_path
                if render_report_artifact
                else None
            )

            artifact_manifest_path = (
                context.metadata.get(
                    "render_artifact_manifest"
                )
            )

            recovery_diagnostics_path = (
                context.metadata.get(
                    "recovery_diagnostics_path"
                )
            )

            quality_report = (
                self.quality_gate.validate(
                    context=context,
                    output_path=final_video_path,
                )
            )

            quality_report_path = (
                quality_report.report_path
            )

            if not quality_report.approved:
                issues.append(
                    ProductionRenderIssue(
                        level="error",
                        code="quality_gate_rejected",
                        message=(
                            "Rendered video was rejected "
                            "by the quality gate."
                        ),
                        stage="quality",
                        metadata={
                            "status": self._value(
                                quality_report.status
                            ),
                            "quality_score": (
                                quality_report
                                .quality_score
                            ),
                            "failure_count": (
                                quality_report
                                .failure_count
                            ),
                            "warning_count": (
                                quality_report
                                .warning_count
                            ),
                        },
                    )
                )

            success = (
                execution_summary.success
                and quality_report.approved
                and final_video_path is not None
                and not any(
                    issue.level == "error"
                    for issue in issues
                )
            )

            return self._result(
                execution_timeline=execution_timeline,
                success=success,
                execution_plan=execution_plan,
                execution_summary=execution_summary,
                quality_report=quality_report,
                final_video_path=final_video_path,
                thumbnail_path=thumbnail_path,
                render_report_path=render_report_path,
                artifact_manifest_path=(
                    artifact_manifest_path
                ),
                quality_report_path=(
                    quality_report_path
                ),
                recovery_diagnostics_path=(
                    recovery_diagnostics_path
                ),
                issues=issues,
                started_counter=started_counter,
                context=context,
            )

        except Exception as error:
            issues.append(
                ProductionRenderIssue(
                    level="error",
                    code="production_render_exception",
                    message=str(error),
                    stage="runtime",
                )
            )

            return self._result(
                execution_timeline=execution_timeline,
                success=False,
                execution_plan=execution_plan,
                execution_summary=execution_summary,
                quality_report=quality_report,
                final_video_path=final_video_path,
                thumbnail_path=thumbnail_path,
                render_report_path=render_report_path,
                artifact_manifest_path=(
                    artifact_manifest_path
                ),
                quality_report_path=(
                    quality_report_path
                ),
                recovery_diagnostics_path=(
                    recovery_diagnostics_path
                ),
                issues=issues,
                started_counter=started_counter,
                context=context,
            )

    def _result(
        self,
        execution_timeline: ExecutionTimeline,
        success: bool,
        execution_plan,
        execution_summary,
        quality_report,
        final_video_path: str | None,
        thumbnail_path: str | None,
        render_report_path: str | None,
        artifact_manifest_path: str | None,
        quality_report_path: str | None,
        recovery_diagnostics_path: str | None,
        issues: list[ProductionRenderIssue],
        started_counter: float,
        context,
    ) -> ProductionRenderResult:
        duration_seconds = round(
            perf_counter() - started_counter,
            6,
        )

        return ProductionRenderResult(
            production_id=(
                execution_timeline.production_id
            ),
            version="15.10.0",
            success=success,
            execution_plan=execution_plan,
            execution_summary=execution_summary,
            quality_report=quality_report,
            final_video_path=final_video_path,
            thumbnail_path=thumbnail_path,
            render_report_path=render_report_path,
            artifact_manifest_path=(
                artifact_manifest_path
            ),
            quality_report_path=quality_report_path,
            recovery_diagnostics_path=(
                recovery_diagnostics_path
            ),
            issues=issues,
            metadata={
                "runtime": "ProductionRenderRuntime",
                "duration_seconds": duration_seconds,
                "execution_timeline_version": (
                    execution_timeline.version
                ),
                "artifact_count": (
                    len(context.artifacts)
                    if context
                    else 0
                ),
                "quality_status": (
                    self._value(
                        quality_report.status
                    )
                    if quality_report
                    else None
                ),
                "quality_score": (
                    quality_report.quality_score
                    if quality_report
                    else None
                ),
            },
        )

    def _value(
        self,
        value: Any,
    ) -> str:
        return (
            value.value
            if hasattr(value, "value")
            else str(value)
        )