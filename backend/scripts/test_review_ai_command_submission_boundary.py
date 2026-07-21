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
    get_review_ai_command_submission_service,
)
from app.review.api.router import router
from app.review.commands import (
    AI_COMMAND_SUBMISSION_CONTRACT_VERSION,
    AICommandSubmissionService,
    AICommandSubmissionStore,
)
from app.review.suggestions import (
    AISuggestionReadModel,
    build_ai_suggestion_lifecycle_runtime,
)
from test_review_ai_suggestion_application_service import (
    FakeSession,
    FakeWorkspaceService,
    PRODUCTION_ID,
    SESSION_ID,
)


BASE_PATH = (
    f"/api/v1/productions/{PRODUCTION_ID}/review"
)


def main() -> None:
    read_model = AISuggestionReadModel(
        production_id=PRODUCTION_ID,
        timeline_revision=1,
    )
    session = FakeSession(
        build_ai_suggestion_lifecycle_runtime(read_model)
    )
    workspace_service = FakeWorkspaceService(session)
    store = AICommandSubmissionStore(maximum_size=10)
    service = AICommandSubmissionService(
        workspace_service=workspace_service,
        store=store,
    )

    timeline_before = deepcopy(
        session.graph.timeline_store.snapshot().to_dict()
    )

    application = FastAPI()
    application.include_router(router, prefix="/api/v1")
    application.dependency_overrides[
        get_review_ai_command_submission_service
    ] = lambda: service

    with TestClient(application) as client:
        response = client.post(
            f"{BASE_PATH}/commands/submit",
            json={
                "session_id": SESSION_ID,
                "command_text": (
                    "  Làm hook mạnh hơn,   thêm B-roll  "
                ),
                "expected_timeline_revision": 1,
                "client_request_id": "command-request-1",
            },
        )
        payload = response.json()

        duplicate_response = client.post(
            f"{BASE_PATH}/commands/submit",
            json={
                "session_id": SESSION_ID,
                "command_text": "Nội dung bị bỏ qua do idempotency",
                "expected_timeline_revision": 1,
                "client_request_id": "command-request-1",
            },
        )
        duplicate_payload = duplicate_response.json()

        before_conflict_count = store.count
        conflict_response = client.post(
            f"{BASE_PATH}/commands/submit",
            json={
                "session_id": SESSION_ID,
                "command_text": "Thêm nhạc nhanh hơn",
                "expected_timeline_revision": 99,
            },
        )

        invalid_response = client.post(
            f"{BASE_PATH}/commands/submit",
            json={
                "session_id": SESSION_ID,
                "command_text": "",
            },
        )

        openapi = client.get("/openapi.json").json()

    timeline_after = (
        session.graph.timeline_store.snapshot().to_dict()
    )
    isolated = deepcopy(payload)
    isolated["submission"]["metadata"]["mutated"] = True

    checks = {
        "contract_version_valid": (
            payload["contract_version"]
            == AI_COMMAND_SUBMISSION_CONTRACT_VERSION
            == "16.6.8"
        ),
        "submission_accepted": (
            response.status_code == 200
            and payload["operation"] == "submit_command"
            and payload["submission"]["status"] == "accepted"
        ),
        "command_normalized": (
            payload["submission"]["command_text"]
            == "Làm hook mạnh hơn, thêm B-roll"
        ),
        "revision_captured": (
            payload["timeline_revision"] == 1
            and payload["submission"]["timeline_revision"] == 1
        ),
        "idempotency_valid": (
            duplicate_response.status_code == 200
            and duplicate_payload["duplicate"] is True
            and duplicate_payload["submission"]["submission_id"]
            == payload["submission"]["submission_id"]
            and store.count == 1
        ),
        "revision_conflict_read_only": (
            conflict_response.status_code == 409
            and conflict_response.json()["error"]["code"]
            == "review_ai_command_revision_conflict"
            and store.count == before_conflict_count
        ),
        "validation_read_only": (
            invalid_response.status_code == 422
            and store.count == 1
        ),
        "timeline_unchanged": (
            timeline_before == timeline_after
            and payload["timeline_mutated"] is False
            and workspace_service.command_count == 0
            and workspace_service.history_count == 0
        ),
        "execution_not_authorized": (
            payload["submission"]["metadata"][
                "execution_authorized"
            ]
            is False
            and payload["submission"]["metadata"][
                "proposal_created"
            ]
            is False
        ),
        "response_isolated": (
            "mutated"
            not in payload["submission"]["metadata"]
        ),
        "openapi_route_present": (
            "/api/v1/productions/{production_id}/review/commands/submit"
            in openapi["paths"]
        ),
        "serialization_valid": bool(json.dumps(payload)),
    }
    assert all(checks.values()), checks

    output = Path(
        "storage/demo_outputs/"
        "review_ai_command_submission_boundary.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {"checks": checks, "response": payload},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=== Natural-language Command Submission Boundary ===")
    for name, value in checks.items():
        print(f"{name}: {value}")
    print(f"output: {output}")
    print(
        "\nDONE: Natural-language command submission "
        "boundary test completed."
    )


if __name__ == "__main__":
    main()
