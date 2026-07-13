from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.review import (
    AIState,
    ExportState,
    PreviewState,
    PreviewTimelineSyncState,
    PreviewTimelineSyncStatus,
    ReviewRuntimeSessionEvent,
    ReviewRuntimeSessionEventType,
    ReviewRuntimeSessionResult,
    ReviewRuntimeSessionSnapshot,
    ReviewRuntimeSessionState,
    ReviewRuntimeSessionStatus,
    ReviewState,
    ReviewWorkspace,
    SelectionState,
    TimelineState,
)
from app.review.editing import (
    EditableClipType,
    EditableTimeline,
    EditableTimelineClip,
    EditableTimelineTrack,
    EditableTrackType,
    TimelineOverlapPolicy,
)
from app.review.editing.clipboard import (
    TimelineClipboardContent,
    TimelineClipboardState,
    TimelineClipboardStatus,
)
from app.review.editing.history import (
    TimelineHistoryState,
)
from app.review.preview import (
    PreviewMediaSource,
    PreviewPlaybackStatus,
    PreviewSessionState,
)
from app.review.selection import (
    TimelineSelectableClip,
    TimelineSelectableTrack,
    TimelineSelectionCatalog,
    TimelineSelectionState,
)


PRODUCTION_ID = (
    "221e4b01-5fb9-4b4a-a549-4fb32c455059"
)


def build_workspace() -> ReviewWorkspace:
    return ReviewWorkspace(
        production_id=PRODUCTION_ID,
        version=1,
        preview=PreviewState(
            available=True,
            video_url="/media/preview.mp4",
            duration=6.0,
            width=1080,
            height=1920,
            fps=30.0,
        ),
        timeline=TimelineState(
            version="16.1.7",
            duration=6.0,
            track_count=1,
            clip_count=1,
        ),
        review=ReviewState(),
        export=ExportState(),
        ai=AIState(),
        selection=SelectionState(),
        metadata={
            "source": "domain_test",
        },
    )


def build_timeline() -> EditableTimeline:
    return EditableTimeline(
        production_id=PRODUCTION_ID,
        version="16.1.7",
        duration=6.0,
        fps=30.0,
        width=1080,
        height=1920,
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
                        track_id=(
                            "video_primary"
                        ),
                        clip_type=(
                            EditableClipType.VIDEO
                        ),
                        start_time=0.0,
                        end_time=6.0,
                        source_start=0.0,
                        source_end=6.0,
                        source_duration=20.0,
                    )
                ],
            )
        ],
    )


def build_snapshot(
    session: ReviewRuntimeSessionState,
) -> ReviewRuntimeSessionSnapshot:
    timeline = build_timeline()

    preview_source = PreviewMediaSource(
        production_id=PRODUCTION_ID,
        video_url="/media/preview.mp4",
        duration=6.0,
        width=1080,
        height=1920,
        fps=30.0,
    )

    preview_state = PreviewSessionState(
        production_id=PRODUCTION_ID,
        status=PreviewPlaybackStatus.READY,
        duration=6.0,
        total_frames=180,
    )

    preview_sync = PreviewTimelineSyncState(
        production_id=PRODUCTION_ID,
        status=(
            PreviewTimelineSyncStatus.CURRENT
        ),
        active_timeline_revision=(
            timeline.revision
        ),
        preview_timeline_revision=(
            timeline.revision
        ),
        metadata={
            "source": "initial_render",
        },
    )

    selectable_clip = TimelineSelectableClip(
        clip_id="clip_1",
        track_id="video_primary",
        start_time=0.0,
        end_time=6.0,
        clip_type="video",
    )

    selection_catalog = (
        TimelineSelectionCatalog(
            production_id=PRODUCTION_ID,
            duration=6.0,
            tracks=(
                TimelineSelectableTrack(
                    track_id="video_primary",
                    track_type="video_primary",
                    position=0,
                    clip_ids=("clip_1",),
                ),
            ),
            clips=(selectable_clip,),
            fps=30.0,
        )
    )

    selection_state = TimelineSelectionState(
        production_id=PRODUCTION_ID,
    )

    history_state = TimelineHistoryState(
        production_id=PRODUCTION_ID,
        can_undo=False,
        can_redo=False,
        undo_count=0,
        redo_count=0,
        current_revision=timeline.revision,
        maximum_history_size=50,
    )

    clipboard_content = (
        TimelineClipboardContent.empty(
            PRODUCTION_ID
        )
    )

    clipboard_state = TimelineClipboardState(
        production_id=PRODUCTION_ID,
        status=TimelineClipboardStatus.EMPTY,
        available=False,
        item_count=0,
        clip_count=0,
        clipboard_id=(
            clipboard_content.clipboard_id
        ),
    )

    return ReviewRuntimeSessionSnapshot(
        session=session,
        workspace=build_workspace(),
        timeline=timeline,
        preview_source=preview_source,
        preview_state=preview_state,
        preview_sync=preview_sync,
        selection_catalog=(
            selection_catalog
        ),
        selection_state=selection_state,
        history_state=history_state,
        clipboard_state=clipboard_state,
        clipboard_content=clipboard_content,
        metadata={
            "contract_version": "16.1.7.1",
        },
    )


def main() -> None:
    input_metadata = {
        "owner": {
            "runtime": "review",
        },
    }

    session = ReviewRuntimeSessionState.create(
        production_id=PRODUCTION_ID,
        timeline_revision=1,
        metadata=input_metadata,
    )

    input_metadata["owner"]["runtime"] = (
        "changed_outside"
    )

    metadata_isolated = (
        session.metadata["owner"]["runtime"]
        == "review"
    )

    snapshot = build_snapshot(session)
    cloned_snapshot = snapshot.clone()

    cloned_snapshot.timeline.tracks[0].clips[
        0
    ].start_time = 1.0

    snapshot_clone_isolated = (
        snapshot.timeline.tracks[0].clips[
            0
        ].start_time
        == 0.0
    )

    payload = snapshot.to_dict()
    payload["metadata"]["contract_version"] = (
        "changed"
    )
    payload["timeline"]["tracks"][0][
        "clips"
    ][0]["start_time"] = 2.0

    payload_isolated = (
        snapshot.metadata["contract_version"]
        == "16.1.7.1"
        and snapshot.timeline.tracks[0]
        .clips[0].start_time
        == 0.0
    )

    event_metadata = {
        "reason": {
            "operation": "session_created",
        },
    }

    event = ReviewRuntimeSessionEvent(
        event_type=(
            ReviewRuntimeSessionEventType
            .SESSION_CREATED
        ),
        session_id=session.session_id,
        production_id=PRODUCTION_ID,
        session_revision=session.revision,
        timeline_revision=(
            session.timeline_revision
        ),
        metadata=deepcopy(event_metadata),
    )

    event_payload = event.to_dict()
    event_payload["metadata"]["reason"][
        "operation"
    ] = "changed"

    event_isolated = (
        event.metadata["reason"]["operation"]
        == "session_created"
    )

    result = ReviewRuntimeSessionResult(
        success=True,
        state=session,
        snapshot=snapshot,
        event=event,
    )

    result_payload = result.to_dict()

    production_ids_match = all(
        value == PRODUCTION_ID
        for value in [
            snapshot.production_id,
            snapshot.workspace.production_id,
            snapshot.timeline.production_id,
            snapshot.preview_source.production_id,
            snapshot.preview_state.production_id,
            snapshot.preview_sync.production_id,
            snapshot.selection_catalog.production_id,
            snapshot.selection_state.production_id,
            snapshot.history_state.production_id,
            snapshot.clipboard_state.production_id,
            snapshot.clipboard_content.production_id,
        ]
    )

    sync_contract_valid = (
        snapshot.preview_sync.available
        and snapshot.preview_sync.current
        and not snapshot.preview_sync.stale
    )

    session_contract_valid = (
        session.active
        and not session.ready
        and not session.closed
        and session.status
        == ReviewRuntimeSessionStatus
        .INITIALIZING
    )

    serialization_valid = (
        result_payload["success"] is True
        and result_payload["snapshot"]
        ["preview"]["sync"]["status"]
        == "current"
        and result_payload["event"]
        ["event_type"]
        == "session_created"
    )

    output = Path(
        "storage/demo_outputs/"
        "review_runtime_session_domain.json"
    )
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output.write_text(
        json.dumps(
            result_payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        "=== Review Runtime Session Domain ==="
    )
    print(
        "session_created:",
        bool(session.session_id),
    )
    print(
        "session_contract_valid:",
        session_contract_valid,
    )
    print(
        "production_ids_match:",
        production_ids_match,
    )
    print(
        "sync_contract_valid:",
        sync_contract_valid,
    )
    print(
        "metadata_isolated:",
        metadata_isolated,
    )
    print(
        "snapshot_clone_isolated:",
        snapshot_clone_isolated,
    )
    print(
        "payload_isolated:",
        payload_isolated,
    )
    print(
        "event_isolated:",
        event_isolated,
    )
    print(
        "serialization_valid:",
        serialization_valid,
    )
    print("output:", output)

    assert bool(session.session_id)
    assert session_contract_valid
    assert production_ids_match
    assert sync_contract_valid
    assert metadata_isolated
    assert snapshot_clone_isolated
    assert payload_isolated
    assert event_isolated
    assert serialization_valid

    print()
    print(
        "DONE: Review runtime session "
        "domain test completed."
    )


if __name__ == "__main__":
    main()