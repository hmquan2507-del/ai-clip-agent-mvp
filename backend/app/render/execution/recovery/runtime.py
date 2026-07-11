from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Callable

from app.render.execution.context import RenderContext
from app.render.execution.recovery.classifier import (
    RenderFailureClassifier,
)
from app.render.execution.recovery.cleanup import (
    RenderCleanupRuntime,
)
from app.render.execution.recovery.enums import (
    RenderRetryDecision,
)
from app.render.execution.recovery.models import (
    RenderRecoveryResult,
    RenderRetryAttempt,
    RenderRetryPolicy,
)
from app.render.ffmpeg.execution import (
    FFmpegExecutionResult,
    FFmpegRenderPipeline,
)


ProgressCallback = Callable[
    [object],
    None,
]


class RenderRecoveryRuntime:
    def __init__(
        self,
        pipeline: FFmpegRenderPipeline | None = None,
        classifier: RenderFailureClassifier | None = None,
        cleanup_runtime: RenderCleanupRuntime | None = None,
        retry_policy: RenderRetryPolicy | None = None,
    ):
        self.pipeline = (
            pipeline or FFmpegRenderPipeline()
        )
        self.classifier = (
            classifier or RenderFailureClassifier()
        )
        self.cleanup_runtime = (
            cleanup_runtime or RenderCleanupRuntime()
        )
        self.retry_policy = (
            retry_policy or RenderRetryPolicy()
        )

    def render_with_recovery(
        self,
        context: RenderContext,
        progress_callback: ProgressCallback | None = None,
    ) -> RenderRecoveryResult:
        attempts: list[RenderRetryAttempt] = []

        final_execution_result: (
            FFmpegExecutionResult | None
        ) = None

        final_error: str | None = None

        for attempt_number in range(
            1,
            self.retry_policy.max_attempts + 1,
        ):
            started_at = self._now()
            started_counter = perf_counter()

            cleanup_paths: list[str] = []

            try:
                pipeline_result = self.pipeline.render(
                    context=context,
                    progress_callback=progress_callback,
                )

                execution_result = (
                    pipeline_result.execution_result
                )

                final_execution_result = (
                    execution_result
                )

                if execution_result.success:
                    attempts.append(
                        RenderRetryAttempt(
                            attempt_number=attempt_number,
                            started_at=started_at,
                            finished_at=self._now(),
                            success=True,
                            duration_seconds=round(
                                perf_counter()
                                - started_counter,
                                6,
                            ),
                            output_path=(
                                execution_result.output_path
                            ),
                            metadata={
                                "returncode": (
                                    execution_result.returncode
                                ),
                                "issue_count": len(
                                    execution_result.issues
                                ),
                            },
                        )
                    )

                    success_cleanup = (
                        self.cleanup_runtime
                        .cleanup_after_success(
                            context=context,
                            remove_temp=True,
                            remove_working_prepared_inputs=False,
                        )
                    )

                    diagnostics_path = (
                        self._write_diagnostics(
                            context=context,
                            attempts=attempts,
                            success=True,
                            final_error=None,
                        )
                    )

                    return RenderRecoveryResult(
                        production_id=(
                            context.production_id
                        ),
                        success=True,
                        attempt_count=len(attempts),
                        attempts=attempts,
                        final_output_path=(
                            execution_result.output_path
                        ),
                        diagnostics_path=(
                            diagnostics_path
                        ),
                        metadata={
                            "runtime": (
                                "RenderRecoveryRuntime"
                            ),
                            "retry_policy": (
                                self.retry_policy.to_dict()
                            ),
                            "success_cleanup": (
                                success_cleanup.to_dict()
                            ),
                        },
                    )

                classification = (
                    self.classifier.classify(
                        result=execution_result,
                        policy=self.retry_policy,
                        attempt_number=attempt_number,
                    )
                )

                final_error = (
                    classification.reason
                )

                cleanup_result = (
                    self.cleanup_runtime.cleanup(
                        context=context,
                        mode=(
                            classification.cleanup_mode
                        ),
                        preserve_diagnostics=True,
                    )
                )

                cleanup_paths = list(
                    cleanup_result.removed_paths
                )

                attempts.append(
                    RenderRetryAttempt(
                        attempt_number=attempt_number,
                        started_at=started_at,
                        finished_at=self._now(),
                        success=False,
                        duration_seconds=round(
                            perf_counter()
                            - started_counter,
                            6,
                        ),
                        category=self._value(
                            classification.category
                        ),
                        retry_decision=self._value(
                            classification.retry_decision
                        ),
                        error=classification.reason,
                        output_path=(
                            execution_result.output_path
                        ),
                        cleanup_paths=cleanup_paths,
                        metadata={
                            "classification": (
                                classification.to_dict()
                            ),
                            "cleanup": (
                                cleanup_result.to_dict()
                            ),
                            "returncode": (
                                execution_result.returncode
                            ),
                            "execution_issues": [
                                issue.to_dict()
                                for issue
                                in execution_result.issues
                            ],
                        },
                    )
                )

                should_retry = (
                    self._value(
                        classification.retry_decision
                    )
                    in {
                        RenderRetryDecision.RETRY.value,
                        RenderRetryDecision
                        .RETRY_AFTER_CLEANUP.value,
                    }
                    and attempt_number
                    < self.retry_policy.max_attempts
                )

                if not should_retry:
                    break

                delay = max(
                    0.0,
                    classification.retry_delay_seconds,
                )

                if delay > 0:
                    time.sleep(delay)

            except Exception as error:
                final_error = str(error)

                cleanup_result = (
                    self.cleanup_runtime.cleanup(
                        context=context,
                        mode="partial",
                        preserve_diagnostics=True,
                    )
                )

                attempts.append(
                    RenderRetryAttempt(
                        attempt_number=attempt_number,
                        started_at=started_at,
                        finished_at=self._now(),
                        success=False,
                        duration_seconds=round(
                            perf_counter()
                            - started_counter,
                            6,
                        ),
                        category="unknown",
                        retry_decision=(
                            "do_not_retry"
                        ),
                        error=str(error),
                        cleanup_paths=list(
                            cleanup_result.removed_paths
                        ),
                        metadata={
                            "unhandled_exception": True,
                            "cleanup": (
                                cleanup_result.to_dict()
                            ),
                        },
                    )
                )

                break

        diagnostics_path = self._write_diagnostics(
            context=context,
            attempts=attempts,
            success=False,
            final_error=final_error,
        )

        return RenderRecoveryResult(
            production_id=context.production_id,
            success=False,
            attempt_count=len(attempts),
            attempts=attempts,
            final_output_path=(
                final_execution_result.output_path
                if (
                    final_execution_result
                    and final_execution_result.success
                )
                else None
            ),
            final_error=final_error,
            diagnostics_path=diagnostics_path,
            metadata={
                "runtime": "RenderRecoveryRuntime",
                "retry_policy": (
                    self.retry_policy.to_dict()
                ),
                "max_attempts_reached": (
                    len(attempts)
                    >= self.retry_policy.max_attempts
                ),
            },
        )

    def _write_diagnostics(
        self,
        context: RenderContext,
        attempts: list[RenderRetryAttempt],
        success: bool,
        final_error: str | None,
    ) -> str:
        path = (
            Path(context.artifact_directory)
            / "recovery_diagnostics.json"
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "production_id": context.production_id,
            "success": success,
            "attempt_count": len(attempts),
            "attempts": [
                item.to_dict()
                for item in attempts
            ],
            "final_error": final_error,
            "created_at": self._now(),
        }

        path.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        context.metadata = {
            **context.metadata,
            "recovery_diagnostics_path": (
                str(path)
            ),
            "render_attempt_count": (
                len(attempts)
            ),
        }

        return str(path)

    def _value(self, value) -> str:
        return (
            value.value
            if hasattr(value, "value")
            else str(value)
        )

    def _now(self) -> str:
        return datetime.now(
            timezone.utc
        ).isoformat()