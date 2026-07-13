from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.product import (
    ProductProductionStatus,
    build_repository_product_workspace_service,
)


PRODUCTION_ID = (
    "221e4b01-5fb9-4b4a-a549-4fb32c455059"
)


@dataclass
class FakeProduction:
    id: str
    name: str
    status: str = "ready"
    version: int = 5
    platform: str = "tiktok"
    editing_style: str = "viral"
    language: str = "vi"


class FakeProductionRepository:
    def __init__(
        self,
        production: FakeProduction,
    ):
        self.production = production

    def get_by_id(
        self,
        production_id,
    ):
        if str(production_id) != (
            self.production.id
        ):
            return None

        return self.production


class FakeTimelineRepository:
    def get_latest_by_production_id(
        self,
        production_id,
    ) -> dict[str, Any]:
        return {
            "production_id": str(
                production_id
            ),
            "version": "14.11.0",
            "duration": 18.0,
            "canvas": {
                "width": 1080,
                "height": 1920,
                "fps": 30,
            },
            "tracks": [
                {
                    "track_id": (
                        "video_primary"
                    ),
                    "track_type": (
                        "video_primary"
                    ),
                    "clips": [
                        {
                            "clip_id": "source_1",
                            "start_time": 0,
                            "end_time": 18,
                        }
                    ],
                },
                {
                    "track_id": "broll",
                    "track_type": "broll",
                    "clips": [
                        {
                            "clip_id": "broll_1",
                            "start_time": 0,
                            "end_time": 4,
                        }
                    ],
                },
            ],
            "effects": [],
            "transitions": [],
        }


class FakeArtifactRepository:
    def list_by_production_id(
        self,
        production_id,
    ) -> list[dict[str, Any]]:
        return [
            {
                "artifact_id": (
                    "final_video"
                ),
                "artifact_type": (
                    "final_video"
                ),
                "local_path": (
                    "storage/artifacts/"
                    "final.mp4"
                ),
                "mime_type": "video/mp4",
                "file_size": 8_368_750,
                "metadata": {
                    "duration": 18.0,
                    "width": 1080,
                    "height": 1920,
                    "fps": 30.0,
                },
            },
            {
                "artifact_id": "thumbnail",
                "artifact_type": "thumbnail",
                "local_path": (
                    "storage/artifacts/"
                    "thumbnail.jpg"
                ),
                "mime_type": "image/jpeg",
                "file_size": 50_000,
                "metadata": {},
            },
        ]


class FakeQualityRepository:
    def get_latest_by_production_id(
        self,
        production_id,
    ) -> dict[str, Any]:
        return {
            "production_id": str(
                production_id
            ),
            "status": "approved",
            "quality_score": 100.0,
            "approved": True,
            "warning_count": 0,
            "failure_count": 0,
            "report_path": (
                "storage/artifacts/"
                "render_quality_report.json"
            ),
            "checks": [],
        }


class FakeAIRepository:
    def get_by_production_id(
        self,
        production_id,
    ) -> dict[str, Any]:
        return {
            "summary": (
                "Video giới thiệu giải pháp "
                "dựng video bằng AI."
            ),
            "hook": (
                "Bạn đang mất quá nhiều "
                "thời gian để edit video."
            ),
            "story_type": (
                "problem_solution"
            ),
            "emotion": "inspirational",
            "editing_style": "viral",
        }


class FakeIssueRepository:
    def list_by_production_id(
        self,
        production_id,
    ) -> list[dict[str, Any]]:
        return []


def main() -> None:
    production_repository = (
        FakeProductionRepository(
            FakeProduction(
                id=PRODUCTION_ID,
                name=(
                    "Video giới thiệu "
                    "AI Clip Agent"
                ),
            )
        )
    )

    service = (
        build_repository_product_workspace_service(
            production_repository=(
                production_repository
            ),
            timeline_repository=(
                FakeTimelineRepository()
            ),
            artifact_repository=(
                FakeArtifactRepository()
            ),
            quality_repository=(
                FakeQualityRepository()
            ),
            ai_repository=(
                FakeAIRepository()
            ),
            issue_repository=(
                FakeIssueRepository()
            ),
            cache_ttl_seconds=60,
        )
    )

    result = service.load_workspace_result(
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

    assert result.success is True
    assert result.snapshot is not None

    snapshot = result.snapshot
    payload = result.to_dict()

    output_path = Path(
        "storage/demo_outputs/"
        "repository_workspace_adapters.json"
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
        "=== Repository Workspace Adapters ==="
    )
    print(
        "production_loaded:",
        snapshot.production is not None,
    )
    print(
        "timeline_loaded:",
        snapshot.timeline.available,
    )
    print(
        "artifacts_loaded:",
        bool(snapshot.artifacts),
    )
    print(
        "quality_loaded:",
        snapshot.quality.available,
    )
    print(
        "ai_summary_loaded:",
        bool(snapshot.ai_summary),
    )
    print(
        "issues_loaded:",
        snapshot.issues is not None,
    )
    print(
        "snapshot_created:",
        result.snapshot is not None,
    )
    print(
        "status:",
        snapshot.production.status,
    )
    print(
        "track_count:",
        snapshot.timeline.track_count,
    )
    print(
        "artifact_count:",
        len(snapshot.artifacts),
    )
    print(
        "quality_score:",
        snapshot.quality.quality_score,
    )
    print("output:", output_path)

    assert (
        snapshot.production
        .production_id
        == PRODUCTION_ID
    )

    assert (
        snapshot.production.status.value
        == "ready_for_review"
    )

    assert (
        snapshot.timeline.track_count
        == 2
    )

    assert (
        snapshot.timeline.clip_count
        == 2
    )

    assert len(
        snapshot.artifacts
    ) >= 2

    assert (
        snapshot.preview.available
        is True
    )

    assert (
        snapshot.quality.approved
        is True
    )

    assert (
        snapshot.quality.quality_score
        == 100.0
    )

    assert (
        snapshot.ai_summary[
            "story_type"
        ]
        == "problem_solution"
    )

    second = service.load_workspace_result(
        PRODUCTION_ID
    )

    assert second.success is True
    assert second.cache_hit is True

    print(
        "\nDONE: Repository workspace "
        "adapters test completed."
    )


if __name__ == "__main__":
    main()