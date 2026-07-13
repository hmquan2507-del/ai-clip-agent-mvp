from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.product.adapters import (
    ProductPreviewSummary,
    ProductQualitySummary,
    ProductTimelineSummary,
    ProductWorkspaceSnapshot,
)
from app.product.contracts import (
    ProductProductionSnapshot,
    ProductProgress,
)
from app.review import (
    ReviewRuntimeSession,
    build_review_runtime_graph,
)
from app.review.selection import (
    TimelineSelectionCatalog,
)


PRODUCTION_ID = (
    "221e4b01-5fb9-4b4a-a549-4fb32c455059"
)


def build_snapshot() -> ProductWorkspaceSnapshot:
    return ProductWorkspaceSnapshot(
        production=ProductProductionSnapshot(
            production_id=PRODUCTION_ID,
            name="Synchronization test",
            status="completed",
            stage="review",
            progress=ProductProgress(
                stage="review",
                progress=100.0,
                message="Ready",
                status="completed",
            ),
        ),
        timeline=ProductTimelineSummary(
            available=True,
            version="16.1.7",
            duration=8.0,
            track_count=2,
            clip_count=2,
            canvas={
                "width": 1080,
                "height": 1920,
                "fps": 30.0,
            },
            tracks=[
                {
                    "track_id": "video_primary",
                    "track_type": "video_primary",
                    "position": 0,
                    "clips": [
                        {
                            "clip_id": "clip_1",
                            "track_id": "video_primary",
                            "clip_type": "video",
                            "start_time": 0.0,
                            "end_time": 4.0,
                            "source_start": 0.0,
                            "source_end": 4.0,
                            "source_duration": 20.0,
                        },
                        {
                            "clip_id": "clip_2",
                            "track_id": "video_primary",
                            "clip_type": "video",
                            "start_time": 4.0,
                            "end_time": 8.0,
                            "source_start": 4.0,
                            "source_end": 8.0,
                            "source_duration": 20.0,
                        },
                    ],
                },
                {
                    "track_id": "video_overlay",
                    "track_type": "video_overlay",
                    "position": 1,
                    "clips": [],
                },
            ],
        ),
        preview=ProductPreviewSummary(
            available=True,
            video_path="storage/render/final.mp4",
            duration=8.0,
            width=1080,
            height=1920,
            fps=30.0,
        ),
        quality=ProductQualitySummary(
            available=True,
            approved=True,
            quality_score=100.0,
        ),
    )


def main() -> None:
    source = build_snapshot()
    source_before = deepcopy(
        source.to_dict()
    )

    graph = build_review_runtime_graph(
        source
    )

    captured_events = []
    session = ReviewRuntimeSession(
        graph,
        event_callback=(
            captured_events.append
        ),
    )

    initial_ready = (
        session.state.ready
        and session.preview_sync.current
        and not session.preview_sync.stale
        and session.state.timeline_revision
        == 1
    )

    selected = (
        graph.selection_runtime.select_clip(
            "clip_2"
        )
    )

    session_revision_before_failure = (
        session.state.revision
    )
    event_count_before_failure = len(
        session.events
    )

    failed_move = (
        graph.mutation_runtime.move_clip(
            "clip_2",
            2.0,
            target_track_id=(
                "video_primary"
            ),
        )
    )

    failure_no_sync = (
        not failed_move.success
        and session.state.revision
        == session_revision_before_failure
        and len(session.events)
        == event_count_before_failure
    )

    delete_result = (
        graph.history_runtime.delete_clip(
            "clip_2"
        )
    )

    selection_after_delete = (
        graph.selection_runtime.state
    )

    delete_synchronized = (
        selected.success
        and delete_result.success
        and "clip_2"
        not in graph.selection_runtime
        .catalog.clip_ids
        and "clip_2"
        not in selection_after_delete
        .selected_clip_ids
        and selection_after_delete
        .active_clip_id
        is None
        and session.preview_sync.stale
        and session.state.timeline_revision
        == graph.timeline_store.revision
    )

    undo_result = graph.history_runtime.undo()

    undo_synchronized = (
        undo_result.success
        and "clip_2"
        in graph.selection_runtime
        .catalog.clip_ids
        and graph.selection_runtime
        .catalog.get_clip("clip_2")
        is not None
        and session.preview_sync.current
    )

    trim_result = (
        graph.history_runtime.trim_clip_end(
            "clip_2",
            7.0,
        )
    )

    trimmed_catalog_clip = (
        graph.selection_runtime.catalog
        .get_clip("clip_2")
    )

    timing_synchronized = (
        trim_result.success
        and trimmed_catalog_clip is not None
        and trimmed_catalog_clip.end_time
        == 7.0
        and session.preview_sync.stale
    )

    undo_trim = graph.history_runtime.undo()

    preview_signature_safe = (
        undo_trim.success
        and session.preview_sync.current
    )

    catalog_before_mismatch = deepcopy(
        graph.selection_runtime.catalog
    )
    state_before_mismatch = (
        graph.selection_runtime.state
    )

    mismatch_result = (
        graph.selection_runtime
        .synchronize_catalog(
            TimelineSelectionCatalog(
                production_id=(
                    "different-production"
                ),
                duration=0.0,
            )
        )
    )

    mismatch_atomic = (
        not mismatch_result.success
        and graph.selection_runtime
        .catalog.to_dict()
        == catalog_before_mismatch.to_dict()
        and graph.selection_runtime
        .state.selected_clip_ids
        == state_before_mismatch
        .selected_clip_ids
    )

    state_payload = session.state.to_dict()
    state_payload["metadata"]["runtime"] = (
        "changed_outside"
    )
    event_payload = session.events[-1].to_dict()
    event_payload["metadata"]["preview_sync_status"] = (
        "changed_outside"
    )

    session_outputs_isolated = (
        session.state.metadata["runtime"]
        == "ReviewRuntimeSession"
        and session.events[-1]
        .metadata.get("preview_sync_status")
        != "changed_outside"
    )

    source_unchanged = (
        source.to_dict() == source_before
    )

    session_event_count_before_close = len(
        session.events
    )
    selection_clip_count_before_close = len(
        graph.selection_runtime.catalog.clips
    )

    close_result = session.close()

    delete_after_close = (
        graph.history_runtime.delete_clip(
            "clip_2"
        )
    )

    close_unsubscribed = (
        close_result.success
        and session.closed
        and delete_after_close.success
        and len(session.events)
        == session_event_count_before_close + 1
        and len(
            graph.selection_runtime
            .catalog.clips
        )
        == selection_clip_count_before_close
    )

    event_callback_works = (
        len(captured_events)
        == len(session.events)
    )

    output_payload = session.to_dict()

    output = Path(
        "storage/demo_outputs/"
        "review_runtime_state_synchronization.json"
    )
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output.write_text(
        json.dumps(
            output_payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        "=== Review Runtime State Synchronization ==="
    )
    print("initial_ready:", initial_ready)
    print(
        "failure_no_sync:",
        failure_no_sync,
    )
    print(
        "delete_synchronized:",
        delete_synchronized,
    )
    print(
        "undo_synchronized:",
        undo_synchronized,
    )
    print(
        "timing_synchronized:",
        timing_synchronized,
    )
    print(
        "preview_signature_safe:",
        preview_signature_safe,
    )
    print(
        "mismatch_atomic:",
        mismatch_atomic,
    )
    print(
        "session_outputs_isolated:",
        session_outputs_isolated,
    )
    print(
        "source_unchanged:",
        source_unchanged,
    )
    print(
        "close_unsubscribed:",
        close_unsubscribed,
    )
    print(
        "event_callback_works:",
        event_callback_works,
    )
    print("output:", output)

    assert initial_ready
    assert failure_no_sync
    assert delete_synchronized
    assert undo_synchronized
    assert timing_synchronized
    assert preview_signature_safe
    assert mismatch_atomic
    assert session_outputs_isolated
    assert source_unchanged
    assert close_unsubscribed
    assert event_callback_works

    print()
    print(
        "DONE: Review runtime state "
        "synchronization test completed."
    )


if __name__ == "__main__":
    main()