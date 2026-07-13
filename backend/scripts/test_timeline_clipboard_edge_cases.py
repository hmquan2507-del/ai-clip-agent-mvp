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
    TimelineClipboardAction,
    TimelineClipboardEventType,
    TimelineOverlapPolicy,
    build_clipboard_from_history_runtime,
    build_history_from_store,
    build_timeline_runtime_store,
)


PRODUCTION_ID = "221e4b01-5fb9-4b4a-a549-4fb32c455059"


def build_timeline() -> EditableTimeline:
    return EditableTimeline(
        production_id=PRODUCTION_ID,
        duration=7.0,
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
                        source_duration=20.0,
                    ),
                    EditableTimelineClip(
                        clip_id="clip_2",
                        track_id="video_primary",
                        clip_type=EditableClipType.VIDEO,
                        start_time=4.0,
                        end_time=7.0,
                        source_start=4.0,
                        source_end=7.0,
                        source_duration=20.0,
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
                track_id="subtitle",
                track_type=EditableTrackType.SUBTITLE,
                position=2,
                overlap_policy=TimelineOverlapPolicy.ALLOW,
                clips=[
                    EditableTimelineClip(
                        clip_id="subtitle_1",
                        track_id="subtitle",
                        clip_type=EditableClipType.SUBTITLE,
                        start_time=1.0,
                        end_time=2.0,
                        text="Nội dung kiểm thử clipboard.",
                    )
                ],
            ),
            EditableTimelineTrack(
                track_id="locked_video",
                track_type=EditableTrackType.VIDEO_PRIMARY,
                position=3,
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
    history = build_history_from_store(store)
    clipboard = build_clipboard_from_history_runtime(
        history,
        maximum_history_size=3,
    )

    print("=== Timeline Clipboard Edge Cases ===")

    first_copy = clipboard.copy_clip("clip_1")
    first_entry_id = clipboard.history_entries[0].entry_id
    content_before_failed_cut = (
        clipboard.content.clipboard_id
    )
    events_before_failed_cut = len(
        clipboard.events
    )

    locked_cut = clipboard.cut_clip(
        "locked_clip"
    )
    locked_cut_rollback = (
        not locked_cut.success
        and clipboard.content.clipboard_id
        == content_before_failed_cut
        and store.snapshot().get_clip(
            "locked_clip"
        )
        is not None
        and len(store.changes) == 0
        and history.state().undo_count == 0
        and len(clipboard.events)
        == events_before_failed_cut + 1
        and clipboard.events[-1].event_type
        == TimelineClipboardEventType.CUT_FAILED
    )

    multi_copy = clipboard.copy_clips(
        ["clip_1", "subtitle_1"]
    )
    events_before_missing_mapping = len(
        clipboard.events
    )
    missing_mapping_paste = clipboard.paste(
        at_time=10.0,
        target_track_id="video_overlay",
    )
    missing_mapping_blocked = (
        not missing_mapping_paste.success
        and len(store.changes) == 0
        and history.state().undo_count == 0
        and len(clipboard.events)
        == events_before_missing_mapping + 1
    )

    events_before_invalid_mapping = len(
        clipboard.events
    )
    invalid_mapping_paste = clipboard.paste(
        at_time=10.0,
        track_mapping={
            "video_primary": "missing_track",
            "subtitle": "subtitle",
        },
    )
    invalid_mapping_atomic = (
        not invalid_mapping_paste.success
        and len(store.changes) == 0
        and history.state().undo_count == 0
        and len(clipboard.events)
        == events_before_invalid_mapping + 1
        and store.snapshot().clip_count == 4
    )

    events_before_valid_paste = len(
        clipboard.events
    )
    valid_paste = clipboard.paste(
        at_time=10.0,
        track_mapping={
            "video_primary": "video_overlay",
            "subtitle": "subtitle",
        },
    )
    pasted_ids = (
        valid_paste
        .timeline_history_result
        .mutation_result
        .metadata.get("inserted_clip_ids", [])
        if (
            valid_paste.success
            and valid_paste.timeline_history_result
            and valid_paste
            .timeline_history_result
            .mutation_result
        )
        else []
    )
    paste_single_event = (
        valid_paste.success
        and len(pasted_ids) == 2
        and len(store.changes) == 1
        and len(clipboard.events)
        == events_before_valid_paste + 1
        and clipboard.events[-1].event_type
        == TimelineClipboardEventType.CLIPS_PASTED
    )

    events_before_cut = len(clipboard.events)
    successful_cut = clipboard.cut_clip(
        "clip_2"
    )
    cut_single_event = (
        successful_cut.success
        and store.snapshot().get_clip("clip_2")
        is None
        and len(store.changes) == 2
        and len(clipboard.events)
        == events_before_cut + 1
        and clipboard.events[-1].event_type
        == TimelineClipboardEventType.CLIP_CUT
    )

    undo_cut = history.undo()
    cut_undo_works = (
        undo_cut.success
        and store.snapshot().get_clip("clip_2")
        is not None
        and len(store.changes) == 3
    )

    clipboard.copy_clip("clip_2")
    clipboard.copy_clip("clip_1")

    history_limit_enforced = (
        len(clipboard.history_entries) == 3
        and all(
            entry.entry_id != first_entry_id
            for entry in clipboard.history_entries
        )
    )

    oldest_current_entry = (
        clipboard.history_entries[0]
    )
    restore_result = (
        clipboard.restore_history_entry(
            oldest_current_entry.entry_id
        )
    )
    restore_works = (
        restore_result.success
        and clipboard.content.clipboard_id
        == oldest_current_entry
        .content.clipboard_id
        and clipboard.content.action
        == TimelineClipboardAction.CUT
    )

    content_id_before_clear_history = (
        clipboard.content.clipboard_id
    )
    clear_history_result = (
        clipboard.clear_history()
    )
    clear_history_preserves_content = (
        clear_history_result.success
        and len(clipboard.history_entries) == 0
        and clipboard.content.clipboard_id
        == content_id_before_clear_history
        and clipboard.has_content
    )

    clear_result = clipboard.clear()
    clear_content_works = (
        clear_result.success
        and not clipboard.has_content
        and clipboard.state().item_count == 0
        and len(clipboard.history_entries) == 0
    )

    source_unchanged = (
        source_timeline.revision == 1
        and source_timeline.dirty is False
        and source_timeline.clip_count == 4
    )

    checks = {
        "first_copy": first_copy.success,
        "locked_cut_rollback": locked_cut_rollback,
        "multi_copy": multi_copy.success,
        "missing_mapping_blocked": missing_mapping_blocked,
        "invalid_mapping_atomic": invalid_mapping_atomic,
        "paste_single_event": paste_single_event,
        "cut_single_event": cut_single_event,
        "cut_undo_works": cut_undo_works,
        "history_limit_enforced": history_limit_enforced,
        "restore_works": restore_works,
        "clear_history_preserves_content": (
            clear_history_preserves_content
        ),
        "clear_content_works": clear_content_works,
        "source_unchanged": source_unchanged,
    }

    for name, success in checks.items():
        print(f"{name}:", success)

    output_path = Path(
        "storage/demo_outputs/"
        "timeline_clipboard_edge_cases.json"
    )
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output_path.write_text(
        json.dumps(
            {
                "checks": checks,
                "store_change_count": len(
                    store.changes
                ),
                "history_state": (
                    history.state().to_dict()
                ),
                "clipboard_state": (
                    clipboard.state().to_dict()
                ),
                "clipboard_event_count": len(
                    clipboard.events
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
        "\nDONE: Timeline clipboard edge "
        "case test completed."
    )


if __name__ == "__main__":
    main()