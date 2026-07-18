from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path
from types import MethodType
from typing import Any


sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.review.application import (
    ReviewClipboardCommandOperationError,
    ReviewClipboardCommandType,
    ReviewWorkspaceApplicationService,
    ReviewWorkspaceApplicationServiceInterface,
)


PRODUCTION_ID = "clipboard-application-test"
SESSION_ID = "clipboard-session-test"


def build_probe() -> tuple[
    ReviewWorkspaceApplicationService,
    list[dict[str, Any]],
]:
    service = object.__new__(
        ReviewWorkspaceApplicationService
    )
    calls: list[dict[str, Any]] = []

    def execute_probe(
        self: ReviewWorkspaceApplicationService,
        production_id: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        payload = {
            "production_id": production_id,
            **kwargs,
        }
        calls.append(payload)
        return payload

    service._execute_clipboard_command = (
        MethodType(execute_probe, service)
    )
    return service, calls


def main() -> None:
    service, calls = build_probe()

    copy_result = service.copy_timeline_clips(
        PRODUCTION_ID,
        session_id=SESSION_ID,
        clip_ids=[" clip_1 ", "clip_1", "clip_2"],
        expected_revision=4,
    )
    cut_result = service.cut_timeline_clips(
        PRODUCTION_ID,
        session_id=SESSION_ID,
        clip_ids=["clip_1", "clip_2"],
        expected_revision=4,
    )
    paste_result = service.paste_timeline_clips(
        PRODUCTION_ID,
        session_id=SESSION_ID,
        at_time=8.5,
        target_track_id=" video_overlay ",
        track_mapping={
            " video_primary ": " video_overlay ",
        },
        expected_revision=5,
    )
    restore_result = (
        service.restore_timeline_clipboard_history(
            PRODUCTION_ID,
            session_id=SESSION_ID,
            entry_id=" history_1 ",
            expected_revision=5,
        )
    )
    clear_result = service.clear_timeline_clipboard(
        PRODUCTION_ID,
        session_id=SESSION_ID,
        expected_revision=5,
    )
    clear_history_result = (
        service.clear_timeline_clipboard_history(
            PRODUCTION_ID,
            session_id=SESSION_ID,
            expected_revision=5,
        )
    )

    invalid_clip_ids_blocked = False
    try:
        service.copy_timeline_clips(
            PRODUCTION_ID,
            session_id=SESSION_ID,
            clip_ids=["", "   "],
        )
    except ValueError:
        invalid_clip_ids_blocked = True

    invalid_time_blocked = False
    try:
        service.paste_timeline_clips(
            PRODUCTION_ID,
            session_id=SESSION_ID,
            at_time=-1.0,
        )
    except ValueError:
        invalid_time_blocked = True

    error = ReviewClipboardCommandOperationError(
        "Clipboard failed.",
        production_id=PRODUCTION_ID,
        session_id=SESSION_ID,
        operation="paste",
        metadata={"nested": {"value": 1}},
    )
    error_payload = error.to_dict()
    error_payload["metadata"]["nested"]["value"] = 99

    required_methods = {
        "copy_timeline_clips",
        "cut_timeline_clips",
        "paste_timeline_clips",
        "restore_timeline_clipboard_history",
        "clear_timeline_clipboard",
        "clear_timeline_clipboard_history",
    }
    interface_methods = {
        name
        for name, member in inspect.getmembers(
            ReviewWorkspaceApplicationServiceInterface,
            predicate=inspect.isfunction,
        )
    }
    source = inspect.getsource(
        ReviewWorkspaceApplicationService
    )

    checks = {
        "interface_contract_valid": (
            required_methods <= interface_methods
            and not ReviewWorkspaceApplicationService
            .__abstractmethods__
        ),
        "operations_complete": (
            {item.value for item in ReviewClipboardCommandType}
            == {
                "copy",
                "cut",
                "paste",
                "restore_history",
                "clear_content",
                "clear_history",
            }
        ),
        "copy_delegated": (
            copy_result["operation"]
            is ReviewClipboardCommandType.COPY
            and copy_result["metadata"]["clip_ids"]
            == ["clip_1", "clip_2"]
        ),
        "cut_delegated": (
            cut_result["operation"]
            is ReviewClipboardCommandType.CUT
        ),
        "paste_delegated": (
            paste_result["operation"]
            is ReviewClipboardCommandType.PASTE
            and paste_result["metadata"]["at_time"] == 8.5
            and paste_result["metadata"]["target_track_id"]
            == "video_overlay"
            and paste_result["metadata"]["track_mapping"]
            == {"video_primary": "video_overlay"}
        ),
        "history_operations_delegated": (
            restore_result["operation"]
            is ReviewClipboardCommandType.RESTORE_HISTORY
            and restore_result["metadata"]["entry_id"]
            == "history_1"
            and clear_history_result["operation"]
            is ReviewClipboardCommandType.CLEAR_HISTORY
        ),
        "clear_content_delegated": (
            clear_result["operation"]
            is ReviewClipboardCommandType.CLEAR_CONTENT
        ),
        "expected_revision_forwarded": (
            all(
                call["expected_revision"] in {4, 5}
                for call in calls
            )
        ),
        "invalid_clip_ids_blocked": (
            invalid_clip_ids_blocked
        ),
        "invalid_time_blocked": invalid_time_blocked,
        "shared_lock_used": (
            "with self._timeline_command_lock" in source
            and "def _execute_clipboard_command" in source
        ),
        "clipboard_runtime_delegated": (
            "session.graph.clipboard_runtime" in source
        ),
        "error_payload_isolated": (
            error.metadata["nested"]["value"] == 1
        ),
        "serialization_valid": bool(
            json.dumps(
                {
                    "calls": [
                        {
                            key: (
                                value.value
                                if isinstance(
                                    value,
                                    ReviewClipboardCommandType,
                                )
                                else value
                            )
                            for key, value in call.items()
                            if key != "executor"
                        }
                        for call in calls
                    ]
                }
            )
        ),
    }

    assert all(checks.values()), checks

    print("=== Review Timeline Clipboard Application Service ===")
    for name, passed in checks.items():
        print(f"{name}: {passed}")

    output_path = Path(
        "storage/demo_outputs/"
        "review_timeline_clipboard_application_service.json"
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
        "\nDONE: Review timeline clipboard "
        "application service test completed."
    )


if __name__ == "__main__":
    main()
