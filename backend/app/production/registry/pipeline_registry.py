from __future__ import annotations

from app.production.contracts import (
    PipelineExecutionContext,
    PipelineResult,
    PipelineStage,
)
from app.production.registry.pipeline_runner import PipelineRunner


class PipelineRegistry:
    def __init__(self):
        self._runners: dict[PipelineStage, PipelineRunner] = {}

    def register(
        self,
        runner: PipelineRunner,
    ) -> None:
        if runner.stage in self._runners:
            raise ValueError(f"Pipeline stage already registered: {runner.stage}")

        self._runners[runner.stage] = runner

    def unregister(
        self,
        stage: PipelineStage,
    ) -> None:
        if stage in self._runners:
            del self._runners[stage]

    def resolve(
        self,
        stage: PipelineStage,
    ) -> PipelineRunner:
        runner = self._runners.get(stage)

        if runner is None:
            raise ValueError(f"Pipeline stage not registered: {stage}")

        return runner

    def exists(
        self,
        stage: PipelineStage,
    ) -> bool:
        return stage in self._runners

    def list_stages(self) -> list[PipelineStage]:
        return list(self._runners.keys())

    def describe(self) -> list[dict]:
        return [
            runner.metadata()
            for runner in self._runners.values()
        ]

    def run(
        self,
        stage: PipelineStage,
        context: PipelineExecutionContext,
    ) -> PipelineResult:
        runner = self.resolve(stage)
        return runner.run(context)