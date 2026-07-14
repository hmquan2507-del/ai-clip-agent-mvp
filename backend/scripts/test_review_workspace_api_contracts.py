from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import ValidationError

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.product import (
    ProductWorkspaceNotFoundError,
    build_in_memory_product_workspace_service,
)
from app.review import (
    REVIEW_WORKSPACE_API_CONTRACT_VERSION,
    CloseReviewWorkspaceRequest,
    OpenReviewWorkspaceRequest,
    ResetReviewWorkspaceRequest,
    ReviewRuntimeSessionConflictError,
    ReviewWorkspaceAPIErrorCode,
    ReviewWorkspaceAPIMapper,
    ReviewWorkspaceAPIOperation,
    ReviewWorkspaceSessionQuery,
    build_review_workspace_application_service,
)
from test_review_workspace_application_service import (
    register_workspace,
)


PRODUCTION_ID = "review-api-contracts-1"


def validation_fails(
    factory,
) -> bool:
    try:
        factory()
    except ValidationError:
        return True

    return False


def main() -> None:
    open_request = (
        OpenReviewWorkspaceRequest()
    )

    replace_request = (
        OpenReviewWorkspaceRequest(
            force_refresh=True,
            replace_existing=True,
        )
    )

    query = ReviewWorkspaceSessionQuery(
        session_id="  session-1  "
    )

    reset_request = (
        ResetReviewWorkspaceRequest(
            session_id="session-1"
        )
    )

    close_request = (
        CloseReviewWorkspaceRequest(
            session_id="session-1"
        )
    )

    defaults_valid = (
        not open_request.force_refresh
        and not open_request.replace_existing
    )

    replace_policy_valid = (
        replace_request.force_refresh
        and replace_request.replace_existing
    )

    invalid_refresh_blocked = (
        validation_fails(
            lambda: (
                OpenReviewWorkspaceRequest(
                    force_refresh=True,
                    replace_existing=False,
                )
            )
        )
    )

    extra_fields_blocked = (
        validation_fails(
            lambda: (
                OpenReviewWorkspaceRequest(
                    unexpected=True
                )
            )
        )
    )

    session_ids_valid = (
        query.session_id == "session-1"
        and reset_request.session_id
        == "session-1"
        and close_request.session_id
        == "session-1"
    )

    product_service, loader = (
        build_in_memory_product_workspace_service(
            ttl_seconds=60,
        )
    )

    register_workspace(
        loader,
        PRODUCTION_ID,
    )

    application_service = (
        build_review_workspace_application_service(
            product_workspace_service=(
                product_service
            ),
        )
    )

    session = (
        application_service.open_session(
            PRODUCTION_ID
        )
    )

    session_response = (
        ReviewWorkspaceAPIMapper
        .session_response(
            session,
            metadata={
                "reused": False
            },
        )
    )

    snapshot = (
        application_service.get_snapshot(
            PRODUCTION_ID,
            session_id=session.session_id,
        )
    )

    snapshot_response = (
        ReviewWorkspaceAPIMapper
        .snapshot_response(snapshot)
    )

    session_response_valid = (
        session_response.success
        and (
            session_response.operation
            == (
                ReviewWorkspaceAPIOperation
                .OPEN_SESSION
            )
        )
        and (
            session_response.production_id
            == PRODUCTION_ID
        )
        and (
            session_response.session_id
            == session.session_id
        )
        and (
            session_response.snapshot[
                "consistency"
            ]["production_ids_match"]
        )
    )

    snapshot_response_valid = (
        snapshot_response.success
        and (
            snapshot_response.operation
            == (
                ReviewWorkspaceAPIOperation
                .GET_SNAPSHOT
            )
        )
        and (
            snapshot_response.snapshot[
                "session"
            ]["session_id"]
            == session.session_id
        )
    )

    session_response.snapshot[
        "metadata"
    ]["mutated"] = True

    response_isolated = (
        "mutated"
        not in session.snapshot().metadata
    )

    edit_result = (
        session.graph.history_runtime
        .trim_clip_end(
            "clip_1",
            3.5,
        )
    )

    reset_snapshot = (
        application_service.reset_session(
            PRODUCTION_ID,
            session_id=session.session_id,
        )
    )

    reset_response = (
        ReviewWorkspaceAPIMapper
        .reset_response(reset_snapshot)
    )

    reset_response_valid = (
        edit_result.success
        and (
            reset_response.operation
            == (
                ReviewWorkspaceAPIOperation
                .RESET_SESSION
            )
        )
        and not (
            reset_response.snapshot[
                "timeline"
            ]["dirty"]
        )
    )

    conflict_error = (
        ReviewRuntimeSessionConflictError(
            "Active session conflict.",
            production_id=PRODUCTION_ID,
            session_id=session.session_id,
        )
    )

    conflict_response = (
        ReviewWorkspaceAPIMapper
        .error_response(
            conflict_error
        )
    )

    not_found_response = (
        ReviewWorkspaceAPIMapper
        .error_response(
            ProductWorkspaceNotFoundError(
                "Missing production."
            ),
            production_id=(
                "missing-production"
            ),
        )
    )

    validation_response = (
        ReviewWorkspaceAPIMapper
        .error_response(
            ValueError(
                "Invalid request."
            ),
            production_id=PRODUCTION_ID,
        )
    )

    error_mapping_valid = (
        not conflict_response.success
        and (
            conflict_response.error.code
            == (
                ReviewWorkspaceAPIErrorCode
                .SESSION_CONFLICT
            )
        )
        and (
            conflict_response.error.session_id
            == session.session_id
        )
        and (
            not_found_response.error.code
            == (
                ReviewWorkspaceAPIErrorCode
                .PRODUCTION_NOT_FOUND
            )
        )
        and (
            validation_response.error.code
            == (
                ReviewWorkspaceAPIErrorCode
                .VALIDATION_ERROR
            )
        )
    )

    close_result = (
        application_service.close_session(
            PRODUCTION_ID,
            session_id=session.session_id,
        )
    )

    close_response = (
        ReviewWorkspaceAPIMapper
        .close_response(close_result)
    )

    close_response_valid = (
        close_response.success
        and (
            close_response.operation
            == (
                ReviewWorkspaceAPIOperation
                .CLOSE_SESSION
            )
        )
        and close_response.state["closed"]
        and close_response.event is not None
    )

    serialized = {
        "session": (
            session_response.model_dump(
                mode="json"
            )
        ),
        "snapshot": (
            snapshot_response.model_dump(
                mode="json"
            )
        ),
        "reset": (
            reset_response.model_dump(
                mode="json"
            )
        ),
        "close": (
            close_response.model_dump(
                mode="json"
            )
        ),
        "conflict": (
            conflict_response.model_dump(
                mode="json"
            )
        ),
    }

    serialization_valid = (
        json.loads(
            json.dumps(
                serialized,
                ensure_ascii=False,
            )
        )["session"]["contract_version"]
        == (
            REVIEW_WORKSPACE_API_CONTRACT_VERSION
        )
    )

    checks = {
        "defaults_valid": defaults_valid,
        "replace_policy_valid": (
            replace_policy_valid
        ),
        "invalid_refresh_blocked": (
            invalid_refresh_blocked
        ),
        "extra_fields_blocked": (
            extra_fields_blocked
        ),
        "session_ids_valid": (
            session_ids_valid
        ),
        "session_response_valid": (
            session_response_valid
        ),
        "snapshot_response_valid": (
            snapshot_response_valid
        ),
        "response_isolated": (
            response_isolated
        ),
        "reset_response_valid": (
            reset_response_valid
        ),
        "error_mapping_valid": (
            error_mapping_valid
        ),
        "close_response_valid": (
            close_response_valid
        ),
        "serialization_valid": (
            serialization_valid
        ),
    }

    output_path = Path(
        "storage/demo_outputs/"
        "review_workspace_api_contracts.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            {
                "checks": checks,
                "payloads": serialized,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "=== Review Workspace API "
        "Contracts & Schemas ==="
    )

    for name, passed in checks.items():
        print(f"{name}: {passed}")

    print("output:", output_path)

    assert all(checks.values()), checks

    print(
        "\nDONE: Review workspace API "
        "contracts test completed."
    )


if __name__ == "__main__":
    main()