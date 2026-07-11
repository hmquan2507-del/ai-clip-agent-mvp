from __future__ import annotations

from app.render.execution.recovery.classifier import (
    RenderFailureClassifier,
)
from app.render.execution.recovery.cleanup import (
    RenderCleanupRuntime,
)
from app.render.execution.recovery.models import (
    RenderRetryPolicy,
)
from app.render.execution.recovery.runtime import (
    RenderRecoveryRuntime,
)


def build_render_failure_classifier() -> (
    RenderFailureClassifier
):
    return RenderFailureClassifier()


def build_render_cleanup_runtime() -> (
    RenderCleanupRuntime
):
    return RenderCleanupRuntime()


def build_render_recovery_runtime(
    retry_policy: RenderRetryPolicy | None = None,
) -> RenderRecoveryRuntime:
    return RenderRecoveryRuntime(
        retry_policy=(
            retry_policy or RenderRetryPolicy()
        )
    )