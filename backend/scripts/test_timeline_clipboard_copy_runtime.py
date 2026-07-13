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
    build_clipboard_from_store,
    build_timeline_clipboard_runtime,
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
                position=0,
                overlap_policy=(
                    TimelineOverlapPolicy
                    .FORBID
                ),
                clips=[
                    EditableTimelineClip(
                        clip_id="clip_1",
                        track_id="video_primary",
                        clip_type=(
                            EditableClipType.VIDEO
                        ),
                        start_time=0.0,
                        end_time=4.0,
                        source_start=0.0,
                        source_end=4.0,
                        source_duration=30.0,
                    ),
                    EditableTimelineClip(
                        clip_id="clip_2",
                        track_id="video_primary",
                        clip_type=(
                            EditableClipType.VIDEO
                        ),
                        start_time=6.0,
                        end_time=10.0,
                        source_start=6.0,
                        source_end=10.0,
                        source_duration=30.0,
                    ),
                ],
            ),
            EditableTimelineTrack(
                track_id="subtitle",
                track_type=(
                    EditableTrackType.SUBTITLE
                ),
                position=1,
                overlap_policy=(
                    TimelineOverlapPolicy.ALLOW
                ),
                clips=[
                    EditableTimelineClip(
                        clip_id="subtitle_1",
                        track_id="subtitle",
                        clip_type=(
                            EditableClipType
                            .SUBTITLE
                        ),
                        start_time=2.0,
                        end_time=5.0,
                        text=(
                            "AI tự động chỉnh sửa "
                            "video cho bạn."
                        ),
                    ),
                ],
            ),
        ],
    )


def main() -> None:
    timeline = build_timeline()
    store = build_timeline_runtime_store(
        timeline
    )
    clipboard = build_clipboard_from_store(
        store
    )

    legacy_clipboard = (
        build_timeline_clipboard_runtime(
            timeline
        )
    )

    print(
        "=== Timeline Clipboard Copy Runtime ==="
    )

    initial_state = clipboard.state()

    single_result = clipboard.copy_clip(
        "clip_1"
    )

    single_item = (
        single_result.content.items[0]
    )

    print(
        "initial_empty:",
        initial_state.available is False,
    )
    print(
        "copy_single:",
        single_result.success,
    )
    print(
        "single_item_count:",
        single_result.content.item_count,
    )

    multiple_result = (
        clipboard.copy_clips(
            [
                "clip_2",
                "subtitle_1",
                "clip_1",
                "clip_2",
            ]
        )
    )

    relative_positions = {
        item.source_clip_id: (
            item.relative_start
        )
        for item
        in multiple_result.content.items
    }

    print(
        "copy_multiple:",
        multiple_result.success,
    )
    print(
        "multiple_item_count:",
        multiple_result.content.item_count,
    )
    print(
        "track_count:",
        len(
            multiple_result.content
            .source_track_ids
        ),
    )
    print(
        "anchor_time:",
        multiple_result.content
        .anchor_time,
    )
    print(
        "total_duration:",
        multiple_result.content
        .total_duration,
    )

    missing_result = (
        clipboard.copy_clip(
            "missing_clip"
        )
    )

    print(
        "missing_clip_blocked:",
        missing_result.success is False,
    )

    # Copy không được sửa timeline gốc.
    original_unchanged = (
        timeline.revision == 1
        and timeline.dirty is False
        and timeline.clip_count == 3
    )

    print(
        "timeline_unchanged:",
        original_unchanged,
    )

    shared_store = clipboard.store is store

    snapshot_clone = clipboard.snapshot()
    snapshot_clone.mark_dirty()
    snapshot_isolated = (
        snapshot_clone.revision == 2
        and store.revision == 1
    )

    exposed_content = clipboard.content
    exposed_content.items[0].clip.start_time = (
        999.0
    )
    content_isolated = (
        clipboard.content.items[0]
        .clip.start_time
        != 999.0
    )

    exposed_entries = (
        clipboard.history_entries
    )
    exposed_entries[-1].content.items[
        0
    ].clip.start_time = 999.0
    history_isolated = (
        clipboard.history_entries[-1]
        .content.items[0].clip.start_time
        != 999.0
    )

    exposed_events = clipboard.events
    exposed_events[-1].metadata[
        "tampered"
    ] = True
    events_isolated = (
        "tampered"
        not in clipboard.events[-1].metadata
    )

    legacy_factory_works = (
        legacy_clipboard.store.production_id
        == timeline.production_id
        and not hasattr(
            legacy_clipboard,
            "_timeline",
        )
    )

    print("shared_store:", shared_store)
    print(
        "store_change_count:",
        len(store.changes),
    )
    print(
        "snapshot_isolated:",
        snapshot_isolated,
    )
    print(
        "content_isolated:",
        content_isolated,
    )
    print(
        "history_isolated:",
        history_isolated,
    )
    print(
        "events_isolated:",
        events_isolated,
    )
    print(
        "legacy_factory_works:",
        legacy_factory_works,
    )

    clipboard_before_clear = (
        clipboard.to_dict()
    )

    clear_result = clipboard.clear()

    print(
        "clear:",
        clear_result.success,
    )
    print(
        "empty_after_clear:",
        clipboard.has_content is False,
    )

    output_path = Path(
        "storage/demo_outputs/"
        "timeline_clipboard_copy_runtime.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            {
                "before_clear": (
                    clipboard_before_clear
                ),
                "after_clear": (
                    clipboard.to_dict()
                ),
                "missing_result": (
                    missing_result.to_dict()
                ),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "event_count:",
        len(clipboard.events),
    )
    print(
        "output:",
        output_path,
    )

    assert initial_state.available is False

    assert single_result.success is True
    assert single_result.content.item_count == 1

    assert (
        single_item.source_clip_id
        == "clip_1"
    )

    assert (
        single_item.relative_start
        == 0.0
    )

    assert multiple_result.success is True

    # clip_2 bị truyền hai lần nhưng chỉ
    # được copy một lần.
    assert (
        multiple_result.content.item_count
        == 3
    )

    assert (
        multiple_result.content.clip_count
        == 3
    )

    assert (
        multiple_result.content
        .anchor_time
        == 0.0
    )

    assert relative_positions == {
        "clip_1": 0.0,
        "subtitle_1": 2.0,
        "clip_2": 6.0,
    }

    assert (
        multiple_result.content
        .total_duration
        == 10.0
    )

    assert len(
        multiple_result.content
        .source_track_ids
    ) == 2

    assert missing_result.success is False

    # Copy lỗi không được xóa clipboard
    # đang tồn tại.
    assert (
        missing_result.content.item_count
        == 3
    )

    assert original_unchanged is True
    assert shared_store is True
    assert len(store.changes) == 0
    assert snapshot_isolated is True
    assert content_isolated is True
    assert history_isolated is True
    assert events_isolated is True
    assert legacy_factory_works is True

    assert not hasattr(
        clipboard,
        "_timeline",
    )

    assert clear_result.success is True
    assert clipboard.has_content is False
    assert clipboard.state().item_count == 0

    print(
        "\nDONE: Timeline clipboard "
        "copy runtime test completed."
    )


if __name__ == "__main__":
    main()