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
    TimelineDirtyStatus,
    TimelineOverlapPolicy,
)


PRODUCTION_ID = (
    "221e4b01-5fb9-4b4a-a549-4fb32c455059"
)


def main() -> None:
    video_track = EditableTimelineTrack(
        track_id="video_primary",
        track_type=(
            EditableTrackType.VIDEO_PRIMARY
        ),
        name="Video chính",
        position=0,
        overlap_policy=(
            TimelineOverlapPolicy.FORBID
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
                source_duration=18.0,
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
                source_duration=18.0,
            ),
        ],
    )

    music_track = EditableTimelineTrack(
        track_id="music",
        track_type=(
            EditableTrackType.MUSIC
        ),
        name="Nhạc nền",
        position=1,
        overlap_policy=(
            TimelineOverlapPolicy.ALLOW
        ),
        clips=[
            EditableTimelineClip(
                clip_id="music_1",
                track_id="music",
                clip_type=(
                    EditableClipType.MUSIC
                ),
                start_time=0.0,
                end_time=10.0,
                source_start=0.0,
                source_end=10.0,
                source_duration=60.0,
                volume=0.18,
            )
        ],
    )

    timeline = EditableTimeline(
        production_id=PRODUCTION_ID,
        duration=10.0,
        fps=30.0,
        width=1080,
        height=1920,
        tracks=[
            video_track,
            music_track,
        ],
    )

    original = timeline.clone()

    print(
        "=== Editable Timeline Domain ==="
    )
    print(
        "production_id:",
        timeline.production_id,
    )
    print(
        "duration:",
        timeline.duration,
    )
    print(
        "fps:",
        timeline.fps,
    )
    print(
        "minimum_clip_duration:",
        timeline.minimum_clip_duration,
    )
    print(
        "track_count:",
        timeline.track_count,
    )
    print(
        "clip_count:",
        timeline.clip_count,
    )
    print(
        "dirty:",
        timeline.dirty,
    )

    timeline.mark_dirty()

    output_path = Path(
        "storage/demo_outputs/"
        "editable_timeline_domain.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            timeline.to_dict(),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    assert timeline.track_count == 2
    assert timeline.clip_count == 3

    assert (
        timeline.get_clip(
            "clip_1"
        )
        is not None
    )

    assert (
        timeline.find_clip_track(
            "music_1"
        ).track_id
        == "music"
    )

    assert timeline.dirty is True

    assert (
        timeline.dirty_status
        == TimelineDirtyStatus.DIRTY
    )

    assert original.dirty is False
    assert original.revision == 1

    assert (
        timeline.minimum_clip_duration
        == 1.0 / 30.0
    )

    print(
        "original_unchanged:",
        original.dirty is False,
    )
    print("output:", output_path)

    print(
        "\nDONE: Editable timeline "
        "domain test completed."
    )


if __name__ == "__main__":
    main()