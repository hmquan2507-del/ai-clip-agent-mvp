from __future__ import annotations

import json
import sys
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(BACKEND_ROOT),
    )


from app.review.application import (
    ReviewTimelineCommandOperationError,
    ReviewTimelineCommandType,
    ReviewTimelineRevisionConflictError,
    ReviewWorkspaceApplicationService,
    ReviewWorkspaceApplicationServiceInterface,
)


OUTPUT_PATH = (
    BACKEND_ROOT
    / "storage"
    / "demo_outputs"
    / (
        "review_timeline_mutation_"
        "application_service.json"
    )
)


@dataclass
class FakeTimeline:
    production_id: str
    revision: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "revision": self.revision,
        }


@dataclass
class FakeSnapshot:
    production_id: str
    session_id: str
    timeline: FakeTimeline

    def clone(self) -> FakeSnapshot:
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "session_id": self.session_id,
            "timeline": self.timeline.to_dict(),
        }


@dataclass
class FakePayload:
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(self.payload)


@dataclass
class FakeHistoryState:
    production_id: str
    current_revision: int
    undo_count: int
    redo_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "current_revision": (
                self.current_revision
            ),
            "can_undo": self.undo_count > 0,
            "can_redo": self.redo_count > 0,
            "undo_count": self.undo_count,
            "redo_count": self.redo_count,
        }


@dataclass
class FakeHistoryResult:
    success: bool
    state: FakeHistoryState

    command: FakePayload | None = None
    event: FakePayload | None = None
    error: str | None = None


class FakeHistoryRuntime:
    def __init__(
        self,
        session: FakeSession,
    ):
        self.session = session
        self.undo_count = 0
        self.redo_count = 0
        self.fail_next = False

    def _execute(
        self,
        operation: str,
    ) -> FakeHistoryResult:
        if self.fail_next:
            self.fail_next = False
            return FakeHistoryResult(
                success=False,
                state=self._state(),
                error="Synthetic command failure.",
            )

        previous_revision = (
            self.session.timeline_revision
        )
        self.session.timeline_revision += 1
        self.undo_count += 1
        self.redo_count = 0

        return FakeHistoryResult(
            success=True,
            state=self._state(),
            command=FakePayload(
                {
                    "command_id": (
                        f"command-{operation}"
                    ),
                    "operation_type": operation,
                    "before_revision": (
                        previous_revision
                    ),
                    "after_revision": (
                        self.session
                        .timeline_revision
                    ),
                }
            ),
            event=FakePayload(
                {
                    "action": "execute",
                    "operation_type": operation,
                }
            ),
        )

    def _state(self) -> FakeHistoryState:
        return FakeHistoryState(
            production_id=(
                self.session.production_id
            ),
            current_revision=(
                self.session.timeline_revision
            ),
            undo_count=self.undo_count,
            redo_count=self.redo_count,
        )

    def move_clip(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> FakeHistoryResult:
        return self._execute("move_clip")

    def trim_clip_start(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> FakeHistoryResult:
        return self._execute(
            "trim_clip_start"
        )

    def trim_clip_end(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> FakeHistoryResult:
        return self._execute(
            "trim_clip_end"
        )

    def split_clip(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> FakeHistoryResult:
        return self._execute("split_clip")

    def duplicate_clip(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> FakeHistoryResult:
        return self._execute(
            "duplicate_clip"
        )

    def delete_clip(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> FakeHistoryResult:
        return self._execute("delete_clip")

    def close_gap(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> FakeHistoryResult:
        return self._execute("close_gap")

    def undo(self) -> FakeHistoryResult:
        if self.undo_count < 1:
            return FakeHistoryResult(
                success=False,
                state=self._state(),
                error="Nothing to undo.",
            )

        self.session.timeline_revision += 1
        self.undo_count -= 1
        self.redo_count += 1

        return FakeHistoryResult(
            success=True,
            state=self._state(),
            command=FakePayload(
                {
                    "command_id": "undo-command",
                }
            ),
            event=FakePayload(
                {
                    "action": "undo",
                }
            ),
        )

    def redo(self) -> FakeHistoryResult:
        if self.redo_count < 1:
            return FakeHistoryResult(
                success=False,
                state=self._state(),
                error="Nothing to redo.",
            )

        self.session.timeline_revision += 1
        self.undo_count += 1
        self.redo_count -= 1

        return FakeHistoryResult(
            success=True,
            state=self._state(),
            command=FakePayload(
                {
                    "command_id": "redo-command",
                }
            ),
            event=FakePayload(
                {
                    "action": "redo",
                }
            ),
        )


class FakeSession:
    def __init__(
        self,
        production_id: str,
        session_id: str,
    ):
        self.production_id = production_id
        self.session_id = session_id
        self.timeline_revision = 1
        self.closed = False

        self.graph = SimpleNamespace(
            history_runtime=(
                FakeHistoryRuntime(self)
            )
        )

    def snapshot(self) -> FakeSnapshot:
        return FakeSnapshot(
            production_id=self.production_id,
            session_id=self.session_id,
            timeline=FakeTimeline(
                production_id=(
                    self.production_id
                ),
                revision=(
                    self.timeline_revision
                ),
            ),
        )


class FakeRegistry:
    def __init__(
        self,
        session: FakeSession,
    ):
        self.session = session

    def get(
        self,
        production_id: str,
        *,
        session_id: str | None = None,
    ) -> FakeSession | None:
        if (
            production_id
            != self.session.production_id
        ):
            return None

        if (
            session_id is not None
            and session_id
            != self.session.session_id
        ):
            return None

        return self.session

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_count": 1,
        }


def main() -> None:
    production_id = (
        "221e4b01-5fb9-4b4a-a549-4fb32c455059"
    )
    session_id = "review-session-001"

    session = FakeSession(
        production_id,
        session_id,
    )

    service = ReviewWorkspaceApplicationService(
        product_workspace_service=object(),
        session_registry=FakeRegistry(
            session
        ),
    )

    required_interface_methods = {
        "move_clip",
        "trim_clip_start",
        "trim_clip_end",
        "split_clip",
        "duplicate_clip",
        "delete_clip",
        "close_gap",
        "undo_timeline",
        "redo_timeline",
    }

    interface_contract_valid = (
        required_interface_methods
        <= {
            name
            for name in dir(
                ReviewWorkspaceApplicationServiceInterface
            )
        }
    )

    revision_before_conflict = (
        session.timeline_revision
    )

    try:
        service.move_clip(
            production_id,
            session_id=session_id,
            clip_id="clip_1",
            new_start_time=1.0,
            expected_revision=99,
        )
        conflict_blocked = False
    except ReviewTimelineRevisionConflictError:
        conflict_blocked = True

    conflict_read_only = (
        session.timeline_revision
        == revision_before_conflict
    )

    move_result = service.move_clip(
        production_id,
        session_id=session_id,
        clip_id="clip_1",
        new_start_time=1.0,
        expected_revision=1,
    )

    move_valid = (
        move_result.operation
        == ReviewTimelineCommandType.MOVE_CLIP
        and move_result.previous_revision == 1
        and move_result.current_revision == 2
        and move_result.snapshot.timeline.revision
        == 2
    )

    service.trim_clip_start(
        production_id,
        session_id=session_id,
        clip_id="clip_1",
        new_start_time=0.5,
    )
    service.trim_clip_end(
        production_id,
        session_id=session_id,
        clip_id="clip_1",
        new_end_time=4.0,
    )
    service.split_clip(
        production_id,
        session_id=session_id,
        clip_id="clip_1",
        split_time=2.0,
    )
    service.duplicate_clip(
        production_id,
        session_id=session_id,
        clip_id="clip_1",
        new_start_time=5.0,
    )
    service.delete_clip(
        production_id,
        session_id=session_id,
        clip_id="clip_copy",
    )
    service.close_gap(
        production_id,
        session_id=session_id,
        track_id="track_video",
        gap_start=4.0,
        gap_end=5.0,
    )

    all_mutations_operational = (
        session.timeline_revision == 8
    )

    undo_result = service.undo_timeline(
        production_id,
        session_id=session_id,
        expected_revision=8,
    )

    redo_result = service.redo_timeline(
        production_id,
        session_id=session_id,
        expected_revision=9,
    )

    undo_redo_operational = (
        undo_result.operation
        == ReviewTimelineCommandType.UNDO
        and redo_result.operation
        == ReviewTimelineCommandType.REDO
        and session.timeline_revision == 10
    )

    failure_revision = (
        session.timeline_revision
    )
    session.graph.history_runtime.fail_next = True

    try:
        service.move_clip(
            production_id,
            session_id=session_id,
            clip_id="missing_clip",
            new_start_time=1.0,
        )
        failure_mapped = False
    except ReviewTimelineCommandOperationError:
        failure_mapped = True

    failure_read_only = (
        session.timeline_revision
        == failure_revision
    )

    isolated_result = move_result.clone()
    isolated_result.snapshot.timeline.revision = 999

    result_isolated = (
        move_result.snapshot.timeline.revision
        == 2
        and session.timeline_revision == 10
    )

    serialized = move_result.to_dict()

    serialization_valid = (
        serialized["operation"]
        == "move_clip"
        and serialized["previous_revision"] == 1
        and serialized["current_revision"] == 2
        and serialized["history"]["can_undo"]
        is True
    )

    service_summary = service.to_dict()

    summary_valid = (
        service_summary[
            "timeline_commands"
        ]["history_backed"]
        is True
        and service_summary[
            "timeline_commands"
        ]["expected_revision"]
        is True
        and len(
            service_summary[
                "timeline_commands"
            ]["operations"]
        )
        == 9
    )

    checks = {
        "interface_contract_valid": (
            interface_contract_valid
        ),
        "conflict_blocked": (
            conflict_blocked
        ),
        "conflict_read_only": (
            conflict_read_only
        ),
        "move_valid": move_valid,
        "all_mutations_operational": (
            all_mutations_operational
        ),
        "undo_redo_operational": (
            undo_redo_operational
        ),
        "failure_mapped": failure_mapped,
        "failure_read_only": (
            failure_read_only
        ),
        "result_isolated": result_isolated,
        "serialization_valid": (
            serialization_valid
        ),
        "summary_valid": summary_valid,
    }

    assert all(checks.values()), checks

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            {
                "checks": checks,
                "result": serialized,
                "service": service_summary,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "=== Review Timeline Mutation "
        "Application Service ==="
    )

    for name, value in checks.items():
        print(f"{name}: {value}")

    print(
        "output: "
        f"{OUTPUT_PATH.relative_to(BACKEND_ROOT)}"
    )
    print()
    print(
        "DONE: Review timeline mutation "
        "application service test completed."
    )


if __name__ == "__main__":
    main()