from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.product import (
    InvalidProductStateTransitionError,
    ProductEvent,
    ProductEventType,
    ProductProductionSnapshot,
    ProductProductionStatus,
    ProductProgress,
    ProductStage,
    build_product_state_machine,
)


PRODUCTION_ID = (
    "221e4b01-5fb9-4b4a-a549-4fb32c455059"
)


def main() -> None:
    state_machine = (
        build_product_state_machine()
    )

    expected_flow = [
        ProductProductionStatus.DRAFT,
        ProductProductionStatus.UPLOADING,
        ProductProductionStatus.UPLOADED,
        ProductProductionStatus.QUEUED,
        ProductProductionStatus.TRANSCRIBING,
        ProductProductionStatus.ANALYZING,
        ProductProductionStatus.PLANNING,
        ProductProductionStatus.RESOLVING_ASSETS,
        ProductProductionStatus.BUILDING_TIMELINE,
        ProductProductionStatus.RENDERING_PREVIEW,
        ProductProductionStatus.READY_FOR_REVIEW,
        ProductProductionStatus.RENDERING_FINAL,
        ProductProductionStatus.QUALITY_CHECK,
        ProductProductionStatus.COMPLETED,
    ]

    current_status = expected_flow[0]

    transitions: list[dict] = []

    for next_status in expected_flow[1:]:
        current_status = state_machine.transition(
            current_status=current_status,
            next_status=next_status,
        )

        transitions.append(
            {
                "status": current_status.value,
                "stage": (
                    state_machine
                    .stage_for_status(
                        current_status
                    )
                    .value
                ),
                "allowed_actions": [
                    action.value
                    for action
                    in state_machine.allowed_actions(
                        current_status
                    )
                ],
            }
        )

    invalid_transition_blocked = False

    try:
        state_machine.transition(
            current_status=(
                ProductProductionStatus.DRAFT
            ),
            next_status=(
                ProductProductionStatus.COMPLETED
            ),
        )
    except InvalidProductStateTransitionError:
        invalid_transition_blocked = True

    progress = ProductProgress(
        stage=ProductStage.REVIEW,
        progress=100.0,
        message=(
            "Video đã sẵn sàng để xem "
            "và chỉnh sửa."
        ),
        status=(
            ProductProductionStatus
            .READY_FOR_REVIEW
        ),
    )

    snapshot = ProductProductionSnapshot(
        production_id=PRODUCTION_ID,
        name="Video giới thiệu AI Clip Agent",
        status=(
            ProductProductionStatus
            .READY_FOR_REVIEW
        ),
        stage=ProductStage.REVIEW,
        progress=progress,
        version=1,
        platform="tiktok",
        editing_style="viral",
        language="vi",
        allowed_actions=(
            state_machine.allowed_actions(
                ProductProductionStatus
                .READY_FOR_REVIEW
            )
        ),
    )

    event = ProductEvent(
        event_type=(
            ProductEventType.REVIEW_READY
        ),
        production_id=PRODUCTION_ID,
        stage=ProductStage.REVIEW,
        status=(
            ProductProductionStatus
            .READY_FOR_REVIEW
        ),
        progress=100.0,
        message=(
            "Video đã sẵn sàng để xem "
            "và chỉnh sửa."
        ),
    )

    output = {
        "flow": transitions,
        "invalid_transition_blocked": (
            invalid_transition_blocked
        ),
        "snapshot": snapshot.to_dict(),
        "event": event.to_dict(),
    }

    output_path = Path(
        "storage/demo_outputs/"
        "product_architecture_contracts.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "=== Product Architecture Contracts ==="
    )
    print(
        "transition_count:",
        len(transitions),
    )
    print(
        "final_status:",
        current_status.value,
    )
    print(
        "invalid_transition_blocked:",
        invalid_transition_blocked,
    )
    print(
        "review_allowed_actions:",
        snapshot.to_dict()[
            "allowed_actions"
        ],
    )
    print("output:", output_path)

    assert current_status == (
        ProductProductionStatus.COMPLETED
    )

    assert invalid_transition_blocked is True

    assert (
        snapshot.to_dict()["status"]
        == "ready_for_review"
    )

    assert "edit_timeline" in (
        snapshot.to_dict()[
            "allowed_actions"
        ]
    )

    assert "render_final" in (
        snapshot.to_dict()[
            "allowed_actions"
        ]
    )

    assert (
        event.to_dict()["message"]
        == "Video đã sẵn sàng để xem "
        "và chỉnh sửa."
    )

    print(
        "\nDONE: Product architecture "
        "contracts test completed."
    )


if __name__ == "__main__":
    main()