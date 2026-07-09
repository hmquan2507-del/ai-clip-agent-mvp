from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.planner.models import EditingPlan, PlannerInstructionType


@dataclass
class PlannerValidationIssue:
    level: str
    code: str
    message: str
    instruction_index: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlannerValidationResult:
    valid: bool
    issues: list[PlannerValidationIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "issues": [issue.__dict__ for issue in self.issues],
        }


class PlannerValidator:
    def validate(self, plan: EditingPlan) -> PlannerValidationResult:
        issues: list[PlannerValidationIssue] = []

        for index, instruction in enumerate(plan.instructions):
            if instruction.end_time <= instruction.start_time:
                issues.append(
                    PlannerValidationIssue(
                        level="error",
                        code="invalid_time_range",
                        message="Instruction end_time must be greater than start_time.",
                        instruction_index=index,
                    )
                )

            if instruction.instruction_type in {
                PlannerInstructionType.BROLL,
                PlannerInstructionType.MUSIC,
                PlannerInstructionType.SOUND_EFFECT,
            } and not instruction.query:
                issues.append(
                    PlannerValidationIssue(
                        level="error",
                        code="missing_query",
                        message="Media instruction requires a query.",
                        instruction_index=index,
                    )
                )

            if instruction.instruction_type == PlannerInstructionType.BROLL:
                if instruction.track_type != "broll":
                    issues.append(
                        PlannerValidationIssue(
                            level="warning",
                            code="broll_track_type_mismatch",
                            message="B-roll instruction should use track_type='broll'.",
                            instruction_index=index,
                        )
                    )

            if instruction.confidence < 0.3:
                issues.append(
                    PlannerValidationIssue(
                        level="warning",
                        code="low_confidence",
                        message="Instruction confidence is low.",
                        instruction_index=index,
                    )
                )

        valid = not any(issue.level == "error" for issue in issues)

        return PlannerValidationResult(valid=valid, issues=issues)