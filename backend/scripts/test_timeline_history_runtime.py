from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__)
        .resolve()
        .parents[1]
    )
)

from app.review.editing import (
    EditableClipType,
    EditableTimeline,
    EditableTimelineClip,
    EditableTimelineTrack,
    EditableTrackType,
    TimelineOverlapPolicy,
    build_history_from_store,
    build_timeline_runtime_store,
)


PRODUCTION_ID = (
    "221e4b01-5fb9-4b4a-a549-4fb32c455059"
)


def build_timeline() -> EditableTimeline:
    return EditableTimeline(
        production_id=PRODUCTION_ID,
        duration=12.0,
        fps=30.0,
        tracks=[
            EditableTimelineTrack(
                track_id="video_primary",
                track_type=(
                    EditableTrackType
                    .VIDEO_PRIMARY
                ),
                overlap_policy=(
                    TimelineOverlapPolicy
                    .FORBID
                ),
                clips=[
                    EditableTimelineClip(
                        clip_id="clip_1",
                        track_id=(
                            "video_primary"
                        ),
                        clip_type=(
                            EditableClipType
                            .VIDEO
                        ),
                        start_time=0.0,
                        end_time=4.0,
                        source_start=0.0,
                        source_end=4.0,
                        source_duration=30.0,
                    ),
                    EditableTimelineClip(
                        clip_id="clip_2",
                        track_id=(
                            "video_primary"
                        ),
                        clip_type=(
                            EditableClipType
                            .VIDEO
                        ),
                        start_time=4.0,
                        end_time=8.0,
                        source_start=4.0,
                        source_end=8.0,
                        source_duration=30.0,
                    ),
                ],
            ),
            EditableTimelineTrack(
                track_id="video_overlay",
                track_type=(
                    EditableTrackType
                    .VIDEO_OVERLAY
                ),
                overlap_policy=(
                    TimelineOverlapPolicy.ALLOW
                ),
            ),
        ],
    )


def main() -> None:
    source_timeline = build_timeline()
    store = build_timeline_runtime_store(
        source_timeline
    )
    history = build_history_from_store(
        store,
        maximum_history_size=3,
    )

    print(
        "=== Timeline Command History ==="
    )

    initial_timeline = (
        history.timeline.to_dict()
    )

    move_result = history.move_clip(
        "clip_2",
        5.0,
        target_track_id=(
            "video_overlay"
        ),
    )

    trim_result = (
        history.trim_clip_start(
            "clip_1",
            1.0,
        )
    )

    duplicate_result = (
        history.duplicate_clip(
            "clip_2",
            new_clip_id="clip_2_copy",
            new_start_time=9.0,
        )
    )

    print(
        "move:",
        move_result.success,
    )
    print(
        "trim:",
        trim_result.success,
    )
    print(
        "duplicate:",
        duplicate_result.success,
    )
    print(
        "can_undo:",
        history.can_undo,
    )
    print(
        "can_redo:",
        history.can_redo,
    )

    after_edits = (
        history.timeline.to_dict()
    )

    clip_2_after_move = (
        history.timeline.get_clip(
            "clip_2"
        )
    )

    clip_1_after_trim = (
        history.timeline.get_clip(
            "clip_1"
        )
    )

    duplicate_after_create = (
        history.timeline.get_clip(
            "clip_2_copy"
        )
    )

    undo_duplicate = history.undo()

    clip_2_copy_after_undo = (
        history.timeline.get_clip(
            "clip_2_copy"
        )
    )

    undo_trim = history.undo()

    clip_1_after_undo_trim = (
        history.timeline.get_clip(
            "clip_1"
        )
    )

    undo_state = history.state()

    print(
        "undo_duplicate:",
        undo_duplicate.success,
    )
    print(
        "undo_trim:",
        undo_trim.success,
    )
    print(
        "undo_count:",
        undo_state.undo_count,
    )
    print(
        "redo_count:",
        undo_state.redo_count,
    )

    redo_trim = history.redo()

    clip_1_after_redo_trim = (
        history.timeline.get_clip(
            "clip_1"
        )
    )

    redo_trim_start_time = (
        clip_1_after_redo_trim.start_time
        if clip_1_after_redo_trim
        else None
    )

    print(
        "redo_trim:",
        redo_trim.success,
    )

    # Edit mới sau undo/redo phải xóa
    # toàn bộ redo branch còn lại.
    delete_result = history.delete_clip(
        "clip_1"
    )

    clip_1_after_delete = (
        history.timeline.get_clip(
            "clip_1"
        )
    )

    redo_cleared_after_new_edit = (
        history.can_redo is False
    )

    print(
        "new_edit:",
        delete_result.success,
    )
    print(
        "redo_cleared:",
        redo_cleared_after_new_edit,
    )

    state_before_reset = (
        history.state()
    )

    timeline_before_reset = (
        history.timeline.to_dict()
    )

    exposed_command = history.undo_commands[-1]
    exposed_before_clip = (
        exposed_command.before.get_clip(
            "clip_2"
        )
    )

    if exposed_before_clip is not None:
        exposed_before_clip.start_time = 999.0

    internal_before_clip = (
        history.undo_commands[-1]
        .before.get_clip("clip_2")
    )

    command_snapshot_isolated = (
        internal_before_clip is not None
        and internal_before_clip.start_time
        != 999.0
    )

    exposed_events = history.events
    exposed_events[-1].metadata[
        "tampered"
    ] = True

    event_snapshot_isolated = (
        "tampered"
        not in history.events[-1].metadata
    )

    reset_result = history.reset()

    reset_state = history.state()

    reset_clip_1 = (
        history.timeline.get_clip(
            "clip_1"
        )
    )

    reset_clip_2 = (
        history.timeline.get_clip(
            "clip_2"
        )
    )

    reset_clip_1_start_time = (
        reset_clip_1.start_time
        if reset_clip_1
        else None
    )

    reset_clip_2_track_id = (
        reset_clip_2.track_id
        if reset_clip_2
        else None
    )

    snapshot_clone = history.snapshot()
    snapshot_clone.mark_dirty()

    shared_store = (
        history.store is store
        and history.mutation_runtime.store
        is store
    )

    snapshot_isolated = (
        snapshot_clone.revision == 2
        and history.timeline.revision == 1
    )

    source_unchanged = (
        source_timeline.revision == 1
        and source_timeline.dirty is False
        and source_timeline
        .get_clip("clip_2")
        .track_id
        == "video_primary"
    )

    output_path = Path(
        "storage/demo_outputs/"
        "timeline_history_runtime.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_payload = {
        "initial_timeline": (
            initial_timeline
        ),
        "after_edits": after_edits,
        "state_before_reset": (
            state_before_reset.to_dict()
        ),
        "timeline_before_reset": (
            timeline_before_reset
        ),
        "runtime_after_reset": (
            history.to_dict()
        ),
        "reset_result": (
            reset_result.to_dict()
        ),
        "checks": {
            "clip_2_after_move_track_id": (
                clip_2_after_move.track_id
                if clip_2_after_move
                else None
            ),
            "clip_2_after_move_start_time": (
                clip_2_after_move.start_time
                if clip_2_after_move
                else None
            ),
            "clip_1_after_trim_start_time": (
                clip_1_after_trim.start_time
                if clip_1_after_trim
                else None
            ),
            "duplicate_created": (
                duplicate_after_create
                is not None
            ),
            "duplicate_removed_after_undo": (
                clip_2_copy_after_undo
                is None
            ),
            "clip_1_after_undo_trim": (
                clip_1_after_undo_trim
                .start_time
                if clip_1_after_undo_trim
                else None
            ),
            "clip_1_after_redo_trim": (
                redo_trim_start_time
            ),
            "clip_deleted_after_new_edit": (
                clip_1_after_delete
                is None
            ),
            "redo_cleared_after_new_edit": (
                redo_cleared_after_new_edit
            ),
            "reset_clip_1_start_time": (
                reset_clip_1_start_time
            ),
            "reset_clip_2_track_id": (
                reset_clip_2_track_id
            ),
        },
    }

    output_path.write_text(
        json.dumps(
            output_payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "reset_success:",
        reset_result.success,
    )
    print(
        "final_undo_count:",
        reset_state.undo_count,
    )
    print(
        "final_redo_count:",
        reset_state.redo_count,
    )
    print(
        "event_count:",
        len(history.events),
    )
    print(
        "shared_store:",
        shared_store,
    )
    print(
        "store_change_count:",
        len(store.changes),
    )
    print(
        "snapshot_isolated:",
        snapshot_isolated,
    )
    print(
        "source_unchanged:",
        source_unchanged,
    )
    print(
        "command_snapshot_isolated:",
        command_snapshot_isolated,
    )
    print(
        "event_snapshot_isolated:",
        event_snapshot_isolated,
    )
    print(
        "output:",
        output_path,
    )

    assert move_result.success is True
    assert trim_result.success is True
    assert duplicate_result.success is True

    assert (
        after_edits["revision"]
        == 4
    )

    assert clip_2_after_move is not None

    assert (
        clip_2_after_move.track_id
        == "video_overlay"
    )

    assert (
        clip_2_after_move.start_time
        == 5.0
    )

    assert clip_1_after_trim is not None

    assert (
        clip_1_after_trim.start_time
        == 1.0
    )

    assert duplicate_after_create is not None

    assert undo_duplicate.success is True

    assert (
        clip_2_copy_after_undo
        is None
    )

    assert undo_trim.success is True

    assert (
        clip_1_after_undo_trim
        is not None
    )

    assert (
        clip_1_after_undo_trim.start_time
        == 0.0
    )

    assert (
        undo_state.undo_count
        == 1
    )

    assert (
        undo_state.redo_count
        == 2
    )

    assert redo_trim.success is True

    assert (
        redo_trim_start_time
        == 1.0
    )

    assert delete_result.success is True

    assert (
        clip_1_after_delete
        is None
    )

    assert (
        redo_cleared_after_new_edit
        is True
    )

    assert (
        state_before_reset.undo_count
        > 0
    )

    assert (
        state_before_reset.redo_count
        == 0
    )

    assert reset_result.success is True

    assert (
        reset_state.undo_count
        == 0
    )

    assert (
        reset_state.redo_count
        == 0
    )

    assert reset_clip_1 is not None
    assert reset_clip_2 is not None

    assert (
        reset_clip_1_start_time
        == 0.0
    )

    assert (
        reset_clip_2_track_id
        == "video_primary"
    )

    assert (
        history.timeline.revision
        == 1
    )

    assert shared_store is True
    assert len(store.changes) == 8
    assert snapshot_isolated is True
    assert source_unchanged is True
    assert command_snapshot_isolated is True
    assert event_snapshot_isolated is True

    assert not hasattr(
        history,
        "_initial_timeline",
    )

    print(
        "\nDONE: Timeline history "
        "runtime test completed."
    )


if __name__ == "__main__":
    main()