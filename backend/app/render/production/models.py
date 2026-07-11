from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.render.execution.models import (
    RenderExecutionPlan,
    RenderExecutionSummary,
)
from app.render.execution.quality import (
    RenderQualityReport,
)


@dataclass
class ProductionRenderIssue:
    level: str
    code: str
    message: str
    stage: str | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "stage": self.stage,
            "metadata": self.metadata,
        }


@dataclass
class ProductionRenderResult:
    production_id: str
    version: str
    success: bool

    execution_plan: RenderExecutionPlan | None
    execution_summary: RenderExecutionSummary | None
    quality_report: RenderQualityReport | None

    final_video_path: str | None
    thumbnail_path: str | None
    render_report_path: str | None
    artifact_manifest_path: str | None
    quality_report_path: str | None
    recovery_diagnostics_path: str | None

    issues: list[ProductionRenderIssue]
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "version": self.version,
            "success": self.success,
            "execution_plan": (
                self.execution_plan.to_dict()
                if self.execution_plan
                else None
            ),
            "execution_summary": (
                self.execution_summary.to_dict()
                if self.execution_summary
                else None
            ),
            "quality_report": (
                self.quality_report.to_dict()
                if self.quality_report
                else None
            ),
            "final_video_path": self.final_video_path,
            "thumbnail_path": self.thumbnail_path,
            "render_report_path": (
                self.render_report_path
            ),
            "artifact_manifest_path": (
                self.artifact_manifest_path
            ),
            "quality_report_path": (
                self.quality_report_path
            ),
            "recovery_diagnostics_path": (
                self.recovery_diagnostics_path
            ),
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
            "metadata": self.metadata,
        }