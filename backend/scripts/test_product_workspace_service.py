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
    build_in_memory_product_workspace_service,
)


PRODUCTION_ID = (
    "221e4b01-5fb9-4b4a-a549-4fb32c455059"
)


@dataclass
class FakeProduction:
    id: str
    name: str
    status: str = "ready"
    version: int = 4
    platform: str = "tiktok"
    editing_style: str = "viral"
    language: str = "vi"


@dataclass
class FakeClip:
    clip_id: str
    start_time: float
    end_time: float


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
    service, loader = (
        build_in_memory_product_workspace_service(
            ttl_seconds=60,
        )
    )

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
                        clip_id="source_1",
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
                    )
                ],
            ),
        ],
        effects=[],
        transitions=[],
    )

    artifacts = [
        FakeArtifact(
            artifact_id="final_video",
            artifact_type="final_video",
            local_path=(
                "storage/artifacts/final.mp4"
            ),
            mime_type="video/mp4",
            size=8_000_000,
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
            size=50_000,
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
        checks=[],
    )

    loader.register(
        PRODUCTION_ID,
        production=production,
        timeline=timeline,
        artifacts=artifacts,
        quality_report=quality,
        ai_summary={
            "story_type": "problem_solution",
            "editing_style": "viral",
        },
        issues=[],
    )

    first = service.load_workspace_result(
        PRODUCTION_ID,
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

    second = service.load_workspace_result(
        PRODUCTION_ID,
    )

    refreshed = service.refresh_workspace(
        PRODUCTION_ID,
        status=(
            ProductProductionStatus
            .READY_FOR_REVIEW
        ),
    )

    payload = {
        "first": first.to_dict(),
        "second": second.to_dict(),
        "refreshed": refreshed.to_dict(),
    }

    output_path = Path(
        "storage/demo_outputs/"
        "product_workspace_service.json"
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
        "=== Product Workspace Service ==="
    )
    print(
        "first_success:",
        first.success,
    )
    print(
        "first_cache_hit:",
        first.cache_hit,
    )
    print(
        "second_success:",
        second.success,
    )
    print(
        "second_cache_hit:",
        second.cache_hit,
    )
    print(
        "status:",
        first.snapshot.production.status,
    )
    print(
        "timeline_available:",
        first.snapshot.timeline.available,
    )
    print(
        "preview_available:",
        first.snapshot.preview.available,
    )
    print(
        "quality_approved:",
        first.snapshot.quality.approved,
    )
    print(
        "artifact_count:",
        len(first.snapshot.artifacts),
    )
    print("output:", output_path)

    assert first.success is True
    assert first.cache_hit is False
    assert first.snapshot is not None

    assert second.success is True
    assert second.cache_hit is True

    assert (
        first.snapshot.production
        .production_id
        == PRODUCTION_ID
    )

    assert (
        first.snapshot.production
        .status.value
        == "ready_for_review"
    )

    assert (
        first.snapshot.timeline.available
        is True
    )

    assert (
        first.snapshot.preview.available
        is True
    )

    assert (
        first.snapshot.quality.approved
        is True
    )

    assert len(
        first.snapshot.artifacts
    ) == 2

    assert (
        refreshed.production.production_id
        == PRODUCTION_ID
    )

    service.invalidate_workspace(
        PRODUCTION_ID
    )

    missing = (
        service.load_workspace_result(
            "missing-production"
        )
    )

    assert missing.success is False
    assert missing.snapshot is None
    assert missing.errors

    print(
        "\nDONE: Product workspace service "
        "test completed."
    )


if __name__ == "__main__":
    main()