from __future__ import annotations

from app.production.contracts import (
    PipelineExecutionContext,
    PipelineResult,
    PipelineStage,
)
from app.production.registry import PipelineRegistry


class ProductionExecutor:
    def __init__(self, registry: PipelineRegistry):
        self.registry = registry

    def run_stage(
        self,
        stage: PipelineStage,
        context: PipelineExecutionContext,
    ) -> PipelineResult:
        return self.registry.run(
            stage=stage,
            context=context,
        )