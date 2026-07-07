from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.production.contracts import (
    PipelineExecutionContext,
    PipelineResult,
    PipelineStage,
)


class PipelineRunner(ABC):
    stage: PipelineStage
    artifact_key: str | None = None

    @abstractmethod
    def run(
        self,
        context: PipelineExecutionContext,
    ) -> PipelineResult:
        raise NotImplementedError

    def metadata(self) -> dict[str, Any]:
        return {
            "runner": self.__class__.__name__,
            "stage": self.stage.value,
            "artifact_key": self.artifact_key,
        }