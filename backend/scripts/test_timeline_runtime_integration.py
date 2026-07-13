from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.review.editing import (
    EditableClipType,
    EditableTimeline,
    EditableTimelineClip,
    EditableTimelineTrack,
    EditableTrackType,
    TimelineOverlapPolicy,
    build_clipboard_from_history_runtime,
    build_clipboard_from_mutation_runtime,
    build_history_from_mutation_runtime,
    build_mutation_runtime_from_store,
    build_timeline_runtime_store,
)


PRODUCTION_ID = "221e4b01-5fb9-4b4a-a549-4fb32c455059"


def build_timeline() -> EditableTimeline:
    return EditableTimeline(
        production_id=PRODUCTION_ID,
        duration=11.0,
        fps=30.0,
        tracks=[
            EditableTimelineTrack(
                track_id="video_primary",
                track_type=EditableTrackType.VIDEO_PRIMARY,
                position=0,
                overlap_policy=TimelineOverlapPolicy.FORBID,
                clips=[
                    EditableTimelineClip(
                        clip_id="clip_1",
                        track_id="video_primary",
                        clip_type=EditableClipType.VIDEO,
                        start_time=0.0,
                        end_time=3.0,
                        source_start=0.0,
                        source_end=3.0,
                        source_duration=30.0,
                    ),
                    EditableTimelineClip(
                        clip_id="clip_2",
                        track_id="video_primary",
                        clip_type=EditableClipType.VIDEO,
                        start_time=4.0,
                        end_time=7.0,
                        source_start=4.0,
                        source_end=7.0,
                        source_duration=30.0,
                    ),
                    EditableTimelineClip(
                        clip_id="clip_3",
                        track_id="video_primary",
                        clip_type=EditableClipType.VIDEO,
                        start_time=8.0,
                        end_time=11.0,
                        source_start=8.0,
                        source_end=11.0,
                        source_duration=30.0,
                    ),
                ],
            ),
            EditableTimelineTrack(
                track_id="video_overlay",
                track_type=EditableTrackType.VIDEO_OVERLAY,
                position=1,
                overlap_policy=TimelineOverlapPolicy.ALLOW,
            ),
            EditableTimelineTrack(
                track_id="locked_video",
                track_type=EditableTrackType.VIDEO_PRIMARY,
                position=2,
                locked=True,
                overlap_policy=TimelineOverlapPolicy.FORBID,
                clips=[
                    EditableTimelineClip(
                        clip_id="locked_clip",
                        track_id="locked_video",
                        clip_type=EditableClipType.VIDEO,
                        start_time=0.0,
                        end_time=2.0,
                        source_start=0.0,
                        source_end=2.0,
                        source_duration=10.0,
                    )
                ],
            ),
        ],
    )


def main() -> None:
    source_timeline = build_timeline()
    store = build_timeline_runtime_store(source_timeline)
    mutation = build_mutation_runtime_from_store(store)
    history = build_history_from_mutation_runtime(
        mutation,
        maximum_history_size=20,
    )
    clipboard = build_clipboard_from_history_runtime(
        history,
        maximum_history_size=10,
    )
    copy_only_clipboard = (
        build_clipboard_from_mutation_runtime(
            mutation
        )
    )

    print("=== Timeline Runtime Integration ===")

    shared_store = (
        mutation.store is store
        and history.store is store
        and clipboard.store is store
        and copy_only_clipboard.store is store
    )

    initial_revision = store.revision
    initial_change_count = len(store.changes)

    overlap_failure = mutation.move_clip(
        "clip_2",
        2.0,
        target_track_id="video_primary",
    )
    locked_failure = mutation.move_clip(
        "clip_1",
        0.0,
        target_track_id="locked_video",
    )

    atomic_candidate = EditableTimelineClip(
        clip_id="atomic_candidate",
        track_id="video_overlay",
        clip_type=EditableClipType.VIDEO,
        start_time=12.0,
        end_time=14.0,
    )
    invalid_candidate = EditableTimelineClip(
        clip_id="invalid_candidate",
        track_id="missing_track",
        clip_type=EditableClipType.VIDEO,
        start_time=14.0,
        end_time=16.0,
    )
    atomic_failure = mutation.insert_clips(
        [atomic_candidate, invalid_candidate]
    )

    failures_no_commit = (
        not overlap_failure.success
        and not locked_failure.success
        and not atomic_failure.success
        and store.revision == initial_revision
        and len(store.changes) == initial_change_count
        and len(mutation.events) == 0
        and store.snapshot().get_clip(
            "atomic_candidate"
        )
        is None
    )

    move_result = mutation.move_clip(
        "clip_3",
        8.0,
        target_track_id="video_overlay",
    )
    move_single_commit = (
        move_result.success
        and store.revision == 2
        and len(store.changes) == 1
        and len(mutation.events) == 1
    )

    trim_result = history.trim_clip_start(
        "clip_1",
        1.0,
    )
    duplicate_result = history.duplicate_clip(
        "clip_1",
        new_clip_id="clip_1_copy",
        new_start_time=12.0,
        target_track_id="video_overlay",
    )
    undo_duplicate = history.undo()
    redo_duplicate = history.redo()
    undo_duplicate_again = history.undo()
    delete_result = history.delete_clip("clip_2")

    redo_branch_cleared = (
        trim_result.success
        and duplicate_result.success
        and undo_duplicate.success
        and redo_duplicate.success
        and undo_duplicate_again.success
        and delete_result.success
        and history.can_redo is False
        and history.timeline.get_clip(
            "clip_1_copy"
        )
        is None
        and history.timeline.get_clip(
            "clip_2"
        )
        is None
    )

    change_count_before_copy = len(store.changes)
    copy_result = clipboard.copy_clips(
        ["clip_1", "clip_3"]
    )
    copy_no_timeline_change = (
        copy_result.success
        and len(store.changes)
        == change_count_before_copy
    )

    paste_result = clipboard.paste(
        at_time=12.0,
        track_mapping={
            "video_primary": "video_overlay",
            "video_overlay": "video_overlay",
        },
    )
    pasted_ids = (
        paste_result
        .timeline_history_result
        .mutation_result
        .metadata.get("inserted_clip_ids", [])
        if (
            paste_result.success
            and paste_result.timeline_history_result
            and paste_result
            .timeline_history_result
            .mutation_result
        )
        else []
    )
    paste_atomic = (
        paste_result.success
        and len(pasted_ids) == 2
        and all(
            store.snapshot().get_clip(clip_id)
            is not None
            for clip_id in pasted_ids
        )
        and store.revision == 5
        and len(store.changes) == 8
    )

    undo_paste = history.undo()
    pasted_absent_after_undo = all(
        store.snapshot().get_clip(clip_id) is None
        for clip_id in pasted_ids
    )
    redo_paste = history.redo()
    pasted_present_after_redo = all(
        store.snapshot().get_clip(clip_id)
        is not None
        for clip_id in pasted_ids
    )

    cut_result = clipboard.cut_clip("clip_1")
    clip_removed_after_cut = (
        store.snapshot().get_clip("clip_1")
        is None
    )
    undo_cut = history.undo()
    clip_restored_after_undo = (
        store.snapshot().get_clip("clip_1")
        is not None
    )

    changes_before_failed_clipboard = len(
        store.changes
    )
    undo_count_before_failed_clipboard = (
        history.state().undo_count
    )
    failed_paste = clipboard.paste(
        at_time=0.0,
        target_track_id="locked_video",
    )
    missing_copy = clipboard.copy_clip(
        "missing_clip"
    )
    copy_only_cut = copy_only_clipboard.cut_clip(
        "clip_1"
    )

    clipboard_failures_no_commit = (
        not failed_paste.success
        and not missing_copy.success
        and not copy_only_cut.success
        and len(store.changes)
        == changes_before_failed_clipboard
        and history.state().undo_count
        == undo_count_before_failed_clipboard
    )

    timeline_snapshot = clipboard.snapshot()
    timeline_snapshot.mark_dirty()
    timeline_snapshot_isolated = (
        timeline_snapshot.revision
        == store.revision + 1
        and clipboard.timeline.revision
        == store.revision
    )

    exposed_content = clipboard.content
    exposed_content.items[0].clip.start_time = 999.0
    clipboard_content_isolated = (
        clipboard.content.items[0]
        .clip.start_time
        != 999.0
    )

    exposed_command = history.undo_commands[-1]
    command_clip = exposed_command.before.get_clip(
        "clip_1"
    )
    if command_clip is not None:
        command_clip.start_time = 999.0
    history_command_isolated = (
        history.undo_commands[-1]
        .before.get_clip("clip_1")
        .start_time
        != 999.0
    )

    exposed_changes = store.changes
    exposed_changes[0].metadata["tampered"] = True
    store_change_log_isolated = (
        "tampered"
        not in store.changes[0].metadata
    )

    expected_reasons = [
        "mutation.move_clip",
        "mutation.trim_clip_start",
        "mutation.duplicate_clip",
        "history.undo",
        "history.redo",
        "history.undo",
        "mutation.delete_clip",
        "mutation.paste_clips",
        "history.undo",
        "history.redo",
        "mutation.cut_clips",
        "history.undo",
    ]
    reasons_before_reset = [
        change.reason for change in store.changes
    ]
    change_reasons_valid = (
        reasons_before_reset == expected_reasons
    )

    reset_result = history.reset()
    reset_to_initial = (
        reset_result.success
        and store.revision == 1
        and history.state().undo_count == 0
        and history.state().redo_count == 0
        and len(mutation.events) == 0
        and store.snapshot().get_clip("clip_1")
        is not None
        and store.snapshot().get_clip("clip_2")
        is not None
        and store.snapshot().get_clip("clip_3")
        .track_id
        == "video_primary"
    )

    source_unchanged = (
        source_timeline.revision == 1
        and source_timeline.dirty is False
        and source_timeline.clip_count == 4
        and source_timeline.get_clip("clip_3")
        .track_id
        == "video_primary"
    )

    final_change_count = len(store.changes)
    final_history_event_count = len(
        history.events
    )

    checks = {
        "shared_store": shared_store,
        "failures_no_commit": failures_no_commit,
        "move_single_commit": move_single_commit,
        "redo_branch_cleared": redo_branch_cleared,
        "copy_no_timeline_change": copy_no_timeline_change,
        "paste_atomic": paste_atomic,
        "undo_paste": (
            undo_paste.success
            and pasted_absent_after_undo
        ),
        "redo_paste": (
            redo_paste.success
            and pasted_present_after_redo
        ),
        "cut_and_undo": (
            cut_result.success
            and clip_removed_after_cut
            and undo_cut.success
            and clip_restored_after_undo
        ),
        "clipboard_failures_no_commit": (
            clipboard_failures_no_commit
        ),
        "timeline_snapshot_isolated": (
            timeline_snapshot_isolated
        ),
        "clipboard_content_isolated": (
            clipboard_content_isolated
        ),
        "history_command_isolated": (
            history_command_isolated
        ),
        "store_change_log_isolated": (
            store_change_log_isolated
        ),
        "change_reasons_valid": (
            change_reasons_valid
        ),
        "reset_to_initial": reset_to_initial,
        "source_unchanged": source_unchanged,
        "final_change_count": (
            final_change_count == 13
        ),
        "final_history_event_count": (
            final_history_event_count == 12
        ),
    }

    for name, success in checks.items():
        print(f"{name}:", success)

    output_path = Path(
        "storage/demo_outputs/"
        "timeline_runtime_integration.json"
    )
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output_path.write_text(
        json.dumps(
            {
                "checks": checks,
                "store_changes": [
                    change.to_dict()
                    for change in store.changes
                ],
                "history_state": (
                    history.state().to_dict()
                ),
                "clipboard_state": (
                    clipboard.state().to_dict()
                ),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("output:", output_path)

    assert all(checks.values())

    print(
        "\nDONE: Timeline runtime integration "
        "test completed."
    )


if __name__ == "__main__":
    main()