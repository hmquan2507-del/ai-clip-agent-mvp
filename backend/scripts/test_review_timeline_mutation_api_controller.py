from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(BACKEND_ROOT),
    )


from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.review.api.dependencies import (
    get_review_workspace_application_service,
)
from app.review.api.router import (
    router as review_router,
)
from app.review.application import (
    ReviewTimelineCommandType,
    ReviewTimelineRevisionConflictError,
)


PRODUCTION_ID = (
    "221e4b01-5fb9-4b4a-a549-4fb32c455059"
)
SESSION_ID = "review-session-001"

BASE_PATH = (
    f"/api/v1/productions/"
    f"{PRODUCTION_ID}/review/timeline"
)
OPENAPI_BASE_PATH = (
    "/api/v1/productions/"
    "{production_id}/review/timeline"
)
OUTPUT_PATH = (
    BACKEND_ROOT
    / "storage"
    / "demo_outputs"
    / "review_timeline_mutation_api_controller.json"
)


class FakePayload:
    def __init__(
        self,
        payload: dict[str, Any],
    ):
        self.payload = dict(payload)

    def to_dict(self) -> dict[str, Any]:
        return dict(self.payload)


class FakeTimelineCommandResult:
    def __init__(
        self,
        operation: ReviewTimelineCommandType,
        *,
        expected_revision: int | None,
    ):
        self.operation = operation
        self.production_id = PRODUCTION_ID
        self.session_id = SESSION_ID
        self.previous_revision = 1
        self.current_revision = 2
        self.expected_revision = expected_revision

        self.snapshot = FakePayload(
            {
                "session": {
                    "session_id": SESSION_ID,
                    "production_id": PRODUCTION_ID,
                },
                "timeline": {
                    "production_id": PRODUCTION_ID,
                    "revision": 2,
                    "dirty": True,
                },
                "history": {
                    "can_undo": True,
                    "can_redo": False,
                    "undo_count": 1,
                    "redo_count": 0,
                },
            }
        )

        self.command = {
            "command_id": "command-001",
            "operation_type": operation.value,
        }
        self.event = {
            "action": "execute",
            "operation_type": operation.value,
        }
        self.history = {
            "production_id": PRODUCTION_ID,
            "current_revision": 2,
            "can_undo": True,
            "can_redo": False,
            "undo_count": 1,
            "redo_count": 0,
        }
        self.metadata = {
            "controller_test": True,
        }


class FakeApplicationService:
    def __init__(self):
        self.calls: list[
            dict[str, Any]
        ] = []

    def _execute(
        self,
        operation: ReviewTimelineCommandType,
        production_id: str,
        **kwargs: Any,
    ) -> FakeTimelineCommandResult:
        expected_revision = kwargs.get(
            "expected_revision"
        )

        if expected_revision == 999:
            raise (
                ReviewTimelineRevisionConflictError(
                    "Synthetic revision conflict.",
                    production_id=production_id,
                    session_id=kwargs["session_id"],
                    expected_revision=999,
                    current_revision=1,
                )
            )

        self.calls.append(
            {
                "operation": operation.value,
                "production_id": production_id,
                "arguments": dict(kwargs),
            }
        )

        return FakeTimelineCommandResult(
            operation,
            expected_revision=expected_revision,
        )

    def move_clip(
        self,
        production_id: str,
        **kwargs: Any,
    ) -> FakeTimelineCommandResult:
        return self._execute(
            ReviewTimelineCommandType.MOVE_CLIP,
            production_id,
            **kwargs,
        )

    def trim_clip_start(
        self,
        production_id: str,
        **kwargs: Any,
    ) -> FakeTimelineCommandResult:
        return self._execute(
            ReviewTimelineCommandType
            .TRIM_CLIP_START,
            production_id,
            **kwargs,
        )

    def trim_clip_end(
        self,
        production_id: str,
        **kwargs: Any,
    ) -> FakeTimelineCommandResult:
        return self._execute(
            ReviewTimelineCommandType
            .TRIM_CLIP_END,
            production_id,
            **kwargs,
        )

    def split_clip(
        self,
        production_id: str,
        **kwargs: Any,
    ) -> FakeTimelineCommandResult:
        return self._execute(
            ReviewTimelineCommandType.SPLIT_CLIP,
            production_id,
            **kwargs,
        )

    def duplicate_clip(
        self,
        production_id: str,
        **kwargs: Any,
    ) -> FakeTimelineCommandResult:
        return self._execute(
            ReviewTimelineCommandType
            .DUPLICATE_CLIP,
            production_id,
            **kwargs,
        )

    def delete_clip(
        self,
        production_id: str,
        **kwargs: Any,
    ) -> FakeTimelineCommandResult:
        return self._execute(
            ReviewTimelineCommandType.DELETE_CLIP,
            production_id,
            **kwargs,
        )

    def close_gap(
        self,
        production_id: str,
        **kwargs: Any,
    ) -> FakeTimelineCommandResult:
        return self._execute(
            ReviewTimelineCommandType.CLOSE_GAP,
            production_id,
            **kwargs,
        )

    def undo_timeline(
        self,
        production_id: str,
        **kwargs: Any,
    ) -> FakeTimelineCommandResult:
        return self._execute(
            ReviewTimelineCommandType.UNDO,
            production_id,
            **kwargs,
        )

    def redo_timeline(
        self,
        production_id: str,
        **kwargs: Any,
    ) -> FakeTimelineCommandResult:
        return self._execute(
            ReviewTimelineCommandType.REDO,
            production_id,
            **kwargs,
        )


def main() -> None:
    application = FastAPI()
    application.include_router(
        review_router,
        prefix="/api/v1",
    )

    service = FakeApplicationService()

    application.dependency_overrides[
        get_review_workspace_application_service
    ] = lambda: service

    cases = [
        (
            "move",
            {
                "session_id": SESSION_ID,
                "expected_revision": 1,
                "clip_id": "clip_1",
                "new_start_time": 2.0,
                "target_track_id": "track_video",
            },
            "move_clip",
        ),
        (
            "trim-start",
            {
                "session_id": SESSION_ID,
                "clip_id": "clip_1",
                "new_start_time": 1.0,
            },
            "trim_clip_start",
        ),
        (
            "trim-end",
            {
                "session_id": SESSION_ID,
                "clip_id": "clip_1",
                "new_end_time": 4.0,
            },
            "trim_clip_end",
        ),
        (
            "split",
            {
                "session_id": SESSION_ID,
                "clip_id": "clip_1",
                "split_time": 2.0,
                "right_clip_id": "clip_right",
            },
            "split_clip",
        ),
        (
            "duplicate",
            {
                "session_id": SESSION_ID,
                "clip_id": "clip_1",
                "new_clip_id": "clip_copy",
                "new_start_time": 5.0,
            },
            "duplicate_clip",
        ),
        (
            "delete",
            {
                "session_id": SESSION_ID,
                "clip_id": "clip_copy",
                "close_gap": False,
            },
            "delete_clip",
        ),
        (
            "close-gap",
            {
                "session_id": SESSION_ID,
                "track_id": "track_video",
                "gap_start": 4.0,
                "gap_end": 5.0,
            },
            "close_gap",
        ),
        (
            "undo",
            {
                "session_id": SESSION_ID,
            },
            "undo",
        ),
        (
            "redo",
            {
                "session_id": SESSION_ID,
            },
            "redo",
        ),
    ]

    with TestClient(application) as client:
        command_responses: dict[
            str,
            dict[str, Any]
        ] = {}

        all_commands_work = True

        for path, body, operation in cases:
            response = client.post(
                f"{BASE_PATH}/{path}",
                json=body,
            )
            payload = response.json()

            command_responses[path] = payload

            all_commands_work = (
                all_commands_work
                and response.status_code == 200
                and payload["success"] is True
                and payload["contract_version"]
                == "16.4.1"
                and payload["operation"]
                == operation
                and payload["session_id"]
                == SESSION_ID
                and payload["snapshot"][
                    "timeline"
                ]["revision"]
                == 2
            )

        all_commands_delegated = (
            len(service.calls) == 9
            and {
                call["operation"]
                for call in service.calls
            }
            == {
                operation
                for _, _, operation in cases
            }
        )

        expected_revision_forwarded = (
            service.calls[0][
                "arguments"
            ]["expected_revision"]
            == 1
        )

        revision_conflict_response = (
            client.post(
                f"{BASE_PATH}/undo",
                json={
                    "session_id": SESSION_ID,
                    "expected_revision": 999,
                },
            )
        )

        revision_conflict_mapped = (
            revision_conflict_response
            .status_code
            == 409
            and (
                revision_conflict_response
                .json()["error"]["code"]
                == "review_session_conflict"
            )
            and (
                revision_conflict_response
                .json()["error"]["metadata"][
                    "application_error"
                ]["expected_revision"]
                == 999
            )
            and (
                revision_conflict_response
                .json()["error"]["metadata"][
                    "application_error"
                ]["current_revision"]
                == 1
            )
        )

        calls_before_invalid = len(
            service.calls
        )

        invalid_response = client.post(
            f"{BASE_PATH}/move",
            json={
                "session_id": SESSION_ID,
                "new_start_time": -1.0,
            },
        )

        validation_blocked_before_service = (
            invalid_response.status_code == 422
            and len(service.calls)
            == calls_before_invalid
        )

        openapi = client.get(
            "/openapi.json"
        ).json()
        
        expected_paths = {
            f"{OPENAPI_BASE_PATH}/{path}"
            for path, _, _ in cases
        }

        openapi_routes_complete = all(
            path in openapi["paths"]
            and "post"
            in openapi["paths"][path]
            for path in expected_paths
        )

    mapper_result = SimpleNamespace(
        response_count=len(
            command_responses
        )
    )

    checks = {
        "all_commands_work": (
            all_commands_work
        ),
        "all_commands_delegated": (
            all_commands_delegated
        ),
        "expected_revision_forwarded": (
            expected_revision_forwarded
        ),
        "revision_conflict_mapped": (
            revision_conflict_mapped
        ),
        "validation_blocked_before_service": (
            validation_blocked_before_service
        ),
        "openapi_routes_complete": (
            openapi_routes_complete
        ),
        "response_count_valid": (
            mapper_result.response_count == 9
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
                "responses": command_responses,
                "conflict": (
                    revision_conflict_response
                    .json()
                ),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "=== Timeline Mutation "
        "API Mapper & Controller ==="
    )

    for name, value in checks.items():
        print(f"{name}: {value}")

    print(
        "output:",
        OUTPUT_PATH.relative_to(
            BACKEND_ROOT
        ),
    )
    print()
    print(
        "DONE: Timeline mutation API "
        "mapper and controller test completed."
    )


if __name__ == "__main__":
    main()