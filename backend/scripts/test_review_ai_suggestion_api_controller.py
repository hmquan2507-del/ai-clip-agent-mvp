from __future__ import annotations

import json
import sys
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


from app.review.api.dependencies import (
    get_review_ai_suggestion_application_service,
)
from app.review.api.router import router
from app.review.application import (
    ReviewAISuggestionApplicationResult,
    ReviewAISuggestionOperation,
    ReviewAISuggestionRevisionConflictError,
)
from app.review.suggestions import (
    AISuggestionLifecycleSnapshot,
    AISuggestionReadModel,
)


PRODUCTION_ID = "221e4b01-5fb9-4b4a-a549-4fb32c455059"
SESSION_ID = "review-session-16-6-4"
BASE_PATH = f"/api/v1/productions/{PRODUCTION_ID}/review"


@dataclass
class FakeTimeline:
    revision: int = 4

    def to_dict(self):
        return {"revision": self.revision}


@dataclass
class FakeWorkspaceSnapshot:
    production_id: str = PRODUCTION_ID
    session_id: str = SESSION_ID
    timeline: FakeTimeline = None

    def __post_init__(self):
        if self.timeline is None:
            self.timeline = FakeTimeline()

    def clone(self):
        return deepcopy(self)

    def to_dict(self):
        return {
            "production_id": self.production_id,
            "session_id": self.session_id,
            "timeline": self.timeline.to_dict(),
        }


@dataclass
class FakeCommandResult:
    operation: str = "move_clip"

    def clone(self):
        return deepcopy(self)

    def to_dict(self):
        return {"operation": self.operation}


class FakeSuggestionService:
    def __init__(self):
        self.calls: list[dict[str, Any]] = []

    def _result(self, operation, *, command=False):
        return ReviewAISuggestionApplicationResult(
            operation=operation,
            production_id=PRODUCTION_ID,
            session_id=SESSION_ID,
            workspace_snapshot=FakeWorkspaceSnapshot(),
            suggestion_snapshot=AISuggestionLifecycleSnapshot(
                production_id=PRODUCTION_ID,
                lifecycle_revision=2,
                read_model=AISuggestionReadModel(
                    production_id=PRODUCTION_ID,
                    timeline_revision=4,
                ),
            ),
            timeline_command_result=(
                FakeCommandResult() if command else None
            ),
        )

    def get_ai_suggestions(self, production_id, *, session_id):
        self.calls.append(
            {"operation": "get", "production_id": production_id, "session_id": session_id}
        )
        return self._result(ReviewAISuggestionOperation.GET)

    def select_ai_suggestion(self, production_id, **kwargs):
        self.calls.append({"operation": "select", "production_id": production_id, **kwargs})
        return self._result(ReviewAISuggestionOperation.SELECT)

    def apply_ai_suggestion(self, production_id, **kwargs):
        self.calls.append({"operation": "apply", "production_id": production_id, **kwargs})
        if kwargs["suggestion_id"] == "revision-conflict":
            raise ReviewAISuggestionRevisionConflictError(
                "conflict",
                production_id=production_id,
                session_id=kwargs["session_id"],
                expected_revision=1,
                current_revision=2,
            )
        return self._result(ReviewAISuggestionOperation.APPLY, command=True)

    def dismiss_ai_suggestion(self, production_id, **kwargs):
        self.calls.append({"operation": "dismiss", "production_id": production_id, **kwargs})
        return self._result(ReviewAISuggestionOperation.DISMISS)

    def regenerate_ai_suggestions(self, production_id, **kwargs):
        self.calls.append({"operation": "regenerate", "production_id": production_id, **kwargs})
        return self._result(ReviewAISuggestionOperation.REGENERATE)


def main() -> None:
    fake = FakeSuggestionService()
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[
        get_review_ai_suggestion_application_service
    ] = lambda: fake
    client = TestClient(app)

    get_response = client.get(
        f"{BASE_PATH}/suggestions",
        params={"session_id": SESSION_ID},
    )
    select_response = client.post(
        f"{BASE_PATH}/suggestions/select",
        json={
            "session_id": SESSION_ID,
            "suggestion_id": "suggestion_1",
            "expected_lifecycle_revision": 1,
        },
    )
    apply_response = client.post(
        f"{BASE_PATH}/suggestions/apply",
        json={
            "session_id": SESSION_ID,
            "suggestion_id": "suggestion_1",
            "expected_timeline_revision": 4,
            "expected_lifecycle_revision": 1,
        },
    )
    dismiss_response = client.post(
        f"{BASE_PATH}/suggestions/dismiss",
        json={
            "session_id": SESSION_ID,
            "suggestion_id": "suggestion_1",
        },
    )
    regenerate_response = client.post(
        f"{BASE_PATH}/suggestions/regenerate",
        json={
            "session_id": SESSION_ID,
            "expected_lifecycle_revision": 2,
        },
    )
    before_invalid = len(fake.calls)
    invalid_response = client.post(
        f"{BASE_PATH}/suggestions/apply",
        json={"session_id": SESSION_ID, "suggestion_id": ""},
    )
    conflict_response = client.post(
        f"{BASE_PATH}/suggestions/apply",
        json={
            "session_id": SESSION_ID,
            "suggestion_id": "revision-conflict",
        },
    )

    schema = app.openapi()
    expected_paths = {
        f"/api/v1/productions/{{production_id}}/review/suggestions",
        f"/api/v1/productions/{{production_id}}/review/suggestions/select",
        f"/api/v1/productions/{{production_id}}/review/suggestions/apply",
        f"/api/v1/productions/{{production_id}}/review/suggestions/dismiss",
        f"/api/v1/productions/{{production_id}}/review/suggestions/regenerate",
    }
    router_source = Path(
        "app/review/api/router.py"
    ).read_text(encoding="utf-8")

    checks = {
        "all_routes_work": all(
            response.status_code == 200
            for response in (
                get_response,
                select_response,
                apply_response,
                dismiss_response,
                regenerate_response,
            )
        ),
        "all_operations_delegated": [
            item["operation"] for item in fake.calls[:5]
        ] == ["get", "select", "apply", "dismiss", "regenerate"],
        "select_payload_forwarded": (
            fake.calls[1]["suggestion_id"] == "suggestion_1"
            and fake.calls[1]["expected_lifecycle_revision"] == 1
        ),
        "apply_revisions_forwarded": (
            fake.calls[2]["expected_timeline_revision"] == 4
            and fake.calls[2]["expected_lifecycle_revision"] == 1
        ),
        "apply_result_mapped": (
            apply_response.json()["timeline_command_result"]["operation"]
            == "move_clip"
        ),
        "validation_blocked_before_service": (
            invalid_response.status_code == 422
            and len(fake.calls) == before_invalid + 1
        ),
        "revision_conflict_mapped": (
            conflict_response.status_code == 409
            and conflict_response.json()["error"]["code"]
            == "review_ai_suggestion_revision_conflict"
        ),
        "openapi_routes_complete": expected_paths.issubset(schema["paths"]),
        "response_contract_valid": all(
            response.json()["contract_version"] == "16.6.4"
            for response in (
                get_response,
                select_response,
                apply_response,
                dismiss_response,
                regenerate_response,
            )
        ),
        "controller_has_no_runtime_access": (
            ".graph" not in router_source
            and "suggestion_runtime" not in router_source
            and "timeline_store" not in router_source
        ),
        "route_count_valid": len(router.routes) == 27,
    }
    assert all(checks.values()), checks

    output = Path(
        "storage/demo_outputs/review_ai_suggestion_api_controller.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {"checks": checks, "calls": fake.calls},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print("=== AI Suggestion API Mapper & Controller ===")
    for name, value in checks.items():
        print(f"{name}: {value}")
    print(f"output: {output}")
    print("\nDONE: AI suggestion API controller test completed.")


if __name__ == "__main__":
    main()
