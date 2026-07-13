from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).resolve().parents[1]
    )
)

from app.review.editing import (
    EditableTimeline,
    build_timeline_runtime_store,
)


def main() -> None:
    timeline = EditableTimeline(
        production_id=(
            "221e4b01-5fb9-4b4a-a549-4fb32c455059"
        ),
        duration=10.0,
        fps=30.0,
    )

    store = build_timeline_runtime_store(
        timeline
    )

    first_snapshot = store.snapshot()
    changed = first_snapshot.clone()
    changed.mark_dirty()

    replace_result = store.replace(
        changed,
        reason="test_change",
    )

    reset_result = store.reset()

    print(
        "=== Timeline Runtime Store ==="
    )
    print(
        "initial_revision:",
        first_snapshot.revision,
    )
    print(
        "replace_success:",
        replace_result.success,
    )
    print(
        "changed_revision:",
        replace_result.timeline.revision,
    )
    print(
        "reset_success:",
        reset_result.success,
    )
    print(
        "reset_revision:",
        reset_result.timeline.revision,
    )
    print(
        "change_count:",
        len(store.changes),
    )

    assert first_snapshot.revision == 1
    assert replace_result.success is True
    assert replace_result.timeline.revision == 2

    assert reset_result.success is True
    assert reset_result.timeline.revision == 1

    assert len(store.changes) == 2

    # Snapshot phải là clone.
    reset_result.timeline.mark_dirty()

    assert store.snapshot().revision == 1

    exposed_changes = store.changes
    exposed_changes[0].metadata[
        "tampered"
    ] = True

    assert (
        "tampered"
        not in store.changes[0].metadata
    )

    print(
        "change_log_isolated:",
        True,
    )

    print(
        "\nDONE: Timeline runtime "
        "store test completed."
    )


if __name__ == "__main__":
    main()