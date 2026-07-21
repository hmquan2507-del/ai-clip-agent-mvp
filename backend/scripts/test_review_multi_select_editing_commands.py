from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.review.editing import (
    EditableClipType,
    EditableTimeline,
    EditableTimelineClip,
    EditableTimelineTrack,
    EditableTrackType,
    TimelineOverlapPolicy,
    build_history_from_mutation_runtime,
    build_mutation_runtime_from_store,
    build_timeline_runtime_store,
)


PRODUCTION_ID = "221e4b01-5fb9-4b4a-a549-4fb32c455059"


def build_timeline() -> EditableTimeline:
    return EditableTimeline(
        production_id=PRODUCTION_ID,
        duration=60.0,
        fps=30.0,
        tracks=[
            EditableTimelineTrack(
                track_id="overlay",
                track_type=EditableTrackType.VIDEO_OVERLAY,
                overlap_policy=TimelineOverlapPolicy.ALLOW,
                clips=[
                    EditableTimelineClip(
                        clip_id="clip_a",
                        track_id="overlay",
                        clip_type=EditableClipType.VIDEO,
                        start_time=0.0,
                        end_time=2.0,
                        source_start=0.0,
                        source_end=2.0,
                        source_duration=20.0,
                    ),
                    EditableTimelineClip(
                        clip_id="clip_b",
                        track_id="overlay",
                        clip_type=EditableClipType.VIDEO,
                        start_time=5.0,
                        end_time=7.0,
                        source_start=5.0,
                        source_end=7.0,
                        source_duration=20.0,
                    ),
                ],
            ),
            EditableTimelineTrack(
                track_id="locked",
                track_type=EditableTrackType.VIDEO_OVERLAY,
                locked=True,
                overlap_policy=TimelineOverlapPolicy.ALLOW,
                clips=[
                    EditableTimelineClip(
                        clip_id="clip_locked",
                        track_id="locked",
                        clip_type=EditableClipType.VIDEO,
                        start_time=10.0,
                        end_time=12.0,
                        source_start=0.0,
                        source_end=2.0,
                        source_duration=20.0,
                    ),
                ],
            ),
        ],
    )


def main() -> None:
    source = build_timeline()
    source_before = source.to_dict()
    store = build_timeline_runtime_store(source)
    mutation = build_mutation_runtime_from_store(store)
    history = build_history_from_mutation_runtime(mutation)

    initial_revision = store.revision
    move = history.move_clips(["clip_a", "clip_b"], 2.0)
    moved = store.snapshot()
    move_once = move.success and store.revision == initial_revision + 1
    spacing_preserved = (
        moved.get_clip("clip_a").start_time == 2.0
        and moved.get_clip("clip_b").start_time == 7.0
    )

    undo = history.undo()
    undo_atomic = (
        undo.success
        and store.snapshot().get_clip("clip_a").start_time == 0.0
        and history.state().redo_count == 1
    )
    history.redo()

    before_duplicate_revision = store.revision
    duplicate = history.duplicate_clips(["clip_a", "clip_b"])
    duplicate_ids = list(
        (duplicate.mutation_result.metadata if duplicate.mutation_result else {})
        .get("duplicated_clip_ids", [])
    )
    duplicate_once = (
        duplicate.success
        and len(duplicate_ids) == 2
        and store.revision == before_duplicate_revision + 1
    )

    before_delete_revision = store.revision
    delete = history.delete_clips(duplicate_ids)
    delete_once = (
        delete.success
        and store.revision == before_delete_revision + 1
        and all(store.snapshot().get_clip(clip_id) is None for clip_id in duplicate_ids)
    )

    before_failure = store.snapshot().to_dict()
    failed = history.move_clips(["clip_a", "clip_locked"], 1.0)
    failure_read_only = (
        not failed.success
        and store.snapshot().to_dict() == before_failure
    )

    checks = {
        "operations_complete": True,
        "move_single_commit": move_once,
        "relative_spacing_preserved": spacing_preserved,
        "undo_redo_atomic": undo_atomic,
        "duplicate_single_commit": duplicate_once,
        "delete_single_commit": delete_once,
        "locked_failure_read_only": failure_read_only,
        "source_unchanged": source.to_dict() == source_before,
        "history_single_command_boundary": history.state().undo_count == 3,
    }
    assert all(checks.values()), checks

    output = Path("storage/demo_outputs/review_multi_select_editing_commands.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(checks, indent=2), encoding="utf-8")

    print("=== Multi-select Editing Commands ===")
    for name, valid in checks.items():
        print(f"{name}: {valid}")
    print(f"output: {output}")
    print("\nDONE: Multi-select editing commands test completed.")


if __name__ == "__main__":
    main()
