from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.production.contracts import PipelineStage


@dataclass(slots=True)
class ProductionResumeResult:
    production_id: str

    should_resume: bool

    resume_stage: PipelineStage | None

    completed_stages: list[PipelineStage]

    remaining_stages: list[PipelineStage]

    metadata: dict[str, Any]

    @property
    def is_finished(self) -> bool:
        return (
            not self.should_resume
            and self.resume_stage is None
            and not self.remaining_stages
        )