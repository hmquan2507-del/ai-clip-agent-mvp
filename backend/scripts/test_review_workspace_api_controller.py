from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.product import (
    build_in_memory_product_workspace_service,
)
from app.product.api.dependencies import (
    get_product_workspace_service,
)
from app.review.api.dependencies import (
    get_review_runtime_session_registry,
)
from app.review.api.router import (
    router as review_workspace_router,
)
from test_review_workspace_application_service import (
    register_workspace,
)


PRODUCTION_ID = (
    "221e4b01-5fb9-4b4a-a549-4fb32c455059"
)

MISSING_ID = (
    "11111111-1111-1111-1111-111111111111"
)

BASE_PATH = (
    f"/api/v1/productions/"
    f"{PRODUCTION_ID}/review"
)


app = FastAPI()

app.include_router(
    review_workspace_router,
    prefix="/api/v1",
)


def main() -> None:
    product_service, loader = (
        build_in_memory_product_workspace_service(
            ttl_seconds=60,
        )
    )

    register_workspace(
        loader,
        PRODUCTION_ID,
    )

    registry = (
        get_review_runtime_session_registry()
    )

    registry.clear(
        close_sessions=True
    )

    app.dependency_overrides[
        get_product_workspace_service
    ] = lambda: product_service

    try:
        with TestClient(app) as client:
            open_response = client.post(
                f"{BASE_PATH}/session",
                json={},
            )

            open_payload = (
                open_response.json()
            )

            session_id = (
                open_payload.get(
                    "session_id"
                )
            )

            open_works = (
                open_response.status_code
                == 200
                and open_payload["success"]
                and (
                    open_payload["operation"]
                    == "open_session"
                )
                and (
                    open_payload[
                        "production_id"
                    ]
                    == PRODUCTION_ID
                )
                and bool(session_id)
            )

            repeated_response = (
                client.post(
                    f"{BASE_PATH}/session",
                    json={},
                )
            )

            repeated_open_reuses_session = (
                repeated_response.status_code
                == 200
                and (
                    repeated_response.json()[
                        "session_id"
                    ]
                    == session_id
                )
                and registry.count == 1
            )

            get_response = client.get(
                f"{BASE_PATH}/session",
                params={
                    "session_id": session_id
                },
            )

            get_session_works = (
                get_response.status_code
                == 200
                and (
                    get_response.json()[
                        "operation"
                    ]
                    == "get_session"
                )
                and (
                    get_response.json()[
                        "session_id"
                    ]
                    == session_id
                )
            )

            snapshot_response = client.get(
                f"{BASE_PATH}/snapshot",
                params={
                    "session_id": session_id
                },
            )

            snapshot_works = (
                snapshot_response.status_code
                == 200
                and (
                    snapshot_response.json()[
                        "operation"
                    ]
                    == "get_snapshot"
                )
                and (
                    snapshot_response.json()[
                        "snapshot"
                    ]["consistency"][
                        "production_ids_match"
                    ]
                )
            )

            active_session = registry.get(
                PRODUCTION_ID,
                session_id=session_id,
            )

            edit_result = (
                active_session
                .graph
                .history_runtime
                .trim_clip_end(
                    "clip_1",
                    3.5,
                )
            )

            reset_response = client.post(
                f"{BASE_PATH}/reset",
                json={
                    "session_id": session_id
                },
            )

            reset_works = (
                edit_result.success
                and (
                    reset_response.status_code
                    == 200
                )
                and (
                    reset_response.json()[
                        "operation"
                    ]
                    == "reset_session"
                )
                and not (
                    reset_response.json()[
                        "snapshot"
                    ]["timeline"]["dirty"]
                )
            )

            wrong_session_response = (
                client.get(
                    f"{BASE_PATH}/snapshot",
                    params={
                        "session_id": (
                            "wrong-session"
                        )
                    },
                )
            )

            error_contract_works = (
                (
                    wrong_session_response
                    .status_code
                    == 404
                )
                and not (
                    wrong_session_response
                    .json()["success"]
                )
                and (
                    wrong_session_response
                    .json()["error"]["code"]
                    == (
                        "review_session_"
                        "not_found"
                    )
                )
            )

            invalid_refresh_response = (
                client.post(
                    f"{BASE_PATH}/session",
                    json={
                        "force_refresh": True,
                        "replace_existing": (
                            False
                        ),
                    },
                )
            )

            request_validation_works = (
                invalid_refresh_response
                .status_code
                == 422
            )

            replace_response = client.post(
                f"{BASE_PATH}/session",
                json={
                    "force_refresh": True,
                    "replace_existing": True,
                },
            )

            replacement_id = (
                replace_response
                .json()
                .get("session_id")
            )

            replace_works = (
                replace_response.status_code
                == 200
                and (
                    replacement_id
                    != session_id
                )
                and active_session.closed
                and registry.count == 1
            )

            close_response = (
                client.request(
                    "DELETE",
                    f"{BASE_PATH}/session",
                    json={
                        "session_id": (
                            replacement_id
                        )
                    },
                )
            )

            close_works = (
                close_response.status_code
                == 200
                and (
                    close_response.json()[
                        "operation"
                    ]
                    == "close_session"
                )
                and (
                    close_response.json()[
                        "state"
                    ]["closed"]
                )
                and registry.count == 0
            )

            closed_lookup_response = (
                client.get(
                    f"{BASE_PATH}/session",
                    params={
                        "session_id": (
                            replacement_id
                        )
                    },
                )
            )

            closed_lookup_blocked = (
                (
                    closed_lookup_response
                    .status_code
                    == 404
                )
                and (
                    closed_lookup_response
                    .json()["error"]["code"]
                    == (
                        "review_session_"
                        "not_found"
                    )
                )
            )

            missing_response = client.post(
                (
                    f"/api/v1/productions/"
                    f"{MISSING_ID}/review/"
                    "session"
                ),
                json={},
            )

            missing_production_mapped = (
                missing_response.status_code
                == 404
                and (
                    missing_response.json()[
                        "error"
                    ]["code"]
                    == "production_not_found"
                )
            )

            invalid_uuid_response = (
                client.post(
                    (
                        "/api/v1/productions/"
                        "not-a-uuid/review/"
                        "session"
                    ),
                    json={},
                )
            )

            path_validation_works = (
                invalid_uuid_response
                .status_code
                == 422
            )

            singleton_registry = (
                get_review_runtime_session_registry()
                is registry
            )

            checks = {
                "open_works": open_works,
                "repeated_open_reuses_session": (
                    repeated_open_reuses_session
                ),
                "get_session_works": (
                    get_session_works
                ),
                "snapshot_works": (
                    snapshot_works
                ),
                "reset_works": reset_works,
                "error_contract_works": (
                    error_contract_works
                ),
                "request_validation_works": (
                    request_validation_works
                ),
                "replace_works": replace_works,
                "close_works": close_works,
                "closed_lookup_blocked": (
                    closed_lookup_blocked
                ),
                "missing_production_mapped": (
                    missing_production_mapped
                ),
                "path_validation_works": (
                    path_validation_works
                ),
                "singleton_registry": (
                    singleton_registry
                ),
            }

            payload = {
                "checks": checks,
                "open": open_payload,
                "snapshot": (
                    snapshot_response.json()
                ),
                "reset": (
                    reset_response.json()
                ),
                "close": (
                    close_response.json()
                ),
                "missing": (
                    missing_response.json()
                ),
            }

            output_path = Path(
                "storage/demo_outputs/"
                "review_workspace_"
                "api_controller.json"
            )

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            output_path.write_text(
                json.dumps(
                    payload,
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            print(
                "=== Review Workspace "
                "API Controller ==="
            )

            for name, passed in (
                checks.items()
            ):
                print(
                    f"{name}: {passed}"
                )

            print(
                "output:",
                output_path,
            )

            assert all(
                checks.values()
            ), checks

            print(
                "\nDONE: Review workspace "
                "API controller test "
                "completed."
            )

    finally:
        registry.clear(
            close_sessions=True
        )

        app.dependency_overrides.clear()


if __name__ == "__main__":
    main()