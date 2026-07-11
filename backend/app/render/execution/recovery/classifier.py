from __future__ import annotations

from app.render.execution.recovery.enums import (
    RenderCleanupMode,
    RenderFailureCategory,
    RenderRetryDecision,
)
from app.render.execution.recovery.models import (
    RenderFailureClassification,
    RenderRetryPolicy,
)
from app.render.ffmpeg.execution import (
    FFmpegExecutionResult,
)


class RenderFailureClassifier:
    def classify(
        self,
        result: FFmpegExecutionResult,
        policy: RenderRetryPolicy,
        attempt_number: int,
    ) -> RenderFailureClassification:
        codes = {
            issue.code
            for issue in result.issues
        }

        stderr = (
            result.stderr_tail or ""
        ).lower()

        if "ffmpeg_not_installed" in codes:
            return self._classification(
                category=(
                    RenderFailureCategory
                    .FFMPEG_NOT_INSTALLED
                ),
                decision=(
                    RenderRetryDecision.DO_NOT_RETRY
                ),
                cleanup=RenderCleanupMode.NONE,
                reason=(
                    "FFmpeg executable is unavailable."
                ),
            )

        if (
            "no space left on device" in stderr
            or "disk full" in stderr
        ):
            decision = (
                RenderRetryDecision.RETRY_AFTER_CLEANUP
                if policy.retry_disk_full
                else RenderRetryDecision.DO_NOT_RETRY
            )

            return self._classification(
                category=RenderFailureCategory.DISK_FULL,
                decision=decision,
                cleanup=RenderCleanupMode.FULL,
                reason="Render disk is full.",
                delay=policy.delay_for_attempt(
                    attempt_number
                ),
            )

        if (
            "permission denied" in stderr
            or "operation not permitted" in stderr
        ):
            return self._classification(
                category=(
                    RenderFailureCategory
                    .PERMISSION_DENIED
                ),
                decision=(
                    RenderRetryDecision.DO_NOT_RETRY
                ),
                cleanup=RenderCleanupMode.NONE,
                reason=(
                    "Render process has insufficient "
                    "filesystem permissions."
                ),
            )

        if "ffmpeg_timeout" in codes:
            decision = (
                RenderRetryDecision.RETRY_AFTER_CLEANUP
                if policy.retry_timeout
                else RenderRetryDecision.DO_NOT_RETRY
            )

            return self._classification(
                category=(
                    RenderFailureCategory.FFMPEG_TIMEOUT
                ),
                decision=decision,
                cleanup=RenderCleanupMode.PARTIAL,
                reason="FFmpeg execution timed out.",
                delay=policy.delay_for_attempt(
                    attempt_number
                ),
            )

        if "render_output_missing" in codes:
            decision = (
                RenderRetryDecision.RETRY_AFTER_CLEANUP
                if policy.retry_output_missing
                else RenderRetryDecision.DO_NOT_RETRY
            )

            return self._classification(
                category=(
                    RenderFailureCategory.OUTPUT_MISSING
                ),
                decision=decision,
                cleanup=RenderCleanupMode.PARTIAL,
                reason=(
                    "FFmpeg completed without producing "
                    "an output file."
                ),
                delay=policy.delay_for_attempt(
                    attempt_number
                ),
            )

        if "render_output_invalid" in codes:
            decision = (
                RenderRetryDecision.RETRY_AFTER_CLEANUP
                if policy.retry_output_invalid
                else RenderRetryDecision.DO_NOT_RETRY
            )

            return self._classification(
                category=(
                    RenderFailureCategory.OUTPUT_INVALID
                ),
                decision=decision,
                cleanup=RenderCleanupMode.PARTIAL,
                reason=(
                    "Rendered output failed media "
                    "validation."
                ),
                delay=policy.delay_for_attempt(
                    attempt_number
                ),
            )

        if (
            "killed" in stderr
            or result.returncode in {-9, 137}
        ):
            return self._classification(
                category=(
                    RenderFailureCategory.PROCESS_KILLED
                ),
                decision=(
                    RenderRetryDecision
                    .RETRY_AFTER_CLEANUP
                ),
                cleanup=RenderCleanupMode.PARTIAL,
                reason=(
                    "FFmpeg process was terminated."
                ),
                delay=policy.delay_for_attempt(
                    attempt_number
                ),
            )

        if (
            "ffmpeg_nonzero_exit" in codes
            or "ffmpeg_execution_exception" in codes
        ):
            decision = (
                RenderRetryDecision.RETRY_AFTER_CLEANUP
                if policy.retry_process_error
                else RenderRetryDecision.DO_NOT_RETRY
            )

            return self._classification(
                category=(
                    RenderFailureCategory
                    .FFMPEG_PROCESS_ERROR
                ),
                decision=decision,
                cleanup=RenderCleanupMode.PARTIAL,
                reason=(
                    "FFmpeg process returned an error."
                ),
                delay=policy.delay_for_attempt(
                    attempt_number
                ),
                metadata={
                    "returncode": result.returncode,
                },
            )

        return self._classification(
            category=RenderFailureCategory.UNKNOWN,
            decision=RenderRetryDecision.DO_NOT_RETRY,
            cleanup=RenderCleanupMode.PARTIAL,
            reason=(
                "Render failure could not be classified "
                "as retryable."
            ),
        )

    def _classification(
        self,
        category: RenderFailureCategory,
        decision: RenderRetryDecision,
        cleanup: RenderCleanupMode,
        reason: str,
        delay: float = 0.0,
        metadata: dict | None = None,
    ) -> RenderFailureClassification:
        return RenderFailureClassification(
            category=category,
            retry_decision=decision,
            cleanup_mode=cleanup,
            reason=reason,
            retry_delay_seconds=delay,
            metadata=metadata or {},
        )