from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.review.suggestions import (
    AI_SUGGESTION_CONTRACT_VERSION,
    AISuggestionReadModelBuilder,
    AISuggestionStatus,
    build_ai_suggestion_read_model,
)


def main() -> None:
    source = [
        "Làm hook mạnh hơn trong 3 giây đầu.",
        {
            "id": "suggestion-broll-1",
            "type": "b-roll",
            "title": "Thêm B-roll sản phẩm",
            "message": (
                "Chèn cảnh sản phẩm để tăng "
                "độ rõ ràng."
            ),
            "timeline_revision": 7,
            "target": {
                "clip_id": "clip-2",
            },
            "command": {
                "operation": "insert_broll",
                "arguments": {
                    "clip_id": "clip-2",
                },
            },
            "confidence": 0.92,
            "metadata": {
                "model": "planner-v1",
            },
        },
        {
            "id": "suggestion-stale-1",
            "kind": "subtitle",
            "description": (
                "Rút ngắn phụ đề ở đoạn cuối."
            ),
            "timeline_revision": 6,
            "target": {
                "type": "range",
                "start_time": 8.0,
                "end_time": 10.0,
            },
            "command": "trim_subtitle",
        },
    ]
    source_before = json.dumps(
        source,
        sort_keys=True,
        ensure_ascii=False,
    )
    metadata = {
        "score": 88,
        "provider": "ai-planner",
    }

    builder = AISuggestionReadModelBuilder(
        now=lambda: (
            "2026-07-18T10:00:00+00:00"
        )
    )
    read_model = builder.build(
        production_id="production-1",
        timeline_revision=7,
        raw_suggestions=source,
        ai_metadata=metadata,
        selected_suggestion_id=(
            "suggestion-broll-1"
        ),
    )

    legacy = read_model.suggestions[0]
    actionable = read_model.get(
        "suggestion-broll-1"
    )
    stale = read_model.get(
        "suggestion-stale-1"
    )

    first_payload = read_model.to_dict()
    first_payload["suggestions"][1][
        "command"
    ]["arguments"]["clip_id"] = (
        "changed-outside"
    )
    first_payload["metadata"][
        "ai_metadata"
    ]["score"] = 0

    second_payload = read_model.to_dict()
    fetched = read_model.get(
        "suggestion-broll-1"
    )
    fetched.metadata["changed_outside"] = True

    duplicate_blocked = False
    try:
        builder.build(
            production_id="production-1",
            timeline_revision=7,
            raw_suggestions=[
                {"id": "duplicate"},
                {"id": "duplicate"},
            ],
        )
    except ValueError:
        duplicate_blocked = True

    invalid_range_blocked = False
    try:
        builder.build(
            production_id="production-1",
            timeline_revision=7,
            raw_suggestions=[
                {
                    "target": {
                        "type": "range",
                        "start_time": 5,
                        "end_time": 4,
                    }
                }
            ],
        )
    except ValueError:
        invalid_range_blocked = True

    factory_result = (
        build_ai_suggestion_read_model(
            production_id="production-1",
            timeline_revision=7,
            raw_suggestions=[],
        )
    )

    checks = {
        "contract_version_valid": (
            AI_SUGGESTION_CONTRACT_VERSION
            == "16.6.1"
        ),
        "legacy_suggestion_normalized": (
            legacy.description
            == source[0]
            and legacy.suggestion_id.startswith(
                "ai-suggestion-"
            )
        ),
        "structured_suggestion_valid": (
            actionable is not None
            and actionable.kind.value == "broll"
            and actionable.target.clip_id
            == "clip-2"
        ),
        "command_proposal_valid": (
            actionable is not None
            and actionable.actionable
            and actionable.command is not None
            and actionable.command.operation
            == "insert_broll"
        ),
        "score_normalized": (
            actionable is not None
            and actionable.score == 92.0
        ),
        "stale_revision_blocked": (
            stale is not None
            and stale.status
            == AISuggestionStatus.STALE
            and not stale.actionable
        ),
        "counts_valid": (
            read_model.count == 3
            and read_model.actionable_count == 1
            and read_model.stale_count == 1
        ),
        "selection_valid": (
            read_model.selected_suggestion_id
            == "suggestion-broll-1"
        ),
        "source_unchanged": (
            json.dumps(
                source,
                sort_keys=True,
                ensure_ascii=False,
            )
            == source_before
            and metadata["score"] == 88
        ),
        "payload_isolated": (
            second_payload["suggestions"][1]
            ["command"]["arguments"]
            ["clip_id"]
            == "clip-2"
            and second_payload["metadata"]
            ["ai_metadata"]["score"] == 88
            and "changed_outside"
            not in read_model.get(
                "suggestion-broll-1"
            ).metadata
        ),
        "duplicate_ids_blocked": (
            duplicate_blocked
        ),
        "invalid_range_blocked": (
            invalid_range_blocked
        ),
        "factory_backward_compatible": (
            factory_result.count == 0
            and factory_result.production_id
            == "production-1"
        ),
        "serialization_valid": (
            second_payload["contract_version"]
            == "16.6.1"
            and json.loads(
                json.dumps(
                    second_payload,
                    ensure_ascii=False,
                )
            )["count"] == 3
        ),
        "read_model_has_no_mutation_api": (
            not hasattr(
                read_model,
                "apply",
            )
            and not hasattr(
                read_model,
                "dismiss",
            )
            and not hasattr(
                read_model,
                "regenerate",
            )
        ),
    }

    assert all(checks.values()), checks

    output = Path(
        "storage/demo_outputs/"
        "review_ai_suggestion_read_model.json"
    )
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output.write_text(
        json.dumps(
            second_payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        "=== AI Suggestion Contracts & "
        "Read Model ==="
    )
    for name, value in checks.items():
        print(f"{name}: {value}")
    print(f"output: {output}")
    print(
        "\nDONE: AI suggestion contracts and "
        "read model test completed."
    )


if __name__ == "__main__":
    main()
