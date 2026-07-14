from __future__ import annotations

import json
import sys
from copy import deepcopy
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


PRODUCTION_A = (
    "221e4b01-5fb9-4b4a-a549-4fb32c455059"
)

PRODUCTION_B = (
    "331e4b01-5fb9-4b4a-a549-4fb32c455059"
)

MISSING_PRODUCTION = (
    "11111111-1111-1111-1111-111111111111"
)


def review_path(
    production_id: str,
) -> str:
    return (
        f"/api/v1/productions/"
        f"{production_id}/review"
    )


def build_test_app() -> FastAPI:
    application = FastAPI()

    application.include_router(
        review_workspace_router,
        prefix="/api/v1",
    )

    return application


def main() -> None:
    product_service, loader = (
        build_in_memory_product_workspace_service(
            ttl_seconds=60,
        )
    )

    source_a = register_workspace(
        loader,
        PRODUCTION_A,
    )

    source_b = register_workspace(
        loader,
        PRODUCTION_B,
    )

    source_a_before = deepcopy(source_a)
    source_b_before = deepcopy(source_b)

    registry = (
        get_review_runtime_session_registry()
    )

    registry.clear(
        close_sessions=True
    )

    application = build_test_app()

    application.dependency_overrides[
        get_product_workspace_service
    ] = lambda: product_service

    try:
        with TestClient(
            application
        ) as client:
            openapi = client.get(
                "/openapi.json"
            ).json()

            expected_routes = {
                (
                    f"{review_path(
                        '{production_id}'
                    )}/session"
                ): {
                    "get",
                    "post",
                    "delete",
                },
                (
                    f"{review_path(
                        '{production_id}'
                    )}/snapshot"
                ): {
                    "get",
                },
                (
                    f"{review_path(
                        '{production_id}'
                    )}/reset"
                ): {
                    "post",
                },
            }

            openapi_routes_complete = all(
                (
                    path
                    in openapi["paths"]
                )
                and methods.issubset(
                    openapi["paths"][
                        path
                    ].keys()
                )
                for path, methods
                in expected_routes.items()
            )

            open_a = client.post(
                (
                    f"{review_path(
                        PRODUCTION_A
                    )}/session"
                ),
                json={},
            )

            open_b = client.post(
                (
                    f"{review_path(
                        PRODUCTION_B
                    )}/session"
                ),
                json={},
            )

            payload_a = open_a.json()
            payload_b = open_b.json()

            session_a_id = (
                payload_a["session_id"]
            )

            session_b_id = (
                payload_b["session_id"]
            )

            multi_production_open = (
                open_a.status_code == 200
                and open_b.status_code == 200
                and (
                    session_a_id
                    != session_b_id
                )
                and registry.count == 2
                and (
                    payload_a[
                        "contract_version"
                    ]
                    == "16.2.3"
                )
                and (
                    payload_b[
                        "contract_version"
                    ]
                    == "16.2.3"
                )
            )

            session_a = registry.get(
                PRODUCTION_A,
                session_id=session_a_id,
            )

            session_b = registry.get(
                PRODUCTION_B,
                session_id=session_b_id,
            )

            initial_b = (
                session_b.snapshot()
            )

            edit_a = (
                session_a
                .graph
                .history_runtime
                .trim_clip_end(
                    "clip_1",
                    3.5,
                )
            )

            copy_a = (
                session_a
                .graph
                .clipboard_runtime
                .copy_clip(
                    "clip_1"
                )
            )

            snapshot_a_response = (
                client.get(
                    (
                        f"{review_path(
                            PRODUCTION_A
                        )}/snapshot"
                    ),
                    params={
                        "session_id": (
                            session_a_id
                        )
                    },
                )
            )

            snapshot_b_response = (
                client.get(
                    (
                        f"{review_path(
                            PRODUCTION_B
                        )}/snapshot"
                    ),
                    params={
                        "session_id": (
                            session_b_id
                        )
                    },
                )
            )

            snapshot_a = (
                snapshot_a_response
                .json()["snapshot"]
            )

            snapshot_b = (
                snapshot_b_response
                .json()["snapshot"]
            )

            runtime_state_survives_requests = (
                edit_a.success
                and copy_a.success
                and (
                    snapshot_a[
                        "timeline"
                    ]["dirty"]
                )
                and (
                    snapshot_a[
                        "history"
                    ]["undo_count"]
                    == 1
                )
                and (
                    snapshot_a[
                        "clipboard"
                    ]["content"][
                        "item_count"
                    ]
                    == 1
                )
            )

            production_isolation = (
                not (
                    snapshot_b[
                        "timeline"
                    ]["dirty"]
                )
                and (
                    snapshot_b[
                        "timeline"
                    ]["revision"]
                    == (
                        initial_b
                        .timeline
                        .revision
                    )
                )
                and (
                    snapshot_b[
                        "history"
                    ]["undo_count"]
                    == 0
                )
                and (
                    snapshot_b[
                        "clipboard"
                    ]["content"][
                        "item_count"
                    ]
                    == 0
                )
            )

            registry_count_before_failures = (
                registry.count
            )

            a_revision_before_failures = (
                session_a
                .snapshot()
                .timeline
                .revision
            )

            b_revision_before_failures = (
                session_b
                .snapshot()
                .timeline
                .revision
            )

            mismatch_response = client.get(
                (
                    f"{review_path(
                        PRODUCTION_A
                    )}/snapshot"
                ),
                params={
                    "session_id": (
                        session_b_id
                    )
                },
            )

            missing_response = (
                client.post(
                    (
                        f"{review_path(
                            MISSING_PRODUCTION
                        )}/session"
                    ),
                    json={},
                )
            )

            invalid_request_response = (
                client.post(
                    (
                        f"{review_path(
                            PRODUCTION_A
                        )}/session"
                    ),
                    json={
                        "force_refresh": True,
                        "replace_existing": (
                            False
                        ),
                    },
                )
            )

            failures_are_read_only = (
                (
                    mismatch_response
                    .status_code
                    == 404
                )
                and (
                    mismatch_response
                    .json()["error"]["code"]
                    == (
                        "review_session_"
                        "not_found"
                    )
                )
                and (
                    missing_response
                    .status_code
                    == 404
                )
                and (
                    missing_response
                    .json()["error"]["code"]
                    == (
                        "production_not_found"
                    )
                )
                and (
                    invalid_request_response
                    .status_code
                    == 422
                )
                and (
                    registry.count
                    == (
                        registry_count_before_failures
                    )
                )
                and (
                    session_a
                    .snapshot()
                    .timeline
                    .revision
                    == (
                        a_revision_before_failures
                    )
                )
                and (
                    session_b
                    .snapshot()
                    .timeline
                    .revision
                    == (
                        b_revision_before_failures
                    )
                )
            )

            reset_a_response = client.post(
                (
                    f"{review_path(
                        PRODUCTION_A
                    )}/reset"
                ),
                json={
                    "session_id": (
                        session_a_id
                    )
                },
            )

            reset_a = (
                reset_a_response
                .json()["snapshot"]
            )

            b_after_reset = (
                session_b.snapshot()
            )

            reset_isolated = (
                (
                    reset_a_response
                    .status_code
                    == 200
                )
                and not (
                    reset_a[
                        "timeline"
                    ]["dirty"]
                )
                and (
                    reset_a[
                        "history"
                    ]["undo_count"]
                    == 0
                )
                and (
                    reset_a[
                        "clipboard"
                    ]["content"][
                        "item_count"
                    ]
                    == 0
                )
                and (
                    b_after_reset
                    .timeline
                    .revision
                    == (
                        initial_b
                        .timeline
                        .revision
                    )
                )
                and not (
                    b_after_reset
                    .timeline
                    .dirty
                )
            )

            replace_a_response = (
                client.post(
                    (
                        f"{review_path(
                            PRODUCTION_A
                        )}/session"
                    ),
                    json={
                        "force_refresh": True,
                        "replace_existing": (
                            True
                        ),
                    },
                )
            )

            replacement_a_id = (
                replace_a_response
                .json()["session_id"]
            )

            replace_isolated = (
                (
                    replace_a_response
                    .status_code
                    == 200
                )
                and (
                    replacement_a_id
                    != session_a_id
                )
                and session_a.closed
                and not session_b.closed
                and registry.count == 2
                and (
                    registry.get(
                        PRODUCTION_B,
                        session_id=(
                            session_b_id
                        ),
                    )
                    is session_b
                )
            )

            close_a_response = (
                client.request(
                    "DELETE",
                    (
                        f"{review_path(
                            PRODUCTION_A
                        )}/session"
                    ),
                    json={
                        "session_id": (
                            replacement_a_id
                        )
                    },
                )
            )

            close_a_isolated = (
                (
                    close_a_response
                    .status_code
                    == 200
                )
                and (
                    close_a_response
                    .json()["state"][
                        "closed"
                    ]
                )
                and registry.count == 1
                and (
                    registry.get(
                        PRODUCTION_A
                    )
                    is None
                )
                and (
                    registry.get(
                        PRODUCTION_B,
                        session_id=(
                            session_b_id
                        ),
                    )
                    is session_b
                )
                and not session_b.closed
            )

            reopen_a_response = (
                client.post(
                    (
                        f"{review_path(
                            PRODUCTION_A
                        )}/session"
                    ),
                    json={},
                )
            )

            reopened_a_id = (
                reopen_a_response
                .json()["session_id"]
            )

            reopen_after_close = (
                (
                    reopen_a_response
                    .status_code
                    == 200
                )
                and (
                    reopened_a_id
                    not in {
                        session_a_id,
                        replacement_a_id,
                    }
                )
                and registry.count == 2
            )

            close_reopened_a = (
                client.request(
                    "DELETE",
                    (
                        f"{review_path(
                            PRODUCTION_A
                        )}/session"
                    ),
                    json={
                        "session_id": (
                            reopened_a_id
                        )
                    },
                )
            )

            close_b = client.request(
                "DELETE",
                (
                    f"{review_path(
                        PRODUCTION_B
                    )}/session"
                ),
                json={
                    "session_id": (
                        session_b_id
                    )
                },
            )

            lifecycle_cleanup_complete = (
                (
                    close_reopened_a
                    .status_code
                    == 200
                )
                and (
                    close_b.status_code
                    == 200
                )
                and registry.count == 0
                and session_b.closed
            )

            response_payload_isolated = True

            payload_a[
                "snapshot"
            ]["metadata"][
                "client_mutation"
            ] = True

            if (
                "client_mutation"
                in (
                    session_a
                    .snapshot()
                    .metadata
                )
            ):
                response_payload_isolated = (
                    False
                )

            source_unchanged = (
                source_a == source_a_before
                and source_b
                == source_b_before
            )

            checks = {
                "openapi_routes_complete": (
                    openapi_routes_complete
                ),
                "multi_production_open": (
                    multi_production_open
                ),
                "runtime_state_survives_requests": (
                    runtime_state_survives_requests
                ),
                "production_isolation": (
                    production_isolation
                ),
                "failures_are_read_only": (
                    failures_are_read_only
                ),
                "reset_isolated": (
                    reset_isolated
                ),
                "replace_isolated": (
                    replace_isolated
                ),
                "close_a_isolated": (
                    close_a_isolated
                ),
                "reopen_after_close": (
                    reopen_after_close
                ),
                "lifecycle_cleanup_complete": (
                    lifecycle_cleanup_complete
                ),
                "response_payload_isolated": (
                    response_payload_isolated
                ),
                "source_unchanged": (
                    source_unchanged
                ),
            }

            output_path = Path(
                "storage/demo_outputs/"
                "review_workspace_"
                "api_integration.json"
            )

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            output_path.write_text(
                json.dumps(
                    {
                        "checks": checks,
                        "open_a": payload_a,
                        "open_b": payload_b,
                        "snapshot_a": (
                            snapshot_a
                        ),
                        "snapshot_b": (
                            snapshot_b
                        ),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            print(
                "=== Review Workspace "
                "API Integration ==="
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
                "API integration test "
                "completed."
            )

    finally:
        registry.clear(
            close_sessions=True
        )

        application.dependency_overrides.clear()


if __name__ == "__main__":
    main()