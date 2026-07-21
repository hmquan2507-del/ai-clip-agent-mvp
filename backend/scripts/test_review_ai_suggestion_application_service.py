from __future__ import annotations

import json
import sys
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from types import SimpleNamespace
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


from app.review.application import (
    AI_SUGGESTION_APPLICATION_CONTRACT_VERSION,
    ReviewAISuggestionApplicationServiceInterface,
    ReviewAISuggestionRevisionConflictError,
    build_review_ai_suggestion_application_service,
)
from app.review.application.suggestion_errors import (
    ReviewAISuggestionOperationError,
)
from app.review.suggestions import (
    AISuggestion,
    AISuggestionCommandProposal,
    AISuggestionKind,
    AISuggestionReadModel,
    AISuggestionStatus,
    AISuggestionTarget,
    AISuggestionTargetType,
    build_ai_suggestion_lifecycle_runtime,
)


PRODUCTION_ID = "221e4b01-5fb9-4b4a-a549-4fb32c455059"
SESSION_ID = "review-session-16-6-3"


@dataclass
class FakeTimeline:
    production_id: str
    revision: int = 1
    dirty: bool = False

    def clone(self):
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(self.__dict__)


class FakeTimelineStore:
    def __init__(self):
        self.timeline = FakeTimeline(PRODUCTION_ID)

    def snapshot(self):
        return self.timeline.clone()


@dataclass
class FakeWorkspaceSnapshot:
    production_id: str
    session_id: str
    timeline: FakeTimeline

    def clone(self):
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "session_id": self.session_id,
            "timeline": self.timeline.to_dict(),
        }


@dataclass
class FakeTimelineCommandResult:
    current_revision: int
    operation: str

    def clone(self):
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(self.__dict__)


class FakeSession:
    def __init__(self, suggestion_runtime):
        self.closed = False
        self.graph = SimpleNamespace(
            suggestion_runtime=suggestion_runtime,
            timeline_store=FakeTimelineStore(),
        )

    def snapshot(self):
        return FakeWorkspaceSnapshot(
            PRODUCTION_ID,
            SESSION_ID,
            self.graph.timeline_store.snapshot(),
        )


class FakeWorkspaceService:
    def __init__(self, session: FakeSession):
        self.operation_lock = RLock()
        self.session = session
        self.command_count = 0
        self.history_count = 0

    def get_session(self, production_id: str, *, session_id: str):
        assert production_id == PRODUCTION_ID
        assert session_id == SESSION_ID
        return self.session

    def move_clip(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_id: str,
        new_start_time: float,
        target_track_id: str | None = None,
        expected_revision: int | None = None,
    ):
        timeline = self.session.graph.timeline_store.timeline
        if expected_revision != timeline.revision:
            raise RuntimeError("revision conflict")
        assert production_id == PRODUCTION_ID
        assert session_id == SESSION_ID
        assert clip_id == "clip_1"
        assert new_start_time == 2.0
        assert target_track_id == "video_track"
        self.command_count += 1
        self.history_count += 1
        timeline.revision += 1
        timeline.dirty = True
        return FakeTimelineCommandResult(
            current_revision=timeline.revision,
            operation="move_clip",
        )


class FakeRegenerator:
    def regenerate(
        self,
        *,
        production_id: str,
        session_id: str,
        timeline_revision: int,
        current,
    ) -> AISuggestionReadModel:
        assert production_id == PRODUCTION_ID
        assert session_id == SESSION_ID
        assert current.production_id == PRODUCTION_ID
        return AISuggestionReadModel(
            production_id=production_id,
            timeline_revision=timeline_revision,
            suggestions=(
                make_suggestion(
                    "suggestion_regenerated",
                    timeline_revision,
                    operation="move_clip",
                ),
            ),
            metadata={"provider": "fake"},
        )


def make_suggestion(
    suggestion_id: str,
    revision: int,
    *,
    operation: str,
) -> AISuggestion:
    arguments = (
        {
            "clip_id": "clip_1",
            "new_start_time": 2.0,
            "target_track_id": "video_track",
        }
        if operation == "move_clip"
        else {}
    )
    return AISuggestion(
        suggestion_id=suggestion_id,
        production_id=PRODUCTION_ID,
        kind=AISuggestionKind.PACING,
        status=AISuggestionStatus.PROPOSED,
        title=f"Suggestion {suggestion_id}",
        description="Application service test suggestion.",
        timeline_revision=revision,
        target=AISuggestionTarget(
            production_id=PRODUCTION_ID,
            target_type=AISuggestionTargetType.CLIP,
            track_id="video_track",
            clip_id="clip_1",
        ),
        command=AISuggestionCommandProposal(
            operation=operation,
            arguments=arguments,
        ),
        score=90,
    )


def main() -> None:
    source_model = AISuggestionReadModel(
        production_id=PRODUCTION_ID,
        timeline_revision=1,
        suggestions=(
            make_suggestion("suggestion_move", 1, operation="move_clip"),
            make_suggestion("suggestion_unsupported", 1, operation="render_video"),
            make_suggestion("suggestion_dismiss", 1, operation="move_clip"),
        ),
    )
    source_payload = source_model.to_dict()
    suggestion_runtime = build_ai_suggestion_lifecycle_runtime(source_model)
    session = FakeSession(suggestion_runtime)
    workspace_service = FakeWorkspaceService(session)
    service = build_review_ai_suggestion_application_service(
        workspace_service=workspace_service,
        regenerator=FakeRegenerator(),
    )

    initial = service.get_ai_suggestions(
        PRODUCTION_ID,
        session_id=SESSION_ID,
    )
    selected = service.select_ai_suggestion(
        PRODUCTION_ID,
        session_id=SESSION_ID,
        suggestion_id="suggestion_move",
        expected_lifecycle_revision=1,
    )
    timeline_before_dismiss = session.graph.timeline_store.snapshot().to_dict()
    dismissed = service.dismiss_ai_suggestion(
        PRODUCTION_ID,
        session_id=SESSION_ID,
        suggestion_id="suggestion_dismiss",
        expected_lifecycle_revision=2,
    )
    timeline_after_dismiss = (
        session.graph.timeline_store.snapshot().to_dict()
    )

    before_failure_timeline = session.graph.timeline_store.snapshot().to_dict()
    before_failure_lifecycle = suggestion_runtime.snapshot().to_dict()
    unsupported_blocked = False
    try:
        service.apply_ai_suggestion(
            PRODUCTION_ID,
            session_id=SESSION_ID,
            suggestion_id="suggestion_unsupported",
            expected_timeline_revision=1,
            expected_lifecycle_revision=3,
        )
    except ReviewAISuggestionOperationError:
        unsupported_blocked = True
    after_unsupported_timeline = (
        session.graph.timeline_store.snapshot().to_dict()
    )
    after_unsupported_lifecycle = (
        suggestion_runtime.snapshot().to_dict()
    )

    conflict_blocked = False
    try:
        service.apply_ai_suggestion(
            PRODUCTION_ID,
            session_id=SESSION_ID,
            suggestion_id="suggestion_move",
            expected_timeline_revision=99,
            expected_lifecycle_revision=3,
        )
    except ReviewAISuggestionRevisionConflictError:
        conflict_blocked = True

    applied = service.apply_ai_suggestion(
        PRODUCTION_ID,
        session_id=SESSION_ID,
        suggestion_id="suggestion_move",
        expected_timeline_revision=1,
        expected_lifecycle_revision=3,
    )
    timeline_before_regenerate = session.graph.timeline_store.snapshot().to_dict()
    regenerated = service.regenerate_ai_suggestions(
        PRODUCTION_ID,
        session_id=SESSION_ID,
        expected_lifecycle_revision=4,
    )

    isolated_payload = regenerated.to_dict()
    isolated_payload["metadata"]["mutated"] = True

    checks = {
        "interface_contract_valid": isinstance(
            service,
            ReviewAISuggestionApplicationServiceInterface,
        ),
        "contract_version_valid": (
            regenerated.to_dict()["contract_version"]
            == AI_SUGGESTION_APPLICATION_CONTRACT_VERSION
        ),
        "shared_lock_used": service.uses_shared_operation_lock,
        "get_read_only": (
            initial.timeline_revision == 1
            and initial.lifecycle_revision == 1
        ),
        "select_delegated": (
            selected.suggestion_snapshot.read_model.selected_suggestion_id
            == "suggestion_move"
        ),
        "dismiss_read_only": (
            timeline_before_dismiss
            == timeline_after_dismiss
        ),
        "unsupported_command_blocked": unsupported_blocked,
        "failure_read_only": (
            before_failure_timeline["revision"] == 1
            and before_failure_timeline
            == after_unsupported_timeline
            and before_failure_lifecycle["lifecycle_revision"]
            == after_unsupported_lifecycle["lifecycle_revision"]
            and before_failure_lifecycle["read_model"]
            == after_unsupported_lifecycle["read_model"]
            and workspace_service.command_count == 1
        ),
        "revision_conflict_blocked": conflict_blocked,
        "apply_history_backed_once": (
            workspace_service.command_count == 1
            and workspace_service.history_count == 1
            and applied.timeline_revision == 2
        ),
        "apply_marks_lifecycle": (
            applied.suggestion_snapshot.read_model
            .get("suggestion_move").status
            == AISuggestionStatus.APPLIED
        ),
        "regenerate_atomic": (
            regenerated.suggestion_snapshot.read_model.count == 1
            and regenerated.suggestion_snapshot.timeline_revision == 2
            and timeline_before_regenerate
            == session.graph.timeline_store.snapshot().to_dict()
        ),
        "result_isolated": (
            "mutated" not in regenerated.metadata
        ),
        "source_unchanged": source_model.to_dict() == source_payload,
        "serialization_valid": bool(
            json.dumps(regenerated.to_dict())
        ),
        "no_direct_timeline_mutation": (
            service.to_dict()["direct_timeline_mutation"] is False
        ),
    }
    assert all(checks.values()), checks

    output = Path("storage/demo_outputs/review_ai_suggestion_application_service.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {"checks": checks, "result": regenerated.to_dict()},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=== AI Suggestion Application Service ===")
    for name, value in checks.items():
        print(f"{name}: {value}")
    print(f"output: {output}")
    print("\nDONE: AI suggestion application service test completed.")


if __name__ == "__main__":
    main()
