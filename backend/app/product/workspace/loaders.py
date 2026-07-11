from __future__ import annotations

from typing import Any

from app.product.workspace.interfaces import (
    AISummaryWorkspaceLoader,
    ArtifactWorkspaceLoader,
    IssueWorkspaceLoader,
    ProductionWorkspaceLoader,
    QualityWorkspaceLoader,
    TimelineWorkspaceLoader,
)


class InMemoryProductWorkspaceLoader(
    ProductionWorkspaceLoader,
    TimelineWorkspaceLoader,
    ArtifactWorkspaceLoader,
    QualityWorkspaceLoader,
    AISummaryWorkspaceLoader,
    IssueWorkspaceLoader,
):
    def __init__(self):
        self.productions: dict[str, Any] = {}
        self.timelines: dict[str, Any] = {}
        self.artifacts: dict[
            str,
            list[Any],
        ] = {}
        self.quality_reports: dict[
            str,
            Any,
        ] = {}
        self.ai_summaries: dict[
            str,
            dict[str, Any],
        ] = {}
        self.issues: dict[
            str,
            list[Any],
        ] = {}

    def register(
        self,
        production_id: str,
        *,
        production: Any,
        timeline: Any | None = None,
        artifacts: list[Any] | None = None,
        quality_report: Any | None = None,
        ai_summary: dict[str, Any] | None = None,
        issues: list[Any] | None = None,
    ) -> None:
        self.productions[
            production_id
        ] = production

        if timeline is not None:
            self.timelines[
                production_id
            ] = timeline

        self.artifacts[
            production_id
        ] = list(
            artifacts or []
        )

        if quality_report is not None:
            self.quality_reports[
                production_id
            ] = quality_report

        self.ai_summaries[
            production_id
        ] = dict(
            ai_summary or {}
        )

        self.issues[
            production_id
        ] = list(
            issues or []
        )

    def load_production(
        self,
        production_id: str,
    ) -> Any | None:
        return self.productions.get(
            production_id
        )

    def load_timeline(
        self,
        production_id: str,
    ) -> Any | None:
        return self.timelines.get(
            production_id
        )

    def load_artifacts(
        self,
        production_id: str,
    ) -> list[Any]:
        return list(
            self.artifacts.get(
                production_id,
                [],
            )
        )

    def load_quality_report(
        self,
        production_id: str,
    ) -> Any | None:
        return self.quality_reports.get(
            production_id
        )

    def load_ai_summary(
        self,
        production_id: str,
    ) -> dict[str, Any]:
        return dict(
            self.ai_summaries.get(
                production_id,
                {},
            )
        )

    def load_issues(
        self,
        production_id: str,
    ) -> list[Any]:
        return list(
            self.issues.get(
                production_id,
                [],
            )
        )