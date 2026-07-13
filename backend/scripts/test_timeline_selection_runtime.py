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

from app.review.selection import (
    TimelineSelectionFocus,
    TimelineSelectionMode,
    build_timeline_selection_runtime,
)


PRODUCTION_ID = (
    "221e4b01-5fb9-4b4a-a549-4fb32c455059"
)


def main() -> None:
    events = []

    tracks = [
        {
            "track_id": "video_primary",
            "track_type": "video_primary",
            "position": 0,
            "clips": [
                {
                    "clip_id": "clip_1",
                    "start_time": 0.0,
                    "end_time": 4.0,
                },
                {
                    "clip_id": "clip_2",
                    "start_time": 4.0,
                    "end_time": 10.0,
                },
                {
                    "clip_id": "clip_3",
                    "start_time": 10.0,
                    "end_time": 18.0,
                },
            ],
        },
        {
            "track_id": "subtitle",
            "track_type": "subtitle",
            "position": 1,
            "clips": [
                {
                    "clip_id": "subtitle_1",
                    "start_time": 0.0,
                    "end_time": 5.0,
                },
                {
                    "clip_id": "subtitle_2",
                    "start_time": 5.0,
                    "end_time": 12.0,
                },
            ],
        },
    ]

    runtime = (
        build_timeline_selection_runtime(
            production_id=PRODUCTION_ID,
            duration=18.0,
            tracks=tracks,
            fps=30.0,
            event_callback=events.append,
        )
    )

    print(
        "=== Timeline Selection Runtime ==="
    )

    track_result = runtime.select_track(
        "video_primary"
    )

    print(
        "select_track:",
        track_result.success,
    )

    clip_result = runtime.select_clip(
        "clip_1",
        move_cursor=True,
    )

    print(
        "select_clip:",
        clip_result.success,
    )

    multi_result = runtime.select_multiple(
        clip_ids=[
            "clip_1",
            "clip_2",
            "subtitle_1",
        ],
    )

    print(
        "multi_select:",
        multi_result.success,
    )

    runtime.hover_clip(
        "clip_2"
    )

    print(
        "hover_clip:",
        runtime.state.hovered_clip_id,
    )

    runtime.set_cursor(6.5)

    print(
        "cursor_time:",
        runtime.state.cursor_time,
    )

    print(
        "cursor_frame:",
        runtime.state.cursor_frame,
    )

    runtime.step_cursor_frames(15)

    print(
        "cursor_after_frames:",
        runtime.state.cursor_time,
    )

    range_result = runtime.set_range(
        4.0,
        9.5,
    )

    print(
        "range_select:",
        range_result.success,
    )

    runtime.set_focus(
        TimelineSelectionFocus.CLIP
    )

    invalid_result = runtime.select_clip(
        "missing_clip"
    )

    print(
        "invalid_selection_blocked:",
        invalid_result.success is False,
    )

    snapshot_before_clear = (
        runtime.to_dict()
    )

    clear_result = runtime.clear_selection(
        preserve_cursor=True,
        preserve_hover=False,
    )

    print(
        "clear_selection:",
        clear_result.success,
    )

    reset_result = runtime.reset()

    output = {
        "snapshot_before_clear": (
            snapshot_before_clear
        ),
        "clear_result": (
            clear_result.to_dict()
        ),
        "reset_result": (
            reset_result.to_dict()
        ),
        "captured_event_count": len(
            events
        ),
    }

    output_path = Path(
        "storage/demo_outputs/"
        "timeline_selection_runtime.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    assert track_result.success is True
    assert clip_result.success is True
    assert multi_result.success is True

    assert (
        snapshot_before_clear[
            "state"
        ]["mode"]
        == TimelineSelectionMode.RANGE.value
    )

    assert (
        snapshot_before_clear[
            "state"
        ]["selected_count"]
        >= 3
    )

    assert (
        snapshot_before_clear[
            "state"
        ]["cursor_frame"]
        > 0
    )

    assert (
        snapshot_before_clear[
            "state"
        ]["selected_range"][
            "duration"
        ]
        == 5.5
    )

    assert invalid_result.success is False
    assert clear_result.state.has_selection is False

    assert (
        reset_result.state.mode
        == TimelineSelectionMode.NONE
    )

    assert (
        reset_result.state.cursor_time
        == 0.0
    )

    print(
        "event_count:",
        len(runtime.events),
    )
    print(
        "captured_event_count:",
        len(events),
    )
    print(
        "output:",
        output_path,
    )

    print(
        "\nDONE: Timeline selection "
        "runtime test completed."
    )


if __name__ == "__main__":
    main()