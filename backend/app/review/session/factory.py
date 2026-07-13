from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.product.adapters import (
    ProductWorkspaceSnapshot,
)
from app.review.builders.workspace_builder import (
    ReviewWorkspaceBuilder,
)
from app.review.editing.clipboard.factory import (
    build_clipboard_from_history_runtime,
)
from app.review.editing.factories import (
    build_editable_timeline,
    build_editable_timeline_from_workspace,
)
from app.review.editing.models import (
    EditableTimeline,
)
from app.review.editing.history.factory import (
    build_history_from_mutation_runtime,
)
from app.review.editing.runtime import (
    build_mutation_runtime_from_store,
)
from app.review.editing.state.factory import (
    build_timeline_runtime_store,
)
from app.review.editing.validator import (
    TimelineEditingValidator,
)
from app.review.models import ReviewWorkspace
from app.review.preview.factory import (
    build_preview_session_from_workspace,
    build_preview_session_runtime,
)
from app.review.preview.models import (
    PreviewSessionConfig,
)
from app.review.preview.runtime import (
    PreviewEventCallback,
    PreviewSessionRuntime,
)
from app.review.selection.factory import (
    build_timeline_selection_runtime,
)
from app.review.selection.runtime import (
    TimelineSelectionEventCallback,
)
from app.review.session.graph import (
    ReviewRuntimeGraph,
)


ReviewRuntimeGraphSource = (
    ProductWorkspaceSnapshot
    | ReviewWorkspace
)


def build_review_runtime_graph(
    source: ReviewRuntimeGraphSource,
    *,
    workspace_builder: (
        ReviewWorkspaceBuilder | None
    ) = None,
    validator: (
        TimelineEditingValidator | None
    ) = None,
    preview_config: (
        PreviewSessionConfig | None
    ) = None,
    preview_event_callback: (
        PreviewEventCallback | None
    ) = None,
    selection_event_callback: (
        TimelineSelectionEventCallback | None
    ) = None,
    maximum_history_size: int = 100,
    maximum_clipboard_history_size: int = 20,
) -> ReviewRuntimeGraph:
    source_copy = deepcopy(source)

    workspace = _build_review_workspace(
        source_copy,
        workspace_builder=workspace_builder,
    )

    timeline = _build_editable_timeline(
        source_copy,
        workspace,
    )

    preview_runtime = _build_preview_runtime(
        source_copy,
        workspace,
        config=preview_config,
        event_callback=(
            preview_event_callback
        ),
    )

    selection_runtime = (
        build_timeline_selection_runtime(
            production_id=(
                timeline.production_id
            ),
            duration=timeline.duration,
            tracks=timeline.tracks,
            fps=timeline.fps,
            event_callback=(
                selection_event_callback
            ),
        )
    )

    store = build_timeline_runtime_store(
        timeline
    )

    mutation_runtime = (
        build_mutation_runtime_from_store(
            store,
            validator=validator,
        )
    )

    history_runtime = (
        build_history_from_mutation_runtime(
            mutation_runtime,
            maximum_history_size=(
                maximum_history_size
            ),
        )
    )

    clipboard_runtime = (
        build_clipboard_from_history_runtime(
            history_runtime,
            maximum_history_size=(
                maximum_clipboard_history_size
            ),
        )
    )

    graph = ReviewRuntimeGraph(
        workspace=workspace,
        preview_runtime=preview_runtime,
        selection_runtime=selection_runtime,
        timeline_store=store,
        mutation_runtime=mutation_runtime,
        history_runtime=history_runtime,
        clipboard_runtime=clipboard_runtime,
    )

    graph.validate()
    return graph


def build_review_runtime_graph_from_snapshot(
    snapshot: ProductWorkspaceSnapshot,
    **kwargs: Any,
) -> ReviewRuntimeGraph:
    return build_review_runtime_graph(
        snapshot,
        **kwargs,
    )


def build_review_runtime_graph_from_workspace(
    workspace: ReviewWorkspace,
    **kwargs: Any,
) -> ReviewRuntimeGraph:
    return build_review_runtime_graph(
        workspace,
        **kwargs,
    )


def _build_review_workspace(
    source: ReviewRuntimeGraphSource,
    *,
    workspace_builder: (
        ReviewWorkspaceBuilder | None
    ),
) -> ReviewWorkspace:
    if isinstance(
        source,
        ReviewWorkspace,
    ):
        return deepcopy(source)

    builder = (
        workspace_builder
        or ReviewWorkspaceBuilder()
    )

    return deepcopy(
        builder.build_from_snapshot(source)
    )


def _build_editable_timeline(
    source: ReviewRuntimeGraphSource,
    workspace: ReviewWorkspace,
) -> EditableTimeline:
    if isinstance(
        source,
        ProductWorkspaceSnapshot,
    ):
        return (
            build_editable_timeline_from_workspace(
                source
            )
        )

    return build_editable_timeline(
        production_id=(
            workspace.production_id
        ),
        tracks=deepcopy(
            workspace.timeline.tracks
        ),
        duration=float(
            workspace.timeline.duration
            or 0.0
        ),
        fps=float(
            workspace.preview.fps
            or 30.0
        ),
        width=workspace.preview.width,
        height=workspace.preview.height,
        version=str(
            workspace.timeline.version
            or "16.1.7"
        ),
    )


def _build_preview_runtime(
    source: ReviewRuntimeGraphSource,
    workspace: ReviewWorkspace,
    *,
    config: PreviewSessionConfig | None,
    event_callback: PreviewEventCallback | None,
) -> PreviewSessionRuntime:
    if isinstance(
        source,
        ProductWorkspaceSnapshot,
    ):
        return build_preview_session_from_workspace(
            source,
            config=config,
            event_callback=event_callback,
        )

    return build_preview_session_runtime(
        production_id=(
            workspace.production_id
        ),
        video_url=(
            workspace.preview.video_url
        ),
        duration=float(
            workspace.preview.duration
            or 0.0
        ),
        width=workspace.preview.width,
        height=workspace.preview.height,
        fps=float(
            workspace.preview.fps
            or 30.0
        ),
        config=config,
        event_callback=event_callback,
        metadata={
            "source": "review_workspace",
        },
    )