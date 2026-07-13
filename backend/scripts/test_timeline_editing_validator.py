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
    TimelineEditingIssueCode,
    TimelineEditingValidator,
    TimelineOverlapPolicy,
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
                name="Video chính",
                position=0,
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
                        source_duration=18.0,
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
                        end_time=10.0,
                        source_start=4.0,
                        source_end=10.0,
                        source_duration=18.0,
                    ),
                ],
            ),
            EditableTimelineTrack(
                track_id="music",
                track_type=(
                    EditableTrackType.MUSIC
                ),
                name="Nhạc nền",
                position=1,
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
                name="Video khóa",
                position=2,
                locked=True,
                overlap_policy=(
                    TimelineOverlapPolicy
                    .FORBID
                ),
            ),
        ],
    )


def has_issue(
    result,
    code: TimelineEditingIssueCode,
) -> bool:
    return any(
        issue.code == code
        for issue in result.issues
    )


def main() -> None:
    timeline = build_timeline()
    validator = (
        TimelineEditingValidator()
    )

    valid_timeline = (
        validator.validate_timeline(
            timeline
        )
    )

    valid_move = validator.validate_move(
        timeline=timeline,
        clip_id="clip_2",
        target_track_id=(
            "video_primary"
        ),
        new_start_time=4.0,
    )

    overlap_move = (
        validator.validate_move(
            timeline=timeline,
            clip_id="clip_2",
            target_track_id=(
                "video_primary"
            ),
            new_start_time=2.0,
        )
    )

    locked_move = validator.validate_move(
        timeline=timeline,
        clip_id="clip_1",
        target_track_id=(
            "locked_video"
        ),
        new_start_time=0.0,
    )

    trim_start = (
        validator.validate_trim_start(
            timeline=timeline,
            clip_id="clip_2",
            new_start_time=5.0,
        )
    )

    invalid_trim = (
        validator.validate_trim_end(
            timeline=timeline,
            clip_id="clip_1",
            new_end_time=0.01,
        )
    )

    insert_clip = EditableTimelineClip(
        clip_id="clip_3",
        track_id="video_primary",
        clip_type=(
            EditableClipType.VIDEO
        ),
        start_time=10.0,
        end_time=14.0,
        source_start=10.0,
        source_end=14.0,
        source_duration=18.0,
    )

    valid_insert = (
        validator.validate_insert(
            timeline=timeline,
            track_id="video_primary",
            clip=insert_clip,
        )
    )

    incompatible_insert = (
        validator.validate_insert(
            timeline=timeline,
            track_id="music",
            clip=insert_clip,
        )
    )

    source_overflow = (
        EditableTimelineClip(
            clip_id="overflow",
            track_id="video_primary",
            clip_type=(
                EditableClipType.VIDEO
            ),
            start_time=10.0,
            end_time=14.0,
            source_start=16.0,
            source_end=20.0,
            source_duration=18.0,
        )
    )

    overflow_result = (
        validator.validate_insert(
            timeline=timeline,
            track_id="video_primary",
            clip=source_overflow,
        )
    )

    output = {
        "valid_timeline": (
            valid_timeline.to_dict()
        ),
        "valid_move": valid_move.to_dict(),
        "overlap_move": (
            overlap_move.to_dict()
        ),
        "locked_move": (
            locked_move.to_dict()
        ),
        "trim_start": trim_start.to_dict(),
        "invalid_trim": (
            invalid_trim.to_dict()
        ),
        "valid_insert": (
            valid_insert.to_dict()
        ),
        "incompatible_insert": (
            incompatible_insert.to_dict()
        ),
        "source_overflow": (
            overflow_result.to_dict()
        ),
    }

    output_path = Path(
        "storage/demo_outputs/"
        "timeline_editing_validator.json"
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

    print(
        "=== Timeline Editing Validator ==="
    )
    print(
        "timeline_valid:",
        valid_timeline.valid,
    )
    print(
        "valid_move:",
        valid_move.valid,
    )
    print(
        "overlap_blocked:",
        not overlap_move.valid,
    )
    print(
        "locked_track_blocked:",
        not locked_move.valid,
    )
    print(
        "trim_start_valid:",
        trim_start.valid,
    )
    print(
        "invalid_trim_blocked:",
        not invalid_trim.valid,
    )
    print(
        "valid_insert:",
        valid_insert.valid,
    )
    print(
        "incompatible_insert_blocked:",
        not incompatible_insert.valid,
    )
    print(
        "source_overflow_blocked:",
        not overflow_result.valid,
    )
    print("output:", output_path)

    assert valid_timeline.valid is True
    assert valid_move.valid is True

    assert overlap_move.valid is False
    assert has_issue(
        overlap_move,
        TimelineEditingIssueCode
        .CLIP_OVERLAP,
    )

    assert locked_move.valid is False
    assert has_issue(
        locked_move,
        TimelineEditingIssueCode
        .TRACK_LOCKED,
    )

    assert trim_start.valid is True
    assert invalid_trim.valid is False

    assert valid_insert.valid is True

    assert (
        incompatible_insert.valid
        is False
    )

    assert overflow_result.valid is False
    assert has_issue(
        overflow_result,
        TimelineEditingIssueCode
        .SOURCE_DURATION_EXCEEDED,
    )

    print(
        "\nDONE: Timeline editing "
        "validator test completed."
    )


if __name__ == "__main__":
    main()