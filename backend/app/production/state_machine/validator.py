from __future__ import annotations

from app.production.contracts import PipelineStage


class ProductionStateMachineValidator:
    def validate_pipeline(
        self,
        stages: list[PipelineStage],
    ) -> list[str]:
        errors: list[str] = []

        if not stages:
            errors.append("pipeline_has_no_stages")
            return errors

        seen: set[PipelineStage] = set()

        for stage in stages:
            if stage in seen:
                errors.append(f"duplicate_stage:{stage.value}")

            seen.add(stage)

        return errors