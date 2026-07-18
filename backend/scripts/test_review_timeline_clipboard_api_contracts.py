from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import ValidationError


sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.review.api import (
    REVIEW_CLIPBOARD_API_CONTRACT_VERSION,
    REVIEW_TIMELINE_COMMAND_API_CONTRACT_VERSION,
    REVIEW_WORKSPACE_API_CONTRACT_VERSION,
    ClearTimelineClipboardHistoryRequest,
    ClearTimelineClipboardRequest,
    CopyTimelineClipsRequest,
    CutTimelineClipsRequest,
    PasteTimelineClipsRequest,
    RestoreTimelineClipboardHistoryRequest,
    ReviewClipboardCommandResponse,
    ReviewClipboardOperation,
    ReviewTimelineCommandResponse,
    ReviewWorkspaceSessionResponse,
)


PRODUCTION_ID = "clipboard-contract-production"
SESSION_ID = "clipboard-contract-session"


def validation_blocked(factory) -> bool:
    try:
        factory()
    except (ValidationError, ValueError, TypeError):
        return True
    return False


def main() -> None:
    copy_request = CopyTimelineClipsRequest(
        session_id=SESSION_ID,
        clip_ids=[" clip_1 ", "clip_1", "clip_2"],
        expected_revision=3,
    )
    cut_request = CutTimelineClipsRequest(
        session_id=SESSION_ID,
        clip_ids=["clip_1", "clip_2"],
        expected_revision=3,
    )
    paste_request = PasteTimelineClipsRequest(
        session_id=SESSION_ID,
        at_time=8.5,
        target_track_id="video_overlay",
        track_mapping={
            " video_primary ": " video_overlay ",
        },
        expected_revision=4,
    )
    restore_request = (
        RestoreTimelineClipboardHistoryRequest(
            session_id=SESSION_ID,
            entry_id="history_1",
            expected_revision=4,
        )
    )
    clear_request = ClearTimelineClipboardRequest(
        session_id=SESSION_ID,
        expected_revision=4,
    )
    clear_history_request = (
        ClearTimelineClipboardHistoryRequest(
            session_id=SESSION_ID,
            expected_revision=4,
        )
    )

    snapshot_payload = {
        "timeline": {"revision": 4},
        "clipboard": {"state": {"available": True}},
    }
    clipboard_payload = {
        "state": {"available": True},
        "content": {
            "items": [{"source_clip_id": "clip_1"}],
        },
        "history_state": {"entry_count": 1},
        "history": [{"entry_id": "history_1"}],
    }
    history_payload = {
        "success": True,
        "operation": "paste_clips",
    }
    metadata_payload = {
        "request": {"at_time": 8.5},
    }

    response = ReviewClipboardCommandResponse(
        operation=ReviewClipboardOperation.PASTE,
        production_id=PRODUCTION_ID,
        session_id=SESSION_ID,
        previous_revision=3,
        current_revision=4,
        snapshot=snapshot_payload,
        clipboard=clipboard_payload,
        timeline_history=history_payload,
        metadata=metadata_payload,
    )

    snapshot_payload["timeline"]["revision"] = 99
    clipboard_payload["state"]["available"] = False
    history_payload["success"] = False
    metadata_payload["request"]["at_time"] = 99.0

    response_payload = response.model_dump(
        mode="json"
    )
    response_payload["clipboard"]["state"][
        "available"
    ] = False

    checks = {
        "legacy_contracts_preserved": (
            REVIEW_WORKSPACE_API_CONTRACT_VERSION
            == "16.2.3"
            and REVIEW_TIMELINE_COMMAND_API_CONTRACT_VERSION
            == "16.4.1"
            and ReviewWorkspaceSessionResponse is not None
            and ReviewTimelineCommandResponse is not None
        ),
        "clipboard_contract_version_valid": (
            REVIEW_CLIPBOARD_API_CONTRACT_VERSION
            == "16.4.8"
            and response.contract_version == "16.4.8"
        ),
        "operations_complete": (
            {item.value for item in ReviewClipboardOperation}
            == {
                "copy",
                "cut",
                "paste",
                "restore_history",
                "clear_content",
                "clear_history",
            }
        ),
        "copy_contract_valid": (
            copy_request.clip_ids
            == ["clip_1", "clip_2"]
            and copy_request.expected_revision == 3
        ),
        "cut_contract_valid": (
            cut_request.clip_ids
            == ["clip_1", "clip_2"]
        ),
        "paste_contract_valid": (
            paste_request.at_time == 8.5
            and paste_request.target_track_id
            == "video_overlay"
            and paste_request.track_mapping
            == {"video_primary": "video_overlay"}
        ),
        "history_contracts_valid": (
            restore_request.entry_id == "history_1"
            and clear_request.expected_revision == 4
            and clear_history_request.expected_revision == 4
        ),
        "empty_clip_ids_blocked": validation_blocked(
            lambda: CopyTimelineClipsRequest(
                session_id=SESSION_ID,
                clip_ids=["", "   "],
            )
        ),
        "negative_time_blocked": validation_blocked(
            lambda: PasteTimelineClipsRequest(
                session_id=SESSION_ID,
                at_time=-0.1,
            )
        ),
        "invalid_mapping_blocked": validation_blocked(
            lambda: PasteTimelineClipsRequest(
                session_id=SESSION_ID,
                at_time=0.0,
                track_mapping={"": "video_overlay"},
            )
        ),
        "invalid_revision_blocked": validation_blocked(
            lambda: ClearTimelineClipboardRequest(
                session_id=SESSION_ID,
                expected_revision=0,
            )
        ),
        "extra_fields_blocked": validation_blocked(
            lambda: CutTimelineClipsRequest(
                session_id=SESSION_ID,
                clip_ids=["clip_1"],
                unexpected=True,
            )
        ),
        "response_contract_valid": (
            response.success is True
            and response.operation
            is ReviewClipboardOperation.PASTE
            and response.previous_revision == 3
            and response.current_revision == 4
        ),
        "response_input_isolated": (
            response.snapshot["timeline"]["revision"] == 4
            and response.clipboard["state"]["available"]
            is True
            and response.timeline_history is not None
            and response.timeline_history["success"] is True
            and response.metadata["request"]["at_time"]
            == 8.5
        ),
        "response_output_isolated": (
            response.clipboard["state"]["available"]
            is True
        ),
        "serialization_valid": bool(
            json.dumps(response.model_dump(mode="json"))
        ),
    }

    assert all(checks.values()), checks

    print("=== Review Timeline Clipboard API Contracts ===")
    for name, passed in checks.items():
        print(f"{name}: {passed}")

    output_path = Path(
        "storage/demo_outputs/"
        "review_timeline_clipboard_api_contracts.json"
    )
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output_path.write_text(
        json.dumps(checks, indent=2),
        encoding="utf-8",
    )
    print(f"output: {output_path}")
    print(
        "\nDONE: Review timeline clipboard API "
        "contracts test completed."
    )


if __name__ == "__main__":
    main()
