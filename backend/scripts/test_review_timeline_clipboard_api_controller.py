from __future__ import annotations

import inspect
import importlib
import json
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient


sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.review.api.contracts import (
    ReviewClipboardOperation,
)
from app.review.api.dependencies import (
    get_review_workspace_application_service,
)
from app.review.api.mappers import (
    ReviewWorkspaceAPIMapper,
)
from app.review.api.router import router
from app.review.api.schemas import (
    ReviewClipboardCommandResponse,
)
from app.review.application import (
    ReviewClipboardCommandOperationError,
    ReviewTimelineRevisionConflictError,
)


PRODUCTION_ID = "221e4b01-5fb9-4b4a-a549-4fb32c455059"
SESSION_ID = "clipboard-controller-session"
BASE_PATH = f"/productions/{PRODUCTION_ID}/review"


class FakeClipboardApplicationService:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def _execute(
        self,
        operation: str,
        production_id: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        call = {
            "operation": operation,
            "production_id": production_id,
            **kwargs,
        }
        self.calls.append(call)

        if kwargs.get("expected_revision") == 99:
            raise ReviewTimelineRevisionConflictError(
                "Revision conflict.",
                production_id=production_id,
                session_id=kwargs["session_id"],
                expected_revision=99,
                current_revision=4,
            )

        if operation == "paste" and kwargs["at_time"] == 77.0:
            raise ReviewClipboardCommandOperationError(
                "Clipboard is empty.",
                production_id=production_id,
                session_id=kwargs["session_id"],
                operation=operation,
            )

        previous_revision = int(
            kwargs.get("expected_revision") or 4
        )
        current_revision = (
            previous_revision + 1
            if operation in {"cut", "paste"}
            else previous_revision
        )
        return {
            **call,
            "previous_revision": previous_revision,
            "current_revision": current_revision,
        }

    def copy_timeline_clips(self, production_id: str, **kwargs: Any):
        return self._execute("copy", production_id, **kwargs)

    def cut_timeline_clips(self, production_id: str, **kwargs: Any):
        return self._execute("cut", production_id, **kwargs)

    def paste_timeline_clips(self, production_id: str, **kwargs: Any):
        return self._execute("paste", production_id, **kwargs)

    def restore_timeline_clipboard_history(
        self,
        production_id: str,
        **kwargs: Any,
    ):
        return self._execute(
            "restore_history",
            production_id,
            **kwargs,
        )

    def clear_timeline_clipboard(self, production_id: str, **kwargs: Any):
        return self._execute("clear_content", production_id, **kwargs)

    def clear_timeline_clipboard_history(
        self,
        production_id: str,
        **kwargs: Any,
    ):
        return self._execute(
            "clear_history",
            production_id,
            **kwargs,
        )


def fake_clipboard_response(
    result: dict[str, Any],
    *,
    metadata: dict[str, Any] | None = None,
) -> ReviewClipboardCommandResponse:
    return ReviewClipboardCommandResponse(
        operation=ReviewClipboardOperation(
            result["operation"]
        ),
        production_id=result["production_id"],
        session_id=result["session_id"],
        previous_revision=(
            result["previous_revision"]
        ),
        current_revision=result["current_revision"],
        snapshot={
            "timeline": {
                "revision": result["current_revision"],
            },
        },
        clipboard={
            "state": {
                "available": (
                    result["operation"]
                    != "clear_content"
                ),
            },
            "content": {},
            "history_state": {},
            "history": [],
        },
        timeline_history=(
            {"success": True}
            if result["operation"] in {"cut", "paste"}
            else None
        ),
        metadata=metadata or {},
    )


def main() -> None:
    fake_service = FakeClipboardApplicationService()
    application = FastAPI()
    application.include_router(router)
    application.dependency_overrides[
        get_review_workspace_application_service
    ] = lambda: fake_service

    ReviewWorkspaceAPIMapper.clipboard_command_response = (
        staticmethod(fake_clipboard_response)
    )

    client = TestClient(application)

    requests = [
        (
            "POST",
            f"{BASE_PATH}/clipboard/copy",
            {
                "session_id": SESSION_ID,
                "clip_ids": ["clip_1", "clip_2"],
                "expected_revision": 4,
            },
            "copy",
        ),
        (
            "POST",
            f"{BASE_PATH}/clipboard/cut",
            {
                "session_id": SESSION_ID,
                "clip_ids": ["clip_1"],
                "expected_revision": 4,
            },
            "cut",
        ),
        (
            "POST",
            f"{BASE_PATH}/clipboard/paste",
            {
                "session_id": SESSION_ID,
                "at_time": 8.5,
                "target_track_id": "video_overlay",
                "track_mapping": {
                    "video_primary": "video_overlay",
                },
                "expected_revision": 5,
            },
            "paste",
        ),
        (
            "POST",
            f"{BASE_PATH}/clipboard/history/restore",
            {
                "session_id": SESSION_ID,
                "entry_id": "history_1",
                "expected_revision": 6,
            },
            "restore_history",
        ),
        (
            "DELETE",
            f"{BASE_PATH}/clipboard",
            {
                "session_id": SESSION_ID,
                "expected_revision": 6,
            },
            "clear_content",
        ),
        (
            "DELETE",
            f"{BASE_PATH}/clipboard/history",
            {
                "session_id": SESSION_ID,
                "expected_revision": 6,
            },
            "clear_history",
        ),
    ]

    responses = [
        client.request(method, path, json=payload)
        for method, path, payload, _ in requests
    ]
    response_operations = [
        response.json().get("operation")
        for response in responses
    ]

    conflict_response = client.post(
        f"{BASE_PATH}/clipboard/copy",
        json={
            "session_id": SESSION_ID,
            "clip_ids": ["clip_1"],
            "expected_revision": 99,
        },
    )
    failure_response = client.post(
        f"{BASE_PATH}/clipboard/paste",
        json={
            "session_id": SESSION_ID,
            "at_time": 77.0,
            "expected_revision": 4,
        },
    )
    validation_response = client.post(
        f"{BASE_PATH}/clipboard/paste",
        json={
            "session_id": SESSION_ID,
            "at_time": -1.0,
        },
    )

    openapi = application.openapi()
    expected_paths = {
        f"/productions/{{production_id}}/review{suffix}"
        for suffix in {
            "/clipboard/copy",
            "/clipboard/cut",
            "/clipboard/paste",
            "/clipboard/history/restore",
            "/clipboard",
            "/clipboard/history",
        }
    }
    mapper_source = inspect.getsource(
        ReviewWorkspaceAPIMapper
    )
    router_source = inspect.getsource(
        importlib.import_module(
            "app.review.api.router"
        )
    )

    checks = {
        "all_routes_work": (
            all(response.status_code == 200 for response in responses)
            and response_operations
            == [item[3] for item in requests]
        ),
        "all_operations_delegated": (
            [call["operation"] for call in fake_service.calls[:6]]
            == [item[3] for item in requests]
        ),
        "copy_payload_forwarded": (
            fake_service.calls[0]["clip_ids"]
            == ["clip_1", "clip_2"]
        ),
        "paste_payload_forwarded": (
            fake_service.calls[2]["at_time"] == 8.5
            and fake_service.calls[2]["target_track_id"]
            == "video_overlay"
            and fake_service.calls[2]["track_mapping"]
            == {"video_primary": "video_overlay"}
        ),
        "expected_revision_forwarded": (
            [call["expected_revision"] for call in fake_service.calls[:6]]
            == [4, 4, 5, 6, 6, 6]
        ),
        "revision_conflict_mapped": (
            conflict_response.status_code == 409
            and conflict_response.json()["error"]["code"]
            == "review_session_conflict"
        ),
        "clipboard_failure_mapped": (
            failure_response.status_code == 409
            and failure_response.json()["error"]["code"]
            == "review_clipboard_command_failed"
        ),
        "validation_blocked_before_service": (
            validation_response.status_code == 422
        ),
        "openapi_routes_complete": (
            expected_paths <= set(openapi["paths"])
        ),
        "mapper_contract_valid": (
            "def clipboard_command_response" in mapper_source
            and "ReviewClipboardCommandResponse" in mapper_source
        ),
        "controller_has_no_runtime_access": (
            ".clipboard_runtime" not in router_source
            and ".mutation_runtime" not in router_source
            and ".history_runtime" not in router_source
        ),
        "response_count_valid": len(responses) == 6,
    }

    assert all(checks.values()), checks

    print("=== Review Timeline Clipboard API Controller ===")
    for name, passed in checks.items():
        print(f"{name}: {passed}")

    output_path = Path(
        "storage/demo_outputs/"
        "review_timeline_clipboard_api_controller.json"
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
        "controller test completed."
    )


if __name__ == "__main__":
    main()
