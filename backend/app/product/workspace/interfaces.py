from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ProductionWorkspaceLoader(
    ABC
):
    @abstractmethod
    def load_production(
        self,
        production_id: str,
    ) -> Any | None:
        raise NotImplementedError


class TimelineWorkspaceLoader(
    ABC
):
    @abstractmethod
    def load_timeline(
        self,
        production_id: str,
    ) -> Any | None:
        raise NotImplementedError


class ArtifactWorkspaceLoader(
    ABC
):
    @abstractmethod
    def load_artifacts(
        self,
        production_id: str,
    ) -> list[Any]:
        raise NotImplementedError


class QualityWorkspaceLoader(
    ABC
):
    @abstractmethod
    def load_quality_report(
        self,
        production_id: str,
    ) -> Any | None:
        raise NotImplementedError


class AISummaryWorkspaceLoader(
    ABC
):
    @abstractmethod
    def load_ai_summary(
        self,
        production_id: str,
    ) -> dict[str, Any]:
        raise NotImplementedError


class IssueWorkspaceLoader(
    ABC
):
    @abstractmethod
    def load_issues(
        self,
        production_id: str,
    ) -> list[Any]:
        raise NotImplementedError