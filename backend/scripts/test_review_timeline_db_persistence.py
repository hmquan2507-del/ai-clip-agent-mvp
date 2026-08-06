from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.models  # noqa: F401  (registers every table on Base.metadata)
from app.db.base import Base
from app.repositories.timeline_repository import TimelineRepository
from app.review.editing.enums import (
    EditableClipType,
    EditableTrackType,
)
from app.review.editing.models import (
    EditableTimeline,
    EditableTimelineClip,
    EditableTimelineTrack,
)
from app.review.persistence import sync_editable_timeline_to_db


PRODUCTION_ID = "9c7b8a1e-0000-4000-8000-000000000001"


def build_timeline(
    clip_end: float,
) -> EditableTimeline:
    return EditableTimeline(
        production_id=PRODUCTION_ID,
        tracks=[
            EditableTimelineTrack(
                track_id="trk_v1",
                track_type=EditableTrackType.VIDEO_PRIMARY,
                name="Video chính",
                position=0,
                clips=[
                    EditableTimelineClip(
                        clip_id="clip_v1",
                        track_id="trk_v1",
                        clip_type=EditableClipType.VIDEO,
                        start_time=0.0,
                        end_time=clip_end,
                        source_start=0.0,
                        source_end=clip_end,
                        asset_id="9c7b8a1e-0000-4000-8000-0000000000a1",
                        text="Hook",
                    ),
                ],
            ),
            EditableTimelineTrack(
                track_id="trk_sub",
                track_type=EditableTrackType.SUBTITLE,
                name="Phụ đề",
                position=1,
                clips=[
                    EditableTimelineClip(
                        clip_id="clip_sub1",
                        track_id="trk_sub",
                        clip_type=EditableClipType.SUBTITLE,
                        start_time=0.0,
                        end_time=3.0,
                        text="Xin chào",
                    ),
                ],
            ),
        ],
    )


def main() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    db = session_factory()

    checks: dict[str, bool] = {}

    # First sync: nothing persisted yet -> a Timeline row is created.
    initial = build_timeline(clip_end=5.0)
    sync_editable_timeline_to_db(db, initial)

    repository = TimelineRepository(db)
    record = repository.get_latest_by_production(PRODUCTION_ID)

    checks["timeline_created"] = record is not None
    checks["track_count_matches"] = (
        len(record.tracks) == 2
    )

    video_track = next(
        (t for t in record.tracks if t.name == "Video chính"),
        None,
    )
    checks["video_track_found"] = video_track is not None
    checks["clip_persisted"] = (
        video_track is not None
        and len(video_track.clips) == 1
        and video_track.clips[0].timeline_end == 5.0
        and str(video_track.clips[0].asset_id)
        == "9c7b8a1e-0000-4000-8000-0000000000a1"
    )
    checks["duration_persisted"] = (
        record.duration_seconds == 5.0
    )

    first_timeline_id = record.id

    # Second sync (simulating a trim edit): same production, different
    # clip boundary and an extra clip - must replace, not accumulate.
    edited = build_timeline(clip_end=8.0)
    edited.tracks[0].clips.append(
        EditableTimelineClip(
            clip_id="clip_v2",
            track_id="trk_v1",
            clip_type=EditableClipType.VIDEO,
            start_time=8.0,
            end_time=12.0,
            source_start=8.0,
            source_end=12.0,
            asset_id="9c7b8a1e-0000-4000-8000-0000000000a1",
        )
    )
    # The real history_runtime recalculates duration after every mutation;
    # replicate that here since this test appends to `.clips` directly.
    edited.recalculate_duration()
    sync_editable_timeline_to_db(db, edited)

    record_after_edit = repository.get_latest_by_production(
        PRODUCTION_ID
    )

    checks["same_timeline_row_reused"] = (
        record_after_edit.id == first_timeline_id
    )

    video_track_after = next(
        (
            t
            for t in record_after_edit.tracks
            if t.name == "Video chính"
        ),
        None,
    )
    checks["edit_replaced_not_accumulated"] = (
        video_track_after is not None
        and len(video_track_after.clips) == 2
    )
    checks["trim_reflected"] = any(
        clip.timeline_end == 8.0
        for clip in (video_track_after.clips if video_track_after else [])
    )
    checks["duration_updated"] = (
        record_after_edit.duration_seconds == 12.0
    )

    print("=== Review Timeline DB Persistence ===")
    for key, value in checks.items():
        print(f"{key}: {value}")

    output_path = Path("storage/demo_outputs/review_timeline_db_persistence.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(checks, indent=2),
        encoding="utf-8",
    )
    print(f"output: {output_path}")

    assert all(checks.values()), checks

    db.close()

    print("\nDONE: Review timeline DB persistence test completed.")


if __name__ == "__main__":
    main()
