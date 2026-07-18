from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.review.suggestions import (
    AISuggestionLifecycleRuntime,
    AISuggestionStatus,
    build_ai_suggestion_lifecycle_runtime,
    build_ai_suggestion_lifecycle_runtime_from_store,
    build_ai_suggestion_lifecycle_store,
    build_ai_suggestion_read_model,
)


def main() -> None:
    raw_suggestions = [
        {
            "id": "suggestion-apply",
            "kind": "hook",
            "title": "Tăng tốc hook",
            "description": (
                "Rút ngắn clip mở đầu."
            ),
            "timeline_revision": 7,
            "target": {
                "clip_id": "clip-1",
            },
            "command": {
                "operation": "trim_clip_end",
                "arguments": {
                    "clip_id": "clip-1",
                    "new_end_time": 2.5,
                },
            },
        },
        {
            "id": "suggestion-dismiss",
            "kind": "music",
            "title": "Đổi nhạc nền",
            "description": (
                "Thử nhạc nền có nhịp nhanh hơn."
            ),
            "timeline_revision": 7,
        },
        {
            "id": "suggestion-stale",
            "kind": "subtitle",
            "title": "Rút ngắn phụ đề",
            "description": (
                "Đề xuất thuộc timeline cũ."
            ),
            "timeline_revision": 6,
            "command": "trim_subtitle",
        },
    ]
    source_before = json.dumps(
        raw_suggestions,
        sort_keys=True,
        ensure_ascii=False,
    )
    initial_model = (
        build_ai_suggestion_read_model(
            production_id="production-1",
            timeline_revision=7,
            raw_suggestions=raw_suggestions,
        )
    )

    store_events = []
    store = build_ai_suggestion_lifecycle_store(
        initial_model
    )
    store.subscribe(
        lambda change: store_events.append(
            change.to_dict()
        )
    )
    store.subscribe(
        lambda change: (_ for _ in ()).throw(
            RuntimeError("isolated subscriber")
        )
    )
    runtime_events = []
    runtime = (
        build_ai_suggestion_lifecycle_runtime_from_store(
            store,
            event_callback=(
                lambda event: runtime_events.append(
                    event.to_dict()
                )
            ),
        )
    )

    initial_snapshot = runtime.snapshot()
    isolated_snapshot = runtime.snapshot()
    isolated_snapshot.read_model.metadata[
        "changed_outside"
    ] = True

    select_result = runtime.select(
        "suggestion-apply",
        expected_revision=1,
    )
    revision_after_select = runtime.revision
    change_count_before_prepare = len(
        store.changes
    )
    event_count_before_prepare = len(
        runtime.events
    )
    preparation = runtime.prepare_apply(
        "suggestion-apply",
        active_timeline_revision=7,
        expected_revision=revision_after_select,
    )
    prepare_read_only = (
        runtime.revision
        == revision_after_select
        and len(store.changes)
        == change_count_before_prepare
        and len(runtime.events)
        == event_count_before_prepare
    )

    stale_prepare = runtime.prepare_apply(
        "suggestion-stale",
        active_timeline_revision=7,
        expected_revision=runtime.revision,
    )
    failure_revision = runtime.revision
    failure_changes = len(store.changes)
    failure_events = len(runtime.events)
    conflict_result = runtime.dismiss(
        "suggestion-dismiss",
        expected_revision=1,
    )
    conflict_read_only = (
        runtime.revision == failure_revision
        and len(store.changes)
        == failure_changes
        and len(runtime.events)
        == failure_events
    )

    dismiss_result = runtime.dismiss(
        "suggestion-dismiss",
        expected_revision=runtime.revision,
    )
    revision_before_apply = runtime.revision
    apply_result = runtime.mark_applied(
        "suggestion-apply",
        source_timeline_revision=7,
        resulting_timeline_revision=8,
        expected_revision=revision_before_apply,
    )
    after_apply = runtime.snapshot()

    regenerated_model = (
        build_ai_suggestion_read_model(
            production_id="production-1",
            timeline_revision=8,
            raw_suggestions=[
                {
                    "id": "suggestion-fresh",
                    "kind": "broll",
                    "description": (
                        "Thêm B-roll sản phẩm."
                    ),
                    "timeline_revision": 8,
                    "command": "insert_broll",
                }
            ],
        )
    )
    regenerate_result = runtime.regenerate(
        regenerated_model,
        expected_revision=runtime.revision,
    )
    synchronize_result = (
        runtime.synchronize_timeline_revision(
            9,
            expected_revision=runtime.revision,
        )
    )
    synchronized = runtime.snapshot()

    wrong_production = (
        build_ai_suggestion_read_model(
            production_id="production-2",
            timeline_revision=9,
        )
    )
    before_wrong_revision = runtime.revision
    before_wrong_read_model = (
        runtime.snapshot().read_model.to_dict()
    )
    before_wrong_changes = len(store.changes)
    before_wrong_events = len(runtime.events)
    wrong_regenerate = runtime.regenerate(
        wrong_production,
        expected_revision=runtime.revision,
    )
    wrong_regenerate_read_only = (
        runtime.revision == before_wrong_revision
        and runtime.snapshot().read_model.to_dict()
        == before_wrong_read_model
        and len(store.changes)
        == before_wrong_changes
        and len(runtime.events)
        == before_wrong_events
    )

    reset_result = runtime.reset(
        expected_revision=runtime.revision,
    )
    reset_snapshot = runtime.snapshot()

    changes_copy = store.changes
    changes_copy[0].metadata[
        "changed_outside"
    ] = True
    events_copy = runtime.events
    events_copy[0].metadata[
        "changed_outside"
    ] = True

    legacy_runtime = (
        build_ai_suggestion_lifecycle_runtime(
            initial_model
        )
    )

    checks = {
        "initial_snapshot_valid": (
            initial_snapshot.lifecycle_revision
            == 1
            and initial_snapshot.timeline_revision
            == 7
            and initial_snapshot.read_model.count
            == 3
        ),
        "snapshot_isolated": (
            "changed_outside"
            not in runtime.snapshot()
            .read_model.metadata
        ),
        "select_single_commit": (
            select_result.success
            and select_result.event is not None
            and revision_after_select == 2
            and len(store_events) >= 1
        ),
        "prepare_apply_read_only": (
            preparation.success
            and preparation.command is not None
            and preparation.command.operation
            == "trim_clip_end"
            and prepare_read_only
        ),
        "stale_prepare_blocked": (
            not stale_prepare.success
            and "actionable"
            in (stale_prepare.error or "")
        ),
        "revision_conflict_read_only": (
            not conflict_result.success
            and "conflict"
            in (conflict_result.error or "")
            and conflict_read_only
        ),
        "dismiss_single_commit": (
            dismiss_result.success
            and dismiss_result.snapshot
            .read_model.get("suggestion-dismiss")
            .status
            == AISuggestionStatus.DISMISSED
        ),
        "apply_single_commit": (
            apply_result.success
            and apply_result.event is not None
            and apply_result.event.event_type.value
            == "suggestion_applied"
            and after_apply.lifecycle_revision
            == revision_before_apply + 1
            and after_apply.timeline_revision == 8
            and after_apply.read_model
            .get("suggestion-apply").status
            == AISuggestionStatus.APPLIED
        ),
        "regenerate_atomic": (
            regenerate_result.success
            and regenerate_result.snapshot
            .read_model.count == 1
            and regenerate_result.snapshot
            .read_model.get("suggestion-fresh")
            is not None
        ),
        "timeline_sync_marks_stale": (
            synchronize_result.success
            and synchronized.timeline_revision == 9
            and synchronized.read_model
            .get("suggestion-fresh").status
            == AISuggestionStatus.STALE
        ),
        "wrong_production_read_only": (
            not wrong_regenerate.success
            and wrong_regenerate_read_only
        ),
        "reset_to_initial": (
            reset_result.success
            and reset_snapshot.read_model
            .timeline_revision == 7
            and reset_snapshot.read_model.count == 3
        ),
        "store_change_log_isolated": (
            "changed_outside"
            not in store.changes[0].metadata
        ),
        "runtime_events_isolated": (
            "changed_outside"
            not in runtime.events[0].metadata
        ),
        "callback_failure_isolated": (
            len(store_events)
            == len(store.changes)
            and len(runtime_events)
            == len(runtime.events)
        ),
        "source_unchanged": (
            json.dumps(
                raw_suggestions,
                sort_keys=True,
                ensure_ascii=False,
            )
            == source_before
        ),
        "legacy_factory_works": (
            isinstance(
                legacy_runtime,
                AISuggestionLifecycleRuntime,
            )
            and legacy_runtime.revision == 1
        ),
        "serialization_valid": (
            json.loads(
                json.dumps(
                    reset_result.to_dict(),
                    ensure_ascii=False,
                )
            )["success"]
        ),
        "no_timeline_mutation_api": (
            not hasattr(runtime, "move_clip")
            and not hasattr(runtime, "trim_clip_end")
            and not hasattr(runtime, "delete_clip")
        ),
    }

    assert all(checks.values()), checks

    output = Path(
        "storage/demo_outputs/"
        "review_ai_suggestion_lifecycle_runtime.json"
    )
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output.write_text(
        json.dumps(
            reset_result.to_dict(),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        "=== AI Suggestion Lifecycle Store "
        "& Runtime ==="
    )
    for name, value in checks.items():
        print(f"{name}: {value}")
    print(f"output: {output}")
    print(
        "\nDONE: AI suggestion lifecycle store "
        "and runtime test completed."
    )


if __name__ == "__main__":
    main()
