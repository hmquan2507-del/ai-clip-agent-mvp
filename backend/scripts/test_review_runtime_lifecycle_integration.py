from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.review import (
    ReviewRuntimeSessionEventType,
    build_review_runtime_session,
    build_review_runtime_session_from_graph,
    build_review_runtime_graph,
)
from test_review_runtime_state_synchronization import (
    build_snapshot as build_product_snapshot,
)


def main() -> None:
    source = build_product_snapshot()
    source_before = deepcopy(
        source.to_dict()
    )

    captured_events = []
    session = build_review_runtime_session(
        source,
        session_event_callback=(
            captured_events.append
        ),
        maximum_history_size=25,
        maximum_clipboard_history_size=10,
    )

    second_graph = build_review_runtime_graph(
        source
    )
    second_session = (
        build_review_runtime_session_from_graph(
            second_graph
        )
    )

    create_ready = (
        session.state.ready
        and not session.closed
        and session.graph.shared_store
        and session.preview_sync.current
        and session.events[0].event_type
        == ReviewRuntimeSessionEventType
        .SESSION_CREATED
        and session.events[1].event_type
        == ReviewRuntimeSessionEventType
        .SESSION_READY
    )

    initial_snapshot = session.snapshot()

    initial_snapshot_valid = (
        initial_snapshot.production_ids_match
        and initial_snapshot
        .workspace_timeline_consistent
        and initial_snapshot.timeline
        .clip_count
        == 2
    )

    play_result = (
        session.graph.preview_runtime.play()
    )
    seek_result = (
        session.graph.preview_runtime.seek(
            3.0
        )
    )
    select_result = (
        session.graph.selection_runtime
        .select_clip("clip_1")
    )
    copy_result = (
        session.graph.clipboard_runtime
        .copy_clip("clip_1")
    )
    paste_result = (
        session.graph.clipboard_runtime.paste(
            at_time=8.0,
            target_track_id="video_overlay",
        )
    )

    paste_snapshot = session.snapshot()

    edit_flow_integrated = (
        play_result.success
        and seek_result.success
        and select_result.success
        and copy_result.success
        and paste_result.success
        and paste_snapshot.timeline
        .clip_count
        == 3
        and paste_snapshot
        .selection_catalog.clips
        and len(
            paste_snapshot
            .selection_catalog.clips
        )
        == 3
        and paste_snapshot.preview_sync.stale
        and paste_snapshot.history_state
        .can_undo
        and paste_snapshot.clipboard_state
        .available
    )

    undo_result = (
        session.graph.history_runtime.undo()
    )
    undo_snapshot = session.snapshot()

    redo_result = (
        session.graph.history_runtime.redo()
    )
    redo_snapshot = session.snapshot()

    undo_redo_integrated = (
        undo_result.success
        and undo_snapshot.timeline
        .clip_count
        == 2
        and undo_snapshot.preview_sync.current
        and redo_result.success
        and redo_snapshot.timeline
        .clip_count
        == 3
        and redo_snapshot.preview_sync.stale
    )

    second_session_isolated = (
        second_session.snapshot()
        .timeline.clip_count
        == 2
        and second_session.preview_sync.current
        and second_session.state.revision == 1
        and second_session.graph.timeline_store
        is not session.graph.timeline_store
    )

    reset_result = session.reset()
    reset_snapshot = session.snapshot()

    reset_integrated = (
        reset_result.success
        and reset_result.snapshot is not None
        and session.state.ready
        and reset_snapshot.timeline.clip_count
        == 2
        and reset_snapshot.timeline.revision
        == 1
        and not reset_snapshot.timeline.dirty
        and reset_snapshot.preview_sync.current
        and reset_snapshot.preview_state
        .current_time
        == 0.0
        and not reset_snapshot
        .selection_state.has_selection
        and not reset_snapshot.history_state
        .can_undo
        and not reset_snapshot.history_state
        .can_redo
        and not reset_snapshot
        .clipboard_state.available
        and len(
            session.graph.clipboard_runtime
            .history_entries
        )
        == 0
        and session.events[-1].event_type
        == ReviewRuntimeSessionEventType
        .SESSION_RESET
    )

    reset_payload = reset_result.to_dict()
    reset_result_serializable = (
        reset_payload["success"]
        and reset_payload["snapshot"]
        ["timeline"]["clip_count"]
        == 2
        and reset_payload["event"]
        ["event_type"]
        == "session_reset"
    )

    event_count_before_close = len(
        session.events
    )
    close_result = session.close()
    close_again_result = session.close()

    close_idempotent = (
        close_result.success
        and close_again_result.success
        and session.closed
        and len(session.events)
        == event_count_before_close + 1
        and session.events[-1].event_type
        == ReviewRuntimeSessionEventType
        .SESSION_CLOSED
    )

    state_before_closed_reset = (
        session.state
    )
    closed_reset_result = session.reset()

    closed_reset_blocked = (
        not closed_reset_result.success
        and session.state
        == state_before_closed_reset
        and session.snapshot()
        .timeline.clip_count
        == 2
    )

    callback_isolated = True

    if captured_events:
        captured_events[0].metadata[
            "changed_outside"
        ] = True
        callback_isolated = (
            "changed_outside"
            not in session.events[0].metadata
        )

    source_unchanged = (
        source.to_dict() == source_before
    )

    second_close = second_session.close()
    all_sessions_closed = (
        second_close.success
        and second_session.closed
        and session.closed
    )

    final_payload = {
        "session": session.to_dict(),
        "snapshot": (
            session.snapshot().to_dict()
        ),
        "checks": {
            "create_ready": create_ready,
            "initial_snapshot_valid": (
                initial_snapshot_valid
            ),
            "edit_flow_integrated": (
                edit_flow_integrated
            ),
            "undo_redo_integrated": (
                undo_redo_integrated
            ),
            "second_session_isolated": (
                second_session_isolated
            ),
            "reset_integrated": (
                reset_integrated
            ),
            "reset_result_serializable": (
                reset_result_serializable
            ),
            "close_idempotent": (
                close_idempotent
            ),
            "closed_reset_blocked": (
                closed_reset_blocked
            ),
            "callback_isolated": (
                callback_isolated
            ),
            "source_unchanged": (
                source_unchanged
            ),
            "all_sessions_closed": (
                all_sessions_closed
            ),
        },
    }

    output = Path(
        "storage/demo_outputs/"
        "review_runtime_lifecycle_integration.json"
    )
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output.write_text(
        json.dumps(
            final_payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        "=== Review Runtime Lifecycle Integration ==="
    )
    print("create_ready:", create_ready)
    print(
        "initial_snapshot_valid:",
        initial_snapshot_valid,
    )
    print(
        "edit_flow_integrated:",
        edit_flow_integrated,
    )
    print(
        "undo_redo_integrated:",
        undo_redo_integrated,
    )
    print(
        "second_session_isolated:",
        second_session_isolated,
    )
    print(
        "reset_integrated:",
        reset_integrated,
    )
    print(
        "reset_result_serializable:",
        reset_result_serializable,
    )
    print(
        "close_idempotent:",
        close_idempotent,
    )
    print(
        "closed_reset_blocked:",
        closed_reset_blocked,
    )
    print(
        "callback_isolated:",
        callback_isolated,
    )
    print(
        "source_unchanged:",
        source_unchanged,
    )
    print(
        "all_sessions_closed:",
        all_sessions_closed,
    )
    print("output:", output)

    assert create_ready
    assert initial_snapshot_valid
    assert edit_flow_integrated
    assert undo_redo_integrated
    assert second_session_isolated
    assert reset_integrated
    assert reset_result_serializable
    assert close_idempotent
    assert closed_reset_blocked
    assert callback_isolated
    assert source_unchanged
    assert all_sessions_closed

    print()
    print(
        "DONE: Review runtime lifecycle "
        "integration test completed."
    )


if __name__ == "__main__":
    main()