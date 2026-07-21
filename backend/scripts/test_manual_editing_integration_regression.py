from __future__ import annotations

from app.review.editing import (
    EditableClipType, EditableTimeline, EditableTimelineClip, EditableTimelineTrack,
    EditableTrackType, TimelineMutationRuntime, TimelineRuntimeStore,
)
from app.review.editing.history import TimelineCommandHistoryRuntime
from app.review.editing.ripple import RippleEditHistoryRuntime, RippleEditPolicy, RippleEditRuntime


def clip(cid, track, start, end):
    return EditableTimelineClip(clip_id=cid, track_id=track, clip_type=EditableClipType.VIDEO, start_time=start, end_time=end)


def timeline():
    return EditableTimeline(production_id="manual-regression", fps=30, tracks=[
        EditableTimelineTrack(track_id="video", track_type=EditableTrackType.VIDEO_PRIMARY, clips=[clip("v1","video",0,2), clip("v2","video",2,4), clip("v3","video",4,7)]),
        EditableTimelineTrack(track_id="audio", track_type=EditableTrackType.AUDIO, clips=[clip("a1","audio",0,2), clip("a2","audio",4,7)]),
    ])


def run():
    store=TimelineRuntimeStore(timeline())
    mutation=TimelineMutationRuntime(store=store)
    history=TimelineCommandHistoryRuntime(mutation)
    ripple=RippleEditRuntime(store=store)
    integrated=RippleEditHistoryRuntime(ripple_runtime=ripple, history_runtime=history)

    before=store.snapshot()
    result=integrated.delete_clips(["v2"], policy=RippleEditPolicy.ALL_UNLOCKED_TRACKS, expected_revision=before.revision)
    assert result.success, result.error
    assert store.revision == before.revision + 1
    assert history.state().undo_count == 1
    assert history.state().redo_count == 0
    assert store.snapshot().get_clip("v2") is None
    assert store.snapshot().get_clip("v3").start_time == 2
    assert store.snapshot().get_clip("a2").start_time == 2

    undone=history.undo()
    assert undone.success, undone.error
    assert store.snapshot().get_clip("v2") is not None
    assert store.snapshot().get_clip("v3").start_time == 4
    assert store.snapshot().get_clip("a2").start_time == 4
    assert history.state().redo_count == 1

    redone=history.redo()
    assert redone.success, redone.error
    assert store.snapshot().get_clip("v2") is None
    assert store.snapshot().get_clip("v3").start_time == 2
    assert store.snapshot().get_clip("a2").start_time == 2

    stable=store.snapshot().to_dict()
    undo_count=history.state().undo_count
    failed=integrated.close_range(1,3,policy=RippleEditPolicy.TRACK,anchor_track_id="video",expected_revision=before.revision)
    assert not failed.success
    assert store.snapshot().to_dict() == stable
    assert history.state().undo_count == undo_count

    foreign_store=TimelineRuntimeStore(timeline())
    try:
        RippleEditHistoryRuntime(ripple_runtime=RippleEditRuntime(store=foreign_store), history_runtime=history)
        raise AssertionError("shared-store validation did not run")
    except ValueError:
        pass

    print("SPRINT 16.7.9 MANUAL EDITING INTEGRATION & REGRESSION: PASS")
    print("ripple_history_boundary: PASS")
    print("undo_redo_roundtrip: PASS")
    print("failure_isolation: PASS")
    print("shared_store_guard: PASS")


if __name__ == "__main__": run()
