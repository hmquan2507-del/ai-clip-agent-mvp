from __future__ import annotations

from app.review.editing import (
    EditableClipType,
    EditableTimeline,
    EditableTimelineClip,
    EditableTimelineTrack,
    EditableTrackType,
    TimelineRuntimeStore,
)
from app.review.editing.ripple import RippleEditPolicy, RippleEditRuntime


def clip(cid, track, start, end):
    return EditableTimelineClip(
        clip_id=cid,
        track_id=track,
        clip_type=EditableClipType.VIDEO,
        start_time=start,
        end_time=end,
    )


def make_timeline():
    return EditableTimeline(
        production_id="ripple-test",
        fps=30,
        tracks=[
            EditableTimelineTrack(
                track_id="video",
                track_type=EditableTrackType.VIDEO_PRIMARY,
                clips=[clip("v1", "video", 0, 2), clip("v2", "video", 2, 4), clip("v3", "video", 4, 7)],
            ),
            EditableTimelineTrack(
                track_id="audio",
                track_type=EditableTrackType.AUDIO,
                clips=[clip("a1", "audio", 0, 2), clip("a2", "audio", 4, 7)],
            ),
        ],
    )


def run():
    store = TimelineRuntimeStore(make_timeline())
    runtime = RippleEditRuntime(store=store)
    before = store.snapshot()
    result = runtime.delete_clips(["v2"], policy=RippleEditPolicy.ALL_UNLOCKED_TRACKS, expected_revision=before.revision)
    assert result.success, result.error
    assert result.timeline.revision == before.revision + 1
    assert result.timeline.get_clip("v2") is None
    assert result.timeline.get_clip("v3").start_time == 2
    assert result.timeline.get_clip("a2").start_time == 2
    assert len(store.changes) == 1

    stable = store.snapshot().to_dict()
    conflict = runtime.close_range(0, 1, policy=RippleEditPolicy.TRACK, anchor_track_id="video", expected_revision=before.revision)
    assert conflict.success is False
    assert store.snapshot().to_dict() == stable

    crossing_store = TimelineRuntimeStore(EditableTimeline(
        production_id="crossing",
        tracks=[EditableTimelineTrack(
            track_id="video",
            track_type=EditableTrackType.VIDEO_PRIMARY,
            clips=[clip("left", "video", 0, 3), clip("right", "video", 4, 6)],
        )],
    ))
    crossing_runtime = RippleEditRuntime(store=crossing_store)
    crossing_before = crossing_store.snapshot().to_dict()
    rejected = crossing_runtime.close_range(2, 4, policy=RippleEditPolicy.TRACK, anchor_track_id="video")
    assert rejected.success is False
    assert crossing_store.snapshot().to_dict() == crossing_before

    locked = make_timeline()
    locked.get_track("audio").locked = True
    locked_store = TimelineRuntimeStore(locked)
    locked_runtime = RippleEditRuntime(store=locked_store)
    ok = locked_runtime.delete_clips(["v2"], policy=RippleEditPolicy.ALL_UNLOCKED_TRACKS)
    assert ok.success is True
    assert ok.timeline.get_clip("a2").start_time == 4

    print("SPRINT 16.7.8 RIPPLE EDIT POLICY & RUNTIME: PASS")
    print("revision:", result.timeline.revision)
    print("shifted_clip_ids:", list(result.shifted_clip_ids))
    print("atomic_commit:", result.metadata["atomic_commit"])


if __name__ == "__main__":
    run()
