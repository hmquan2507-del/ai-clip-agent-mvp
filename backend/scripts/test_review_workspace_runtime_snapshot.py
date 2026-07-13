from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.review import (
    ReviewRuntimeSession,
    build_review_runtime_graph,
)
from test_review_runtime_state_synchronization import (
    build_snapshot as build_product_snapshot,
)


def main() -> None:
    source = build_product_snapshot()
    graph = build_review_runtime_graph(source)
    session = ReviewRuntimeSession(graph)

    select_result = (
        graph.selection_runtime.select_clip(
            "clip_2"
        )
    )
    copy_result = (
        graph.clipboard_runtime.copy_clip(
            "clip_2"
        )
    )
    trim_result = (
        graph.history_runtime.trim_clip_end(
            "clip_2",
            7.0,
        )
    )

    event_count_before = len(session.events)
    change_count_before = len(
        graph.timeline_store.changes
    )

    snapshot = session.snapshot()
    second_snapshot = session.snapshot()

    snapshot_read_only = (
        len(session.events)
        == event_count_before
        and len(graph.timeline_store.changes)
        == change_count_before
    )

    production_ids_match = (
        snapshot.production_ids_match
    )

    workspace_timeline_current = (
        snapshot.workspace_timeline_consistent
        and snapshot.workspace.timeline
        .clip_count
        == snapshot.timeline.clip_count
        and snapshot.workspace.timeline
        .tracks[0]["clips"][1]["end_time"]
        == 7.0
        and snapshot.timeline
        .get_clip("clip_2")
        .end_time
        == 7.0
    )

    selection_current = (
        select_result.success
        and snapshot.selection_state
        .selected_clip_ids
        == ["clip_2"]
        and snapshot.workspace.selection
        .selected_clip_ids
        == ["clip_2"]
        and snapshot.selection_catalog
        .get_clip("clip_2")
        .end_time
        == 7.0
    )

    preview_current = (
        snapshot.preview_sync.stale
        and snapshot.preview_sync
        .active_timeline_revision
        == snapshot.timeline.revision
        and snapshot.preview_source.available
    )

    history_current = (
        trim_result.success
        and snapshot.history_state.can_undo
        and snapshot.history_state.undo_count
        == 1
        and snapshot.history_state
        .current_revision
        == snapshot.timeline.revision
    )

    clipboard_current = (
        copy_result.success
        and snapshot.clipboard_state.available
        and snapshot.clipboard_state.item_count
        == 1
        and snapshot.clipboard_content.available
        and snapshot.clipboard_content
        .items[0].source_clip_id
        == "clip_2"
    )

    snapshot.timeline.get_clip(
        "clip_1"
    ).start_time = 3.0
    snapshot.workspace.timeline.tracks[0][
        "clips"
    ][0]["start_time"] = 3.0
    (
        snapshot.selection_state
        .selected_clip_ids.clear()
    )
    snapshot.preview_state.metadata[
        "changed_outside"
    ] = True
    snapshot.clipboard_content.items[
        0
    ].clip.start_time = 3.0

    snapshot_isolated = (
        graph.timeline_store.snapshot()
        .get_clip("clip_1")
        .start_time
        == 0.0
        and graph.selection_runtime.state
        .selected_clip_ids
        == ["clip_2"]
        and "changed_outside"
        not in graph.preview_runtime
        .state.metadata
        and graph.clipboard_runtime
        .content.items[0].clip.start_time
        == 4.0
    )

    repeated_snapshot_isolated = (
        second_snapshot.timeline
        .get_clip("clip_1")
        .start_time
        == 0.0
        and second_snapshot.workspace
        .timeline.tracks[0]["clips"][0]
        ["start_time"]
        == 0.0
        and second_snapshot.selection_state
        .selected_clip_ids
        == ["clip_2"]
    )

    payload = second_snapshot.to_dict()
    payload["timeline"]["tracks"][0][
        "clips"
    ][0]["start_time"] = 5.0
    payload["metadata"]["runtime"] = (
        "changed_outside"
    )

    payload_isolated = (
        second_snapshot.timeline
        .get_clip("clip_1")
        .start_time
        == 0.0
        and second_snapshot.metadata["runtime"]
        == "ReviewRuntimeSession"
    )

    mismatch_blocked = False

    try:
        invalid_selection_state = replace(
            second_snapshot.selection_state,
            production_id=(
                "different-production"
            ),
        )
        replace(
            second_snapshot,
            selection_state=(
                invalid_selection_state
            ),
        )
    except ValueError:
        mismatch_blocked = True

    close_result = session.close()
    closed_snapshot = session.snapshot()

    closed_snapshot_available = (
        close_result.success
        and closed_snapshot.session.closed
        and closed_snapshot.timeline
        .get_clip("clip_2")
        .end_time
        == 7.0
        and closed_snapshot
        .workspace_timeline_consistent
    )

    serialization_valid = (
        second_snapshot.to_dict()
        ["consistency"]
        ["production_ids_match"]
        and second_snapshot.to_dict()
        ["consistency"]
        ["workspace_timeline_consistent"]
        and second_snapshot.to_dict()
        ["metadata"]["contract_version"]
        == "16.1.7.4"
    )

    output = Path(
        "storage/demo_outputs/"
        "review_workspace_runtime_snapshot.json"
    )
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output.write_text(
        json.dumps(
            second_snapshot.to_dict(),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        "=== Review Workspace Runtime Snapshot ==="
    )
    print(
        "snapshot_read_only:",
        snapshot_read_only,
    )
    print(
        "production_ids_match:",
        production_ids_match,
    )
    print(
        "workspace_timeline_current:",
        workspace_timeline_current,
    )
    print(
        "selection_current:",
        selection_current,
    )
    print(
        "preview_current:",
        preview_current,
    )
    print(
        "history_current:",
        history_current,
    )
    print(
        "clipboard_current:",
        clipboard_current,
    )
    print(
        "snapshot_isolated:",
        snapshot_isolated,
    )
    print(
        "repeated_snapshot_isolated:",
        repeated_snapshot_isolated,
    )
    print(
        "payload_isolated:",
        payload_isolated,
    )
    print(
        "mismatch_blocked:",
        mismatch_blocked,
    )
    print(
        "closed_snapshot_available:",
        closed_snapshot_available,
    )
    print(
        "serialization_valid:",
        serialization_valid,
    )
    print("output:", output)

    assert snapshot_read_only
    assert production_ids_match
    assert workspace_timeline_current
    assert selection_current
    assert preview_current
    assert history_current
    assert clipboard_current
    assert snapshot_isolated
    assert repeated_snapshot_isolated
    assert payload_isolated
    assert mismatch_blocked
    assert closed_snapshot_available
    assert serialization_valid

    print()
    print(
        "DONE: Review workspace runtime "
        "snapshot test completed."
    )


if __name__ == "__main__":
    main()