from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.product import (
    ProductProductionStatus,
    build_product_snapshot_builder,
)


PRODUCTION_ID = (
    "221e4b01-5fb9-4b4a-a549-4fb32c455059"
)


@dataclass
class FakeProduction:
    id: str
    name: str
    version: int = 3
    status: str = "ready"
    platform: str = "tiktok"
    editing_style: str = "viral"
    language: str = "vi"


@dataclass
class FakeClip:
    clip_id: str
    start_time: float
    end_time: float
    local_path: str | None = None


@dataclass
class FakeTrack:
    track_id: str
    track_type: str
    clips: list[FakeClip] = field(
        default_factory=list
    )


@dataclass
class FakeTimeline:
    production_id: str
    version: str
    duration: float
    canvas: dict[str, Any]
    tracks: list[FakeTrack]
    effects: list[dict[str, Any]]
    transitions: list[dict[str, Any]]


@dataclass
class FakeArtifact:
    artifact_id: str
    artifact_type: str
    local_path: str
    mime_type: str
    size: int
    metadata: dict[str, Any]


@dataclass
class FakeQuality:
    status: str
    quality_score: float
    approved: bool
    warning_count: int
    failure_count: int
    report_path: str
    checks: list[dict[str, Any]]


def main() -> None:
    production = FakeProduction(
        id=PRODUCTION_ID,
        name="Video giới thiệu AI Clip Agent",
    )

    timeline = FakeTimeline(
        production_id=PRODUCTION_ID,
        version="14.11.0",
        duration=18.0,
        canvas={
            "width": 1080,
            "height": 1920,
            "fps": 30,
        },
        tracks=[
            FakeTrack(
                track_id="video_primary",
                track_type="video_primary",
                clips=[
                    FakeClip(
                        clip_id="clip_1",
                        start_time=0,
                        end_time=18,
                    )
                ],
            ),
            FakeTrack(
                track_id="broll",
                track_type="broll",
                clips=[
                    FakeClip(
                        clip_id="broll_1",
                        start_time=0,
                        end_time=4,
                        local_path=(
                            "storage/assets/broll.mp4"
                        ),
                    ),
                    FakeClip(
                        clip_id="broll_2",
                        start_time=10,
                        end_time=14,
                        local_path=(
                            "storage/assets/broll_2.mp4"
                        ),
                    ),
                ],
            ),
        ],
        effects=[
            {
                "effect_id": "effect_1",
                "effect_type": "zoom_in",
            }
        ],
        transitions=[
            {
                "transition_id": "transition_1",
                "transition_type": "clean_cut",
            }
        ],
    )

    artifacts = [
        FakeArtifact(
            artifact_id="final_video",
            artifact_type="final_video",
            local_path=(
                "storage/artifacts/final.mp4"
            ),
            mime_type="video/mp4",
            size=8_368_750,
            metadata={
                "duration": 18.0,
                "width": 1080,
                "height": 1920,
                "fps": 30.0,
            },
        ),
        FakeArtifact(
            artifact_id="thumbnail",
            artifact_type="thumbnail",
            local_path=(
                "storage/artifacts/thumbnail.jpg"
            ),
            mime_type="image/jpeg",
            size=45_000,
            metadata={},
        ),
    ]

    quality = FakeQuality(
        status="approved",
        quality_score=100.0,
        approved=True,
        warning_count=0,
        failure_count=0,
        report_path=(
            "storage/artifacts/"
            "render_quality_report.json"
        ),
        checks=[
            {
                "check_type": "black_frame",
                "status": "pass",
            }
        ],
    )

    snapshot = (
        build_product_snapshot_builder()
        .build(
            production=production,
            timeline=timeline,
            artifacts=artifacts,
            quality_report=quality,
            ai_summary={
                "story_type": "problem_solution",
                "editing_style": "viral",
            },
            issues=[],
            status=(
                ProductProductionStatus
                .READY_FOR_REVIEW
            ),
            progress=100,
            progress_message=(
                "Video đã sẵn sàng để xem "
                "và chỉnh sửa."
            ),
        )
    )

    payload = snapshot.to_dict()

    output_path = Path(
        "storage/demo_outputs/"
        "product_adapter_snapshot.json"
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

    print("=== Product Adapter Layer ===")
    print(
        "production_id:",
        payload["production"]["production_id"],
    )
    print(
        "status:",
        payload["production"]["status"],
    )
    print(
        "stage:",
        payload["production"]["stage"],
    )
    print(
        "timeline_available:",
        payload["timeline"]["available"],
    )
    print(
        "track_count:",
        payload["timeline"]["track_count"],
    )
    print(
        "clip_count:",
        payload["timeline"]["clip_count"],
    )
    print(
        "preview_available:",
        payload["preview"]["available"],
    )
    print(
        "quality_status:",
        payload["quality"]["status"],
    )
    print(
        "artifact_count:",
        len(payload["artifacts"]),
    )
    print(
        "allowed_actions:",
        payload["production"][
            "allowed_actions"
        ],
    )
    print("output:", output_path)

    assert (
        payload["production"]["status"]
        == "ready_for_review"
    )

    assert payload["timeline"]["available"] is True
    assert payload["timeline"]["track_count"] == 2
    assert payload["timeline"]["clip_count"] == 3

    assert payload["preview"]["available"] is True

    assert (
        payload["preview"]["video_path"]
        == "storage/artifacts/final.mp4"
    )

    assert payload["quality"]["approved"] is True
    assert payload["quality"]["quality_score"] == 100.0

    assert len(payload["artifacts"]) == 2

    assert "edit_timeline" in (
        payload["production"][
            "allowed_actions"
        ]
    )

    print(
        "\nDONE: Product adapter layer "
        "test completed."
    )


if __name__ == "__main__":
    main()