from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.review.editing.enums import EditableClipType, EditableTrackType, TimelineDirtyStatus
from app.review.editing.models import EditableTimeline, EditableTimelineClip, EditableTimelineTrack
from app.review.editing.state.store import TimelineRuntimeStore
from app.review.render import ReviewRenderContractValidator, ReviewToRenderHandoffRuntime


def make_timeline(*, dirty=False):
    return EditableTimeline(
        production_id="production-1681",
        revision=7,
        dirty_status=TimelineDirtyStatus.DIRTY if dirty else TimelineDirtyStatus.CLEAN,
        tracks=[EditableTimelineTrack(
            track_id="video-1",
            track_type=EditableTrackType.VIDEO_PRIMARY,
            clips=[EditableTimelineClip(
                clip_id="clip-1",
                track_id="video-1",
                clip_type=EditableClipType.VIDEO,
                start_time=0,
                end_time=5,
                asset_id="asset-1",
            )],
        )],
    )


def main():
    store = TimelineRuntimeStore(make_timeline())
    runtime = ReviewToRenderHandoffRuntime(store)

    first = runtime.create_contract(expected_revision=7, render_options={"format": "mp4"})
    second = runtime.create_contract(expected_revision=7, render_options={"format": "mp4"})
    assert first.snapshot_id != second.snapshot_id
    assert first.timeline_revision == second.timeline_revision == 7
    assert first.timeline == second.timeline
    ReviewRenderContractValidator().validate(first, expected_revision=7)

    frozen = first.timeline
    updated = store.snapshot()
    updated.revision = 8
    updated.mark_clean()
    store.commit(updated, reason="post_handoff_edit")
    assert first.timeline["revision"] == 7
    assert frozen == first.timeline

    dirty_runtime = ReviewToRenderHandoffRuntime(TimelineRuntimeStore(make_timeline(dirty=True)))
    dirty_result = dirty_runtime.handoff(expected_revision=7)
    assert not dirty_result.success and dirty_result.error_code == "timeline_dirty"

    mismatch = runtime.handoff(expected_revision=99)
    assert not mismatch.success and mismatch.error_code == "timeline_revision_mismatch"

    tampered = replace(first, timeline={**first.timeline, "revision": 999})
    try:
        ReviewRenderContractValidator().validate(tampered)
        raise AssertionError("tampered contract should fail")
    except ValueError:
        pass

    print("SPRINT 16.8.1 REVIEW-TO-RENDER HANDOFF: PASS")
    print("snapshot_immutable: True")
    print("checksum_validated: True")
    print("dirty_workspace_rejected: True")
    print("revision_conflict_rejected: True")


if __name__ == "__main__":
    main()
