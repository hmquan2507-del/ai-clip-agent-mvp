from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from threading import Barrier
from typing import Any

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.product import (
    ProductWorkspaceNotFoundError,
    build_in_memory_product_workspace_service,
)
from app.review import (
    ReviewRuntimeSessionConflictError,
    ReviewRuntimeSessionNotFoundError,
    ReviewWorkspaceApplicationConfig,
    ReviewWorkspaceApplicationServiceInterface,
    build_in_memory_review_runtime_session_registry,
    build_review_workspace_application_service,
)


PRODUCTION_ID = "review-application-service-1"
CONCURRENT_PRODUCTION_ID = (
    "review-application-service-2"
)


@dataclass
class FakeProduction:
    id: str
    name: str
    status: str = "ready"
    version: int = 1
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


class BarrierWorkspaceService:
    def __init__(
        self,
        service: Any,
        parties: int,
    ):
        self.service = service
        self.barrier = Barrier(parties)

    def load_workspace(
        self,
        production_id: str,
        **kwargs: Any,
    ) -> Any:
        self.barrier.wait(timeout=10)

        return self.service.load_workspace(
            production_id,
            **kwargs,
        )


def register_workspace(
    loader: Any,
    production_id: str,
) -> FakeTimeline:
    timeline = FakeTimeline(
        production_id=production_id,
        version="16.2.2",
        duration=8.0,
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
                        start_time=0.0,
                        end_time=4.0,
                    ),
                    FakeClip(
                        clip_id="clip_2",
                        start_time=4.0,
                        end_time=8.0,
                    ),
                ],
            ),
            FakeTrack(
                track_id="broll",
                track_type="broll",
            ),
        ],
        effects=[],
        transitions=[],
    )

    loader.register(
        production_id,
        production=FakeProduction(
            id=production_id,
            name=(
                f"Review workspace "
                f"{production_id}"
            ),
        ),
        timeline=timeline,
        artifacts=[
            FakeArtifact(
                artifact_id="final_video",
                artifact_type="final_video",
                local_path=(
                    "storage/artifacts/final.mp4"
                ),
                mime_type="video/mp4",
                size=1_000_000,
                metadata={
                    "duration": 8.0,
                    "width": 1080,
                    "height": 1920,
                    "fps": 30.0,
                },
            )
        ],
        quality_report=FakeQuality(
            status="approved",
            quality_score=100.0,
            approved=True,
            warning_count=0,
            failure_count=0,
            report_path=(
                "storage/artifacts/quality.json"
            ),
            checks=[],
        ),
        ai_summary={
            "editing_style": "viral"
        },
        issues=[],
    )

    return timeline


def main() -> None:
    product_service, loader = (
        build_in_memory_product_workspace_service(
            ttl_seconds=60,
        )
    )

    source_timeline = register_workspace(
        loader,
        PRODUCTION_ID,
    )
    source_before = deepcopy(
        source_timeline
    )

    register_workspace(
        loader,
        CONCURRENT_PRODUCTION_ID,
    )

    registry = (
        build_in_memory_review_runtime_session_registry(
            ttl_seconds=1800,
        )
    )

    service = (
        build_review_workspace_application_service(
            product_workspace_service=(
                product_service
            ),
            session_registry=registry,
            config=(
                ReviewWorkspaceApplicationConfig(
                    maximum_history_size=25,
                    maximum_clipboard_history_size=10,
                )
            ),
        )
    )

    interface_contract_valid = isinstance(
        service,
        ReviewWorkspaceApplicationServiceInterface,
    )

    first = service.open_session(
        PRODUCTION_ID
    )

    open_ready = (
        first.state.ready
        and registry.count == 1
    )

    repeated = service.open_session(
        PRODUCTION_ID
    )
    open_idempotent = repeated is first

    conflict_blocked = False
    conflict_payload_valid = False

    try:
        service.open_session(
            PRODUCTION_ID,
            force_refresh=True,
        )
    except ReviewRuntimeSessionConflictError as error:
        conflict_blocked = True
        conflict_payload_valid = (
            error.to_dict()["code"]
            == "review_session_conflict"
        )

    lookup_valid = (
        service.get_session(
            PRODUCTION_ID,
            session_id=first.session_id,
        )
        is first
    )

    wrong_session_blocked = False

    try:
        service.get_session(
            PRODUCTION_ID,
            session_id="wrong-session",
        )
    except ReviewRuntimeSessionNotFoundError:
        wrong_session_blocked = True

    initial_snapshot = service.get_snapshot(
        PRODUCTION_ID,
        session_id=first.session_id,
    )

    edit_result = (
        first.graph.history_runtime
        .trim_clip_end(
            "clip_1",
            3.5,
        )
    )

    changed_snapshot = service.get_snapshot(
        PRODUCTION_ID
    )

    edit_visible = (
        edit_result.success
        and changed_snapshot.timeline.revision
        == initial_snapshot.timeline.revision + 1
        and changed_snapshot.timeline.dirty
    )

    reset_snapshot = service.reset_session(
        PRODUCTION_ID,
        session_id=first.session_id,
    )

    reset_integrated = (
        reset_snapshot.timeline.revision
        == initial_snapshot.timeline.revision
        and not reset_snapshot.timeline.dirty
        and (
            reset_snapshot
            .history_state
            .undo_count
            == 0
        )
        and (
            reset_snapshot
            .clipboard_content
            .item_count
            == 0
        )
    )

    replacement = service.open_session(
        PRODUCTION_ID,
        force_refresh=True,
        replace_existing=True,
    )

    replace_integrated = (
        replacement is not first
        and (
            replacement.session_id
            != first.session_id
        )
        and first.closed
        and (
            registry.get(PRODUCTION_ID)
            is replacement
        )
    )

    worker_count = 5

    concurrent_registry = (
        build_in_memory_review_runtime_session_registry(
            ttl_seconds=1800,
        )
    )

    concurrent_service = (
        build_review_workspace_application_service(
            product_workspace_service=(
                BarrierWorkspaceService(
                    product_service,
                    worker_count,
                )
            ),
            session_registry=(
                concurrent_registry
            ),
        )
    )

    with ThreadPoolExecutor(
        max_workers=worker_count
    ) as executor:
        sessions = list(
            executor.map(
                lambda _: (
                    concurrent_service
                    .open_session(
                        CONCURRENT_PRODUCTION_ID
                    )
                ),
                range(worker_count),
            )
        )

    concurrent_open_atomic = (
        len(
            {
                session.session_id
                for session in sessions
            }
        )
        == 1
        and concurrent_registry.count == 1
    )

    cleanup_delegated = (
        service.cleanup_expired_sessions()
        == []
    )

    close_result = service.close_session(
        PRODUCTION_ID,
        session_id=replacement.session_id,
    )

    close_integrated = (
        close_result.success
        and replacement.closed
        and registry.get(PRODUCTION_ID)
        is None
    )

    missing_session_blocked = False

    try:
        service.close_session(
            PRODUCTION_ID,
            session_id=(
                replacement.session_id
            ),
        )
    except ReviewRuntimeSessionNotFoundError:
        missing_session_blocked = True

    missing_workspace_propagated = False

    try:
        service.open_session(
            "missing-production"
        )
    except ProductWorkspaceNotFoundError:
        missing_workspace_propagated = True

    source_unchanged = (
        source_timeline == source_before
    )

    serialized = json.loads(
        json.dumps(
            service.to_dict(),
            ensure_ascii=False,
        )
    )

    serialization_valid = (
        serialized["service"]
        == "ReviewWorkspaceApplicationService"
    )

    concurrent_session = sessions[0]

    concurrent_service.close_session(
        CONCURRENT_PRODUCTION_ID,
        session_id=(
            concurrent_session.session_id
        ),
    )

    checks = {
        "interface_contract_valid": (
            interface_contract_valid
        ),
        "open_ready": open_ready,
        "open_idempotent": open_idempotent,
        "conflict_blocked": conflict_blocked,
        "conflict_payload_valid": (
            conflict_payload_valid
        ),
        "lookup_valid": lookup_valid,
        "wrong_session_blocked": (
            wrong_session_blocked
        ),
        "edit_visible": edit_visible,
        "reset_integrated": reset_integrated,
        "replace_integrated": replace_integrated,
        "concurrent_open_atomic": (
            concurrent_open_atomic
        ),
        "cleanup_delegated": (
            cleanup_delegated
        ),
        "close_integrated": close_integrated,
        "missing_session_blocked": (
            missing_session_blocked
        ),
        "missing_workspace_propagated": (
            missing_workspace_propagated
        ),
        "source_unchanged": source_unchanged,
        "serialization_valid": (
            serialization_valid
        ),
    }

    output_path = Path(
        "storage/demo_outputs/"
        "review_workspace_application_service.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            {
                "checks": checks,
                "service": service.to_dict(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "=== Review Workspace "
        "Application Service ==="
    )

    for name, passed in checks.items():
        print(f"{name}: {passed}")

    print("output:", output_path)

    assert all(checks.values()), checks

    print(
        "\nDONE: Review workspace application "
        "service test completed."
    )


if __name__ == "__main__":
    main()