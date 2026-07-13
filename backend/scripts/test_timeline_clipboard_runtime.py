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
    build_clipboard_from_history_runtime,
    build_timeline_history_runtime,
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
                        end_time=3.0,
                        source_start=0.0,
                        source_end=3.0,
                        source_duration=30.0,
                    ),
                    EditableTimelineClip(
                        clip_id="clip_2",
                        track_id="video_primary",
                        clip_type=(
                            EditableClipType.VIDEO
                        ),
                        start_time=4.0,
                        end_time=7.0,
                        source_start=4.0,
                        source_end=7.0,
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
                position=1,
                overlap_policy=(
                    TimelineOverlapPolicy.ALLOW
                ),
            ),
        ],
    )


def main() -> None:
    history = (
        build_timeline_history_runtime(
            build_timeline()
        )
    )

    clipboard = (
        build_clipboard_from_history_runtime(
            history,
            maximum_history_size=3,
        )
    )

    print(
        "=== Timeline Clipboard Runtime ==="
    )

    copy_result = clipboard.copy_clips(
        ["clip_1", "clip_2"]
    )

    print(
        "copy:",
        copy_result.success,
    )

    paste_result = clipboard.paste(
        at_time=10.0,
        target_track_id="video_overlay",
        track_mapping={
            "video_primary": (
                "video_overlay"
            )
        },
    )

    print(
        "paste:",
        paste_result.success,
    )
    print(
    "paste_error:",
    paste_result.error,
)

    print(
    "timeline_history_result:",
    (
        paste_result
        .timeline_history_result
        .to_dict()
        if paste_result.timeline_history_result
        else None
    ),
)

    pasted_ids = []

    if (
    paste_result.success
    and paste_result.timeline_history_result
    and paste_result
    .timeline_history_result
    .mutation_result
    ):
        pasted_ids = (
        paste_result
        .timeline_history_result
        .mutation_result
        .metadata
        .get(
            "inserted_clip_ids",
            [],
        )
    )
    print(
        "pasted_count:",
        len(pasted_ids),
    )

    undo_paste = history.undo()

    print(
        "undo_paste:",
        undo_paste.success,
    )

    redo_paste = history.redo()

    print(
        "redo_paste:",
        redo_paste.success,
    )

    cut_result = clipboard.cut_clip(
        "clip_1"
    )

    print(
        "cut:",
        cut_result.success,
    )

    clip_removed = (
        history.timeline.get_clip(
            "clip_1"
        )
        is None
    )

    print(
        "clip_removed:",
        clip_removed,
    )

    undo_cut = history.undo()

    print(
        "undo_cut:",
        undo_cut.success,
    )

    copy_again = clipboard.copy_clip(
        "clip_2"
    )

    history_state = (
        clipboard.history_state()
    )

    print(
        "clipboard_history_count:",
        history_state.entry_count,
    )

    oldest_entry = (
        clipboard.history_entries[0]
    )

    restore_result = (
        clipboard.restore_history_entry(
            oldest_entry.entry_id
        )
    )

    print(
        "restore_history:",
        restore_result.success,
    )

    output_path = Path(
        "storage/demo_outputs/"
        "timeline_clipboard_runtime.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            clipboard.to_dict(),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "output:",
        output_path,
    )

    assert copy_result.success is True
    assert paste_result.success is True
    assert len(pasted_ids) == 2

    assert undo_paste.success is True

    for clip_id in pasted_ids:
        assert (
            history.timeline.get_clip(
                clip_id
            )
            is None
        )

    assert redo_paste.success is True

    for clip_id in pasted_ids:
        assert (
            history.timeline.get_clip(
                clip_id
            )
            is not None
        )

    assert cut_result.success is True
    assert clip_removed is True

    assert undo_cut.success is True

    assert (
        history.timeline.get_clip(
            "clip_1"
        )
        is not None
    )

    assert copy_again.success is True

    assert (
        history_state.entry_count
        == 3
    )

    assert restore_result.success is True

    assert (
        restore_result.content.item_count
        >= 1
    )

    print(
        "\nDONE: Timeline clipboard "
        "runtime test completed."
    )


if __name__ == "__main__":
    main()