from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.media.validation import MediaValidationRuntime
from app.timeline.compiler.models import (
    ExecutionTimeline,
    TimelineCompilerIssue,
)


@dataclass
class TimelineReadinessResult:
    compile_ready: bool
    assets_resolved: bool
    media_validated: bool
    render_ready: bool
    issues: list[TimelineCompilerIssue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "compile_ready": self.compile_ready,
            "assets_resolved": self.assets_resolved,
            "media_validated": self.media_validated,
            "render_ready": self.render_ready,
            "issues": [issue.to_dict() for issue in self.issues],
            "metadata": self.metadata,
        }


class TimelineReadinessValidator:
    def __init__(
        self,
        media_validator: MediaValidationRuntime | None = None,
    ):
        self.media_validator = (
            media_validator or MediaValidationRuntime()
        )

    def validate(
        self,
        execution: ExecutionTimeline,
    ) -> TimelineReadinessResult:
        issues = list(execution.issues)

        compile_ready = not any(
            issue.level == "error"
            for issue in execution.issues
        )

        assets_resolved = True
        media_validated = True
        validated_input_count = 0

        for timeline_input in execution.inputs:
            if not timeline_input.local_path:
                assets_resolved = False
                media_validated = False

                issues.append(
                    TimelineCompilerIssue(
                        level="error",
                        code="input_path_missing",
                        message="Timeline input has no local path.",
                        source_id=timeline_input.input_id,
                    )
                )
                continue

            validation = self.media_validator.validate(
                local_path=timeline_input.local_path,
                require_video=timeline_input.input_type == "video",
            )

            validated_input_count += 1

            if not validation.valid:
                media_validated = False

                issues.append(
                    TimelineCompilerIssue(
                        level="error",
                        code="media_validation_failed",
                        message=(
                            "Media input failed ffprobe validation."
                        ),
                        source_id=timeline_input.input_id,
                        metadata=validation.to_dict(),
                    )
                )

        render_ready = (
            compile_ready
            and assets_resolved
            and media_validated
        )

        return TimelineReadinessResult(
            compile_ready=compile_ready,
            assets_resolved=assets_resolved,
            media_validated=media_validated,
            render_ready=render_ready,
            issues=issues,
            metadata={
                "input_count": len(execution.inputs),
                "validated_input_count": validated_input_count,
            },
        )