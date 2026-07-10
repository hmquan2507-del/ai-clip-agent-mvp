from __future__ import annotations

from app.render.ffmpeg.instructions.enums import (
    FFmpegInstructionStatus,
    FFmpegInstructionType,
)
from app.render.ffmpeg.instructions.models import (
    FFmpegInstructionIssue,
    FFmpegInstructionPlan,
)


class FFmpegInstructionPlanValidator:
    def validate(
        self,
        plan: FFmpegInstructionPlan,
    ) -> FFmpegInstructionPlan:
        issues = list(plan.issues)

        input_ids = {
            item.input_id
            for item in plan.inputs
        }

        instruction_ids: set[str] = set()

        for instruction in plan.instructions:
            instruction_valid = True

            if (
                instruction.instruction_id
                in instruction_ids
            ):
                issues.append(
                    FFmpegInstructionIssue(
                        level="error",
                        code="duplicate_instruction_id",
                        message=(
                            "FFmpeg instruction IDs "
                            "must be unique."
                        ),
                        instruction_id=(
                            instruction.instruction_id
                        ),
                    )
                )
                instruction_valid = False
            else:
                instruction_ids.add(
                    instruction.instruction_id
                )

            if instruction.start_time < 0:
                issues.append(
                    FFmpegInstructionIssue(
                        level="error",
                        code="negative_start_time",
                        message=(
                            "FFmpeg instruction start_time "
                            "cannot be negative."
                        ),
                        instruction_id=(
                            instruction.instruction_id
                        ),
                    )
                )
                instruction_valid = False

            if (
                instruction.end_time
                <= instruction.start_time
            ):
                issues.append(
                    FFmpegInstructionIssue(
                        level="error",
                        code="invalid_time_range",
                        message=(
                            "FFmpeg instruction end_time "
                            "must be greater than start_time."
                        ),
                        instruction_id=(
                            instruction.instruction_id
                        ),
                    )
                )
                instruction_valid = False

            if (
                instruction.source_input_id
                and instruction.source_input_id
                not in input_ids
            ):
                issues.append(
                    FFmpegInstructionIssue(
                        level="error",
                        code="missing_input",
                        message=(
                            "FFmpeg instruction references "
                            "an unknown input."
                        ),
                        instruction_id=(
                            instruction.instruction_id
                        ),
                        metadata={
                            "source_input_id": (
                                instruction.source_input_id
                            ),
                        },
                    )
                )
                instruction_valid = False

            for dependency in (
                instruction.dependencies
            ):
                if dependency not in instruction_ids:
                    dependency_exists = any(
                        item.instruction_id
                        == dependency
                        for item in plan.instructions
                    )

                    if not dependency_exists:
                        issues.append(
                            FFmpegInstructionIssue(
                                level="error",
                                code=(
                                    "missing_instruction_dependency"
                                ),
                                message=(
                                    "FFmpeg instruction "
                                    "dependency does not exist."
                                ),
                                instruction_id=(
                                    instruction.instruction_id
                                ),
                                metadata={
                                    "dependency": dependency,
                                },
                            )
                        )
                        instruction_valid = False

            instruction.status = (
                FFmpegInstructionStatus.VALID
                if instruction_valid
                else FFmpegInstructionStatus.INVALID
            )

        encode_count = sum(
            1
            for instruction in plan.instructions
            if self._value(
                instruction.instruction_type
            )
            == FFmpegInstructionType.ENCODE.value
        )

        if encode_count != 1:
            issues.append(
                FFmpegInstructionIssue(
                    level="error",
                    code="invalid_encode_count",
                    message=(
                        "FFmpeg plan must contain exactly "
                        "one encode instruction."
                    ),
                    metadata={
                        "encode_count": encode_count,
                    },
                )
            )

        plan.issues = issues

        plan.metadata = {
            **plan.metadata,
            "issue_count": len(issues),
            "valid": not any(
                issue.level == "error"
                for issue in issues
            ),
            "valid_instruction_count": sum(
                1
                for instruction
                in plan.instructions
                if self._value(instruction.status)
                == FFmpegInstructionStatus.VALID.value
            ),
        }

        return plan

    def _value(self, value) -> str:
        return (
            value.value
            if hasattr(value, "value")
            else str(value)
        )