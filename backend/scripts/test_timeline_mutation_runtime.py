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
    build_timeline_mutation_runtime,
)


PRODUCTION_ID = (
    "221e4b01-5fb9-4b4a-a549-4fb32c455059"
)


def build_timeline() -> EditableTimeline:
    return EditableTimeline(
        production_id=PRODUCTION_ID,
        duration=18.0,
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
                        start_time=4.0,
                        end_time=10.0,
                        source_start=4.0,
                        source_end=10.0,
                        source_duration=30.0,
                    ),
                    EditableTimelineClip(
                        clip_id="clip_3",
                        track_id="video_primary",
                        clip_type=(
                            EditableClipType.VIDEO
                        ),
                        start_time=12.0,
                        end_time=18.0,
                        source_start=12.0,
                        source_end=18.0,
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
            EditableTimelineTrack(
                track_id="locked_video",
                track_type=(
                    EditableTrackType
                    .VIDEO_PRIMARY
                ),
                locked=True,
                overlap_policy=(
                    TimelineOverlapPolicy
                    .FORBID
                ),
            ),
        ],
    )


def main() -> None:
    source_timeline = build_timeline()

    runtime = (
        build_timeline_mutation_runtime(
            source_timeline
        )
    )

    print(
        "=== Timeline Mutation Runtime ==="
    )

    move_result = runtime.move_clip(
        "clip_2",
        5.0,
        target_track_id=(
            "video_overlay"
        ),
    )

    trim_start = runtime.trim_clip_start(
        "clip_1",
        1.0,
    )

    trim_end = runtime.trim_clip_end(
        "clip_1",
        3.5,
    )

    inserted = EditableTimelineClip(
        clip_id="inserted_clip",
        track_id="video_overlay",
        clip_type=(
            EditableClipType.VIDEO
        ),
        start_time=0.0,
        end_time=2.0,
        source_start=0.0,
        source_end=2.0,
        source_duration=10.0,
    )

    insert_result = runtime.insert_clip(
        "video_overlay",
        inserted,
    )

    split_result = runtime.split_clip(
        "clip_3",
        15.0,
        right_clip_id="clip_3_right",
    )

    duplicate_result = (
        runtime.duplicate_clip(
            "inserted_clip",
            new_clip_id=(
                "inserted_clip_copy"
            ),
            new_start_time=2.0,
        )
    )

    overlap_result = runtime.move_clip(
        "clip_3_right",
        2.0,
        target_track_id=(
            "video_primary"
        ),
    )

    locked_result = runtime.move_clip(
        "clip_1",
        0.0,
        target_track_id=(
            "locked_video"
        ),
    )

    delete_result = runtime.delete_clip(
        "clip_2",
        close_gap=False,
    )

    close_gap_result = runtime.close_gap(
        "video_primary",
        3.5,
        12.0,
    )

    output_path = Path(
        "storage/demo_outputs/"
        "timeline_mutation_runtime.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            runtime.to_dict(),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "move_clip:",
        move_result.success,
    )
    print(
        "trim_start:",
        trim_start.success,
    )
    print(
        "trim_end:",
        trim_end.success,
    )
    print(
        "insert_clip:",
        insert_result.success,
    )
    print(
        "split_clip:",
        split_result.success,
    )
    print(
        "duplicate_clip:",
        duplicate_result.success,
    )
    print(
        "delete_clip:",
        delete_result.success,
    )
    print(
        "close_gap:",
        close_gap_result.success,
    )
    print(
        "overlap_blocked:",
        overlap_result.success is False,
    )
    print(
        "locked_track_blocked:",
        locked_result.success is False,
    )
    print(
        "revision:",
        runtime.timeline.revision,
    )
    print(
        "dirty:",
        runtime.timeline.dirty,
    )
    print(
        "event_count:",
        len(runtime.events),
    )
    print(
        "original_unchanged:",
        (
            source_timeline.revision == 1
            and source_timeline.dirty
            is False
            and source_timeline
            .get_clip("clip_2")
            .track_id
            == "video_primary"
        ),
    )
    print(
        "output:",
        output_path,
    )

    assert move_result.success is True
    assert trim_start.success is True
    assert trim_end.success is True
    assert insert_result.success is True
    assert split_result.success is True
    assert duplicate_result.success is True
    assert delete_result.success is True
    assert close_gap_result.success is True

    assert overlap_result.success is False
    assert locked_result.success is False

    assert runtime.timeline.dirty is True
    assert runtime.timeline.revision > 1
    assert len(runtime.events) == 8

    assert source_timeline.revision == 1
    assert source_timeline.dirty is False

    print(
        "\nDONE: Timeline mutation "
        "runtime test completed."
    )


if __name__ == "__main__":
    main()