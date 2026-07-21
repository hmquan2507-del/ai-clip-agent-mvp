from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

from pydantic import ValidationError


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


from app.review.api import (
    REVIEW_AI_SUGGESTION_API_CONTRACT_VERSION,
    REVIEW_CLIPBOARD_API_CONTRACT_VERSION,
    REVIEW_TIMELINE_COMMAND_API_CONTRACT_VERSION,
    REVIEW_WORKSPACE_API_CONTRACT_VERSION,
    ApplyAISuggestionRequest,
    DismissAISuggestionRequest,
    RegenerateAISuggestionsRequest,
    ReviewAISuggestionAPIOperation,
    ReviewAISuggestionResponse,
    ReviewWorkspaceAPIErrorCode,
    ReviewWorkspaceAPIMapper,
    SelectAISuggestionRequest,
)
from app.review.application import (
    ReviewAISuggestionOperationError,
    ReviewAISuggestionRevisionConflictError,
)


PRODUCTION_ID = "221e4b01-5fb9-4b4a-a549-4fb32c455059"
SESSION_ID = "review-session-16-6-4"


def blocked(factory) -> bool:
    try:
        factory()
    except ValidationError:
        return True
    return False


def main() -> None:
    apply_request = ApplyAISuggestionRequest(
        session_id=SESSION_ID,
        suggestion_id="suggestion_1",
        expected_timeline_revision=4,
        expected_lifecycle_revision=2,
    )
    select_clear = SelectAISuggestionRequest(
        session_id=SESSION_ID,
        suggestion_id=None,
    )
    dismiss_request = DismissAISuggestionRequest(
        session_id=SESSION_ID,
        suggestion_id="suggestion_1",
    )
    regenerate_request = RegenerateAISuggestionsRequest(
        session_id=SESSION_ID,
        expected_lifecycle_revision=3,
    )

    source_snapshot = {
        "production_id": PRODUCTION_ID,
        "session_id": SESSION_ID,
        "timeline": {"revision": 4},
    }
    source_suggestions = {
        "production_id": PRODUCTION_ID,
        "lifecycle_revision": 2,
        "timeline_revision": 4,
        "read_model": {"suggestions": []},
    }
    response = ReviewAISuggestionResponse(
        operation=ReviewAISuggestionAPIOperation.GET,
        production_id=PRODUCTION_ID,
        session_id=SESSION_ID,
        timeline_revision=4,
        lifecycle_revision=2,
        workspace_snapshot=source_snapshot,
        suggestion_snapshot=source_suggestions,
        timeline_command_result=None,
        metadata={"source": "test"},
    )
    source_snapshot["timeline"]["revision"] = 999
    source_suggestions["read_model"]["suggestions"].append("mutated")
    output_payload = response.model_dump(mode="json")
    output_payload["metadata"]["mutated"] = True

    operation_error = ReviewAISuggestionOperationError(
        "unsupported",
        production_id=PRODUCTION_ID,
        session_id=SESSION_ID,
        operation="apply_suggestion",
        suggestion_id="suggestion_1",
    )
    conflict_error = ReviewAISuggestionRevisionConflictError(
        "conflict",
        production_id=PRODUCTION_ID,
        session_id=SESSION_ID,
        expected_revision=1,
        current_revision=2,
    )
    mapped_operation = ReviewWorkspaceAPIMapper.error_response(
        operation_error
    )
    mapped_conflict = ReviewWorkspaceAPIMapper.error_response(
        conflict_error
    )

    checks = {
        "legacy_contracts_preserved": (
            REVIEW_WORKSPACE_API_CONTRACT_VERSION == "16.2.3"
            and REVIEW_TIMELINE_COMMAND_API_CONTRACT_VERSION == "16.4.1"
            and REVIEW_CLIPBOARD_API_CONTRACT_VERSION == "16.4.8"
        ),
        "suggestion_contract_version_valid": (
            REVIEW_AI_SUGGESTION_API_CONTRACT_VERSION == "16.6.4"
            and response.contract_version == "16.6.4"
        ),
        "operations_complete": {
            item.value for item in ReviewAISuggestionAPIOperation
        } == {
            "get_suggestions",
            "select_suggestion",
            "apply_suggestion",
            "dismiss_suggestion",
            "regenerate_suggestions",
        },
        "apply_contract_valid": (
            apply_request.expected_timeline_revision == 4
            and apply_request.expected_lifecycle_revision == 2
        ),
        "select_clear_valid": select_clear.suggestion_id is None,
        "dismiss_contract_valid": (
            dismiss_request.suggestion_id == "suggestion_1"
        ),
        "regenerate_contract_valid": (
            regenerate_request.expected_lifecycle_revision == 3
        ),
        "empty_session_blocked": blocked(
            lambda: SelectAISuggestionRequest(
                session_id="",
                suggestion_id=None,
            )
        ),
        "empty_suggestion_blocked": blocked(
            lambda: ApplyAISuggestionRequest(
                session_id=SESSION_ID,
                suggestion_id="",
            )
        ),
        "invalid_revision_blocked": blocked(
            lambda: ApplyAISuggestionRequest(
                session_id=SESSION_ID,
                suggestion_id="suggestion_1",
                expected_timeline_revision=0,
            )
        ),
        "extra_fields_blocked": blocked(
            lambda: DismissAISuggestionRequest(
                session_id=SESSION_ID,
                suggestion_id="suggestion_1",
                unexpected=True,
            )
        ),
        "response_input_isolated": (
            response.workspace_snapshot["timeline"]["revision"] == 4
            and response.suggestion_snapshot["read_model"]["suggestions"] == []
        ),
        "response_output_isolated": (
            "mutated" not in response.metadata
        ),
        "operation_error_mapped": (
            mapped_operation.error.code
            == ReviewWorkspaceAPIErrorCode.AI_SUGGESTION_OPERATION_FAILED
        ),
        "conflict_error_mapped": (
            mapped_conflict.error.code
            == ReviewWorkspaceAPIErrorCode.AI_SUGGESTION_REVISION_CONFLICT
            and mapped_conflict.error.metadata["application_error"]
            ["expected_revision"] == 1
        ),
        "serialization_valid": bool(
            json.dumps(response.model_dump(mode="json"))
        ),
    }
    assert all(checks.values()), checks

    output = Path(
        "storage/demo_outputs/review_ai_suggestion_api_contracts.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {"checks": checks, "response": response.model_dump(mode="json")},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print("=== AI Suggestion API Contracts & Schemas ===")
    for name, value in checks.items():
        print(f"{name}: {value}")
    print(f"output: {output}")
    print("\nDONE: AI suggestion API contracts test completed.")


if __name__ == "__main__":
    main()
