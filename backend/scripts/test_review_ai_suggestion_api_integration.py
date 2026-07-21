from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

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
    build_review_ai_suggestion_application_service,
)
from app.review.suggestions import (
    AISuggestionReadModel,
    build_ai_suggestion_lifecycle_runtime,
)
from test_review_ai_suggestion_application_service import (
    FakeRegenerator,
    FakeSession,
    FakeWorkspaceService,
    PRODUCTION_ID,
    SESSION_ID,
    make_suggestion,
)


BASE_PATH = (
    f"/api/v1/productions/{PRODUCTION_ID}/review"
)


def main() -> None:
    source_model = AISuggestionReadModel(
        production_id=PRODUCTION_ID,
        timeline_revision=1,
        suggestions=(
            make_suggestion(
                "suggestion_move",
                1,
                operation="move_clip",
            ),
            make_suggestion(
                "suggestion_dismiss",
                1,
                operation="move_clip",
            ),
        ),
    )
    source_before = deepcopy(source_model.to_dict())

    suggestion_runtime = (
        build_ai_suggestion_lifecycle_runtime(
            source_model
        )
    )
    session = FakeSession(suggestion_runtime)
    workspace_service = FakeWorkspaceService(session)
    service = (
        build_review_ai_suggestion_application_service(
            workspace_service=workspace_service,
            regenerator=FakeRegenerator(),
        )
    )

    application = FastAPI()
    application.include_router(
        router,
        prefix="/api/v1",
    )
    application.dependency_overrides[
        get_review_ai_suggestion_application_service
    ] = lambda: service

    with TestClient(application) as client:
        openapi = client.get("/openapi.json").json()
        expected_routes = {
            f"{BASE_PATH}/suggestions": {"get"},
            f"{BASE_PATH}/suggestions/select": {"post"},
            f"{BASE_PATH}/suggestions/apply": {"post"},
            f"{BASE_PATH}/suggestions/dismiss": {"post"},
            f"{BASE_PATH}/suggestions/regenerate": {"post"},
        }
        openapi_routes_complete = all(
            path in openapi["paths"]
            and methods.issubset(
                openapi["paths"][path].keys()
            )
            for path, methods in expected_routes.items()
        )

        initial_response = client.get(
            f"{BASE_PATH}/suggestions",
            params={"session_id": SESSION_ID},
        )
        initial = initial_response.json()

        select_response = client.post(
            f"{BASE_PATH}/suggestions/select",
            json={
                "session_id": SESSION_ID,
                "suggestion_id": "suggestion_move",
                "expected_lifecycle_revision": 1,
            },
        )
        selected = select_response.json()

        timeline_before_dismiss = (
            session.graph.timeline_store.snapshot().to_dict()
        )
        dismiss_response = client.post(
            f"{BASE_PATH}/suggestions/dismiss",
            json={
                "session_id": SESSION_ID,
                "suggestion_id": "suggestion_dismiss",
                "expected_lifecycle_revision": 2,
            },
        )
        dismissed = dismiss_response.json()
        timeline_after_dismiss = (
            session.graph.timeline_store.snapshot().to_dict()
        )

        lifecycle_before_conflict = (
            suggestion_runtime.snapshot().to_dict()
        )
        timeline_before_conflict = (
            session.graph.timeline_store.snapshot().to_dict()
        )
        conflict_response = client.post(
            f"{BASE_PATH}/suggestions/apply",
            json={
                "session_id": SESSION_ID,
                "suggestion_id": "suggestion_move",
                "expected_timeline_revision": 99,
                "expected_lifecycle_revision": 3,
            },
        )
        lifecycle_after_conflict = (
            suggestion_runtime.snapshot().to_dict()
        )
        timeline_after_conflict = (
            session.graph.timeline_store.snapshot().to_dict()
        )

        apply_response = client.post(
            f"{BASE_PATH}/suggestions/apply",
            json={
                "session_id": SESSION_ID,
                "suggestion_id": "suggestion_move",
                "expected_timeline_revision": 1,
                "expected_lifecycle_revision": 3,
            },
        )
        applied = apply_response.json()

        timeline_before_regenerate = (
            session.graph.timeline_store.snapshot().to_dict()
        )
        regenerate_response = client.post(
            f"{BASE_PATH}/suggestions/regenerate",
            json={
                "session_id": SESSION_ID,
                "expected_lifecycle_revision": 4,
            },
        )
        regenerated = regenerate_response.json()
        timeline_after_regenerate = (
            session.graph.timeline_store.snapshot().to_dict()
        )

        isolated_payload = deepcopy(regenerated)
        isolated_payload["suggestion_snapshot"][
            "metadata"
        ]["mutated"] = True
        final_response = client.get(
            f"{BASE_PATH}/suggestions",
            params={"session_id": SESSION_ID},
        )
        final_payload = final_response.json()

        before_invalid_session = (
            suggestion_runtime.snapshot().to_dict()
        )
        invalid_session_response = client.get(
            f"{BASE_PATH}/suggestions",
            params={"session_id": ""},
        )
        after_invalid_session = (
            suggestion_runtime.snapshot().to_dict()
        )

    checks = {
        "openapi_routes_complete": openapi_routes_complete,
        "initial_read_valid": (
            initial_response.status_code == 200
            and initial["contract_version"] == "16.6.4"
            and initial["suggestion_snapshot"][
                "lifecycle_revision"
            ] == 1
            and initial["suggestion_snapshot"][
                "read_model"
            ]["count"] == 2
        ),
        "selection_authoritative": (
            select_response.status_code == 200
            and selected["suggestion_snapshot"][
                "read_model"
            ]["selected_suggestion_id"]
            == "suggestion_move"
            and selected["suggestion_snapshot"][
                "lifecycle_revision"
            ] == 2
        ),
        "dismiss_read_only": (
            dismiss_response.status_code == 200
            and timeline_before_dismiss
            == timeline_after_dismiss
            and dismissed["suggestion_snapshot"][
                "lifecycle_revision"
            ] == 3
        ),
        "conflict_is_atomic": (
            conflict_response.status_code == 409
            and conflict_response.json()["error"]["code"]
            == "review_ai_suggestion_revision_conflict"
            and timeline_before_conflict
            == timeline_after_conflict
            and lifecycle_before_conflict
            == lifecycle_after_conflict
        ),
        "apply_history_backed_once": (
            apply_response.status_code == 200
            and workspace_service.command_count == 1
            and workspace_service.history_count == 1
            and applied["workspace_snapshot"][
                "timeline"
            ]["revision"] == 2
            and applied["suggestion_snapshot"][
                "lifecycle_revision"
            ] == 4
            and applied["timeline_command_result"][
                "operation"
            ] == "move_clip"
        ),
        "regenerate_read_only": (
            regenerate_response.status_code == 200
            and timeline_before_regenerate
            == timeline_after_regenerate
            and regenerated["suggestion_snapshot"][
                "timeline_revision"
            ] == 2
            and regenerated["suggestion_snapshot"][
                "lifecycle_revision"
            ] == 5
        ),
        "response_payload_isolated": (
            "mutated"
            not in final_payload["suggestion_snapshot"][
                "metadata"
            ]
        ),
        "invalid_session_read_only": (
            invalid_session_response.status_code == 422
            and before_invalid_session == after_invalid_session
        ),
        "source_unchanged": (
            source_model.to_dict() == source_before
        ),
        "serialization_valid": bool(
            json.dumps(final_payload)
        ),
        "lifecycle_cleanup_complete": (
            final_payload["suggestion_snapshot"][
                "read_model"
            ]["count"] == 1
        ),
    }
    assert all(checks.values()), checks

    output = Path(
        "storage/demo_outputs/"
        "review_ai_suggestion_api_integration.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "checks": checks,
                "final": final_payload,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=== AI Suggestion API Integration & Regression ===")
    for name, value in checks.items():
        print(f"{name}: {value}")
    print(f"output: {output}")
    print(
        "\nDONE: AI suggestion API integration "
        "and regression test completed."
    )


if __name__ == "__main__":
    main()
