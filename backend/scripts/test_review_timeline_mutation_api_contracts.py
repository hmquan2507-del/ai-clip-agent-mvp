from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import ValidationError


BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(BACKEND_ROOT),
    )


from app.review.api import (
    REVIEW_TIMELINE_COMMAND_API_CONTRACT_VERSION,
    REVIEW_WORKSPACE_API_CONTRACT_VERSION,
    CloseTimelineGapRequest,
    DeleteTimelineClipRequest,
    DuplicateTimelineClipRequest,
    MoveTimelineClipRequest,
    RedoTimelineCommandRequest,
    ReviewTimelineCommandOperation,
    ReviewTimelineCommandResponse,
    SplitTimelineClipRequest,
    TrimTimelineClipEndRequest,
    TrimTimelineClipStartRequest,
    UndoTimelineCommandRequest,
)


OUTPUT_PATH = (
    BACKEND_ROOT
    / "storage"
    / "demo_outputs"
    / "review_timeline_mutation_api_contracts.json"
)


def validation_fails(
    schema_type: type,
    payload: dict,
) -> bool:
    try:
        schema_type.model_validate(payload)
    except ValidationError:
        return True

    return False


def main() -> None:
    production_id = (
        "221e4b01-5fb9-4b4a-a549-4fb32c455059"
    )
    session_id = "review-session-001"

    legacy_contract_preserved = (
        REVIEW_WORKSPACE_API_CONTRACT_VERSION
        == "16.2.3"
    )

    timeline_contract_valid = (
        REVIEW_TIMELINE_COMMAND_API_CONTRACT_VERSION
        == "16.4.1"
    )

    expected_operations = {
        "move_clip",
        "trim_clip_start",
        "trim_clip_end",
        "split_clip",
        "duplicate_clip",
        "delete_clip",
        "close_gap",
        "undo",
        "redo",
    }

    operations_complete = {
        operation.value
        for operation in ReviewTimelineCommandOperation
    } == expected_operations

    move_request = MoveTimelineClipRequest(
        session_id=session_id,
        expected_revision=3,
        clip_id="clip_1",
        new_start_time=2.5,
        target_track_id="track_video",
    )

    move_contract_valid = (
        move_request.session_id == session_id
        and move_request.expected_revision == 3
        and move_request.clip_id == "clip_1"
        and move_request.new_start_time == 2.5
        and move_request.target_track_id
        == "track_video"
    )

    trim_start_request = (
        TrimTimelineClipStartRequest(
            session_id=session_id,
            clip_id="clip_1",
            new_start_time=1.0,
        )
    )

    trim_end_request = (
        TrimTimelineClipEndRequest(
            session_id=session_id,
            clip_id="clip_1",
            new_end_time=4.0,
        )
    )

    trim_contracts_valid = (
        trim_start_request.new_start_time == 1.0
        and trim_end_request.new_end_time == 4.0
    )

    split_request = SplitTimelineClipRequest(
        session_id=session_id,
        clip_id="clip_1",
        split_time=2.0,
        right_clip_id="clip_1_right",
    )

    split_contract_valid = (
        split_request.split_time == 2.0
        and split_request.right_clip_id
        == "clip_1_right"
    )

    duplicate_request = (
        DuplicateTimelineClipRequest(
            session_id=session_id,
            clip_id="clip_1",
            new_clip_id="clip_1_copy",
            new_start_time=6.0,
            target_track_id="track_video",
        )
    )

    duplicate_contract_valid = (
        duplicate_request.new_clip_id
        == "clip_1_copy"
        and duplicate_request.new_start_time
        == 6.0
        and duplicate_request.target_track_id
        == "track_video"
    )

    delete_request = DeleteTimelineClipRequest(
        session_id=session_id,
        clip_id="clip_1",
    )

    delete_defaults_valid = (
        delete_request.close_gap is False
    )

    close_gap_request = CloseTimelineGapRequest(
        session_id=session_id,
        track_id="track_video",
        gap_start=4.0,
        gap_end=6.0,
    )

    close_gap_contract_valid = (
        close_gap_request.gap_start == 4.0
        and close_gap_request.gap_end == 6.0
    )

    undo_request = UndoTimelineCommandRequest(
        session_id=session_id,
        expected_revision=4,
    )

    redo_request = RedoTimelineCommandRequest(
        session_id=session_id,
    )

    history_contracts_valid = (
        undo_request.expected_revision == 4
        and redo_request.expected_revision is None
    )

    invalid_session_blocked = validation_fails(
        MoveTimelineClipRequest,
        {
            "session_id": "",
            "clip_id": "clip_1",
            "new_start_time": 1.0,
        },
    )

    negative_time_blocked = validation_fails(
        MoveTimelineClipRequest,
        {
            "session_id": session_id,
            "clip_id": "clip_1",
            "new_start_time": -1.0,
        },
    )

    invalid_revision_blocked = validation_fails(
        MoveTimelineClipRequest,
        {
            "session_id": session_id,
            "expected_revision": 0,
            "clip_id": "clip_1",
            "new_start_time": 1.0,
        },
    )

    invalid_gap_blocked = validation_fails(
        CloseTimelineGapRequest,
        {
            "session_id": session_id,
            "track_id": "track_video",
            "gap_start": 5.0,
            "gap_end": 5.0,
        },
    )

    extra_fields_blocked = validation_fails(
        DeleteTimelineClipRequest,
        {
            "session_id": session_id,
            "clip_id": "clip_1",
            "unexpected": True,
        },
    )

    source_snapshot = {
        "production_id": production_id,
        "session_id": session_id,
        "timeline": {
            "revision": 4,
            "dirty": True,
        },
    }

    source_command = {
        "command_id": "command-001",
        "operation_type": "move_clip",
        "label": "Di chuyển clip",
    }

    source_event = {
        "action": "execute",
        "production_id": production_id,
    }

    source_history = {
        "can_undo": True,
        "can_redo": False,
        "undo_count": 1,
        "redo_count": 0,
        "current_revision": 4,
    }

    response = ReviewTimelineCommandResponse(
        operation=(
            ReviewTimelineCommandOperation
            .MOVE_CLIP
        ),
        production_id=production_id,
        session_id=session_id,
        snapshot=source_snapshot,
        command=source_command,
        event=source_event,
        history=source_history,
        metadata={
            "expected_revision": 3,
            "current_revision": 4,
        },
    )

    response_contract_valid = (
        response.success is True
        and response.contract_version == "16.4.1"
        and response.operation
        == ReviewTimelineCommandOperation.MOVE_CLIP
        and response.production_id
        == production_id
        and response.session_id == session_id
    )

    source_snapshot["timeline"]["revision"] = 99
    source_command["label"] = "changed"
    source_event["action"] = "changed"
    source_history["undo_count"] = 99

    response_isolated = (
        response.snapshot["timeline"]["revision"]
        == 4
        and response.command is not None
        and response.command["label"]
        == "Di chuyển clip"
        and response.event is not None
        and response.event["action"]
        == "execute"
        and response.history["undo_count"] == 1
    )

    serialized = response.model_dump(
        mode="json"
    )

    serialization_valid = (
        serialized["contract_version"]
        == "16.4.1"
        and serialized["operation"]
        == "move_clip"
        and serialized["snapshot"]["timeline"][
            "revision"
        ]
        == 4
        and serialized["history"]["can_undo"]
        is True
    )

    checks = {
        "legacy_contract_preserved": (
            legacy_contract_preserved
        ),
        "timeline_contract_valid": (
            timeline_contract_valid
        ),
        "operations_complete": (
            operations_complete
        ),
        "move_contract_valid": (
            move_contract_valid
        ),
        "trim_contracts_valid": (
            trim_contracts_valid
        ),
        "split_contract_valid": (
            split_contract_valid
        ),
        "duplicate_contract_valid": (
            duplicate_contract_valid
        ),
        "delete_defaults_valid": (
            delete_defaults_valid
        ),
        "close_gap_contract_valid": (
            close_gap_contract_valid
        ),
        "history_contracts_valid": (
            history_contracts_valid
        ),
        "invalid_session_blocked": (
            invalid_session_blocked
        ),
        "negative_time_blocked": (
            negative_time_blocked
        ),
        "invalid_revision_blocked": (
            invalid_revision_blocked
        ),
        "invalid_gap_blocked": (
            invalid_gap_blocked
        ),
        "extra_fields_blocked": (
            extra_fields_blocked
        ),
        "response_contract_valid": (
            response_contract_valid
        ),
        "response_isolated": (
            response_isolated
        ),
        "serialization_valid": (
            serialization_valid
        ),
    }

    assert all(checks.values()), checks

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            {
                "checks": checks,
                "response": serialized,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "=== Review Timeline Mutation "
        "API Contracts ==="
    )

    for name, value in checks.items():
        print(f"{name}: {value}")

    print(f"output: {OUTPUT_PATH.relative_to(BACKEND_ROOT)}")
    print()
    print(
        "DONE: Review timeline mutation "
        "API contracts test completed."
    )


if __name__ == "__main__":
    main()