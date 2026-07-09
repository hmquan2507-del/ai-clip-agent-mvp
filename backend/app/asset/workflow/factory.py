from __future__ import annotations

from app.asset.workflow.runtime import MediaWorkflowRuntime


def build_media_workflow_runtime() -> MediaWorkflowRuntime:
    return MediaWorkflowRuntime()