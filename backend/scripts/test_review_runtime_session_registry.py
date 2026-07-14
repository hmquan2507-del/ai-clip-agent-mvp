from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.review import (
    InMemoryReviewRuntimeSessionRegistry,
    ReviewRuntimeSessionRegistryInterface,
    build_in_memory_review_runtime_session_registry,
    build_review_runtime_session,
)
from test_review_runtime_state_synchronization import (
    build_snapshot as build_product_snapshot,
)


@dataclass
class MutableClock:
    value: datetime

    def __call__(self) -> datetime:
        return self.value

    def advance(
        self,
        seconds: float,
    ) -> None:
        self.value = (
            self.value
            + timedelta(seconds=seconds)
        )


def build_source(
    production_id: str,
):
    source = build_product_snapshot()
    source.production.production_id = (
        production_id
    )
    source.production.name = production_id
    return source


def main() -> None:
    clock = MutableClock(
        datetime(
            2026,
            7,
            14,
            8,
            0,
            tzinfo=timezone.utc,
        )
    )

    registry = (
        build_in_memory_review_runtime_session_registry(
            ttl_seconds=10.0,
            clock=clock,
        )
    )

    interface_contract = (
        isinstance(
            registry,
            ReviewRuntimeSessionRegistryInterface,
        )
        and isinstance(
            registry,
            InMemoryReviewRuntimeSessionRegistry,
        )
    )

    source_one = build_source(
        "production-one"
    )
    source_one_before = deepcopy(
        source_one.to_dict()
    )

    first_session = build_review_runtime_session(
        source_one
    )
    registered = registry.register(
        first_session,
        metadata={
            "owner": {
                "type": "test",
            },
        },
    )

    registration_works = (
        registered is first_session
        and registry.count == 1
        and registry.production_ids
        == ("production-one",)
        and registry.contains(
            "production-one",
            session_id=(
                first_session.session_id
            ),
        )
    )

    wrong_session_id_blocked = (
        registry.get(
            "production-one",
            session_id="wrong-session-id",
        )
        is None
        and registry.count == 1
    )

    entry_payload = registry.entries[0]
    entry_payload.metadata["owner"][
        "type"
    ] = "changed-outside"

    entry_isolated = (
        registry.entries[0].metadata[
            "owner"
        ]["type"]
        == "test"
    )

    duplicate_session = (
        build_review_runtime_session(
            source_one
        )
    )
    duplicate_blocked = False

    try:
        registry.register(
            duplicate_session
        )
    except ValueError:
        duplicate_blocked = (
            registry.get(
                "production-one",
                touch=False,
            )
            is first_session
            and not duplicate_session.closed
        )

    replacement_session = (
        build_review_runtime_session(
            source_one
        )
    )
    registry.register(
        replacement_session,
        replace_existing=True,
    )

    replace_closes_previous = (
        first_session.closed
        and registry.get(
            "production-one",
            touch=False,
        )
        is replacement_session
        and not replacement_session.closed
        and registry.count == 1
    )

    source_two = build_source(
        "production-two"
    )
    second_session = (
        build_review_runtime_session(
            source_two
        )
    )
    registry.register(second_session)

    production_isolation = (
        registry.count == 2
        and registry.get(
            "production-one",
            touch=False,
        )
        is replacement_session
        and registry.get(
            "production-two",
            touch=False,
        )
        is second_session
        and replacement_session.graph
        .timeline_store
        is not second_session.graph
        .timeline_store
    )

    def access_replacement(
        _: int,
    ) -> bool:
        return (
            registry.get(
                "production-one"
            )
            is replacement_session
        )

    with ThreadPoolExecutor(
        max_workers=8
    ) as executor:
        concurrent_results = list(
            executor.map(
                access_replacement,
                range(200),
            )
        )

    thread_safe_access = (
        all(concurrent_results)
        and registry.count == 2
        and next(
            entry
            for entry in registry.entries
            if entry.production_id
            == "production-one"
        ).access_count
        >= 200
    )

    clock.advance(5.0)
    touched_session = registry.get(
        "production-one"
    )
    clock.advance(6.0)
    removed_expired = (
        registry.cleanup_expired()
    )

    ttl_cleanup_works = (
        touched_session
        is replacement_session
        and second_session.session_id
        in removed_expired
        and second_session.closed
        and registry.count == 1
        and registry.get(
            "production-one",
            touch=False,
        )
        is replacement_session
    )

    wrong_remove_blocked = (
        registry.remove(
            "production-one",
            session_id="wrong-session-id",
        )
        is None
        and registry.count == 1
        and not replacement_session.closed
    )

    removed_without_close = registry.remove(
        "production-one",
        session_id=(
            replacement_session.session_id
        ),
        close_session=False,
    )

    optional_close_works = (
        removed_without_close
        is replacement_session
        and registry.count == 0
        and not replacement_session.closed
    )

    registry.register(replacement_session)
    cleared_ids = registry.clear()

    clear_closes_sessions = (
        replacement_session.session_id
        in cleared_ids
        and replacement_session.closed
        and registry.count == 0
        and registry.production_ids == ()
    )

    closed_registration_blocked = False

    try:
        registry.register(
            replacement_session
        )
    except ValueError:
        closed_registration_blocked = True

    duplicate_session.close()

    source_unchanged = (
        source_one.to_dict()
        == source_one_before
    )

    registry_payload = registry.to_dict()
    serialization_valid = (
        registry_payload["registry"]
        == (
            "InMemoryReviewRuntimeSessionRegistry"
        )
        and registry_payload["ttl_seconds"]
        == 10.0
        and registry_payload["session_count"]
        == 0
        and registry_payload["entries"] == []
    )

    output_payload = {
        "registry": registry_payload,
        "checks": {
            "interface_contract": (
                interface_contract
            ),
            "registration_works": (
                registration_works
            ),
            "wrong_session_id_blocked": (
                wrong_session_id_blocked
            ),
            "entry_isolated": entry_isolated,
            "duplicate_blocked": (
                duplicate_blocked
            ),
            "replace_closes_previous": (
                replace_closes_previous
            ),
            "production_isolation": (
                production_isolation
            ),
            "thread_safe_access": (
                thread_safe_access
            ),
            "ttl_cleanup_works": (
                ttl_cleanup_works
            ),
            "wrong_remove_blocked": (
                wrong_remove_blocked
            ),
            "optional_close_works": (
                optional_close_works
            ),
            "clear_closes_sessions": (
                clear_closes_sessions
            ),
            "closed_registration_blocked": (
                closed_registration_blocked
            ),
            "source_unchanged": (
                source_unchanged
            ),
            "serialization_valid": (
                serialization_valid
            ),
        },
    }

    output = Path(
        "storage/demo_outputs/"
        "review_runtime_session_registry.json"
    )
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output.write_text(
        json.dumps(
            output_payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        "=== Review Runtime Session Registry ==="
    )

    checks = output_payload["checks"]
    for name, value in checks.items():
        print(f"{name}:", value)

    print("output:", output)

    assert all(checks.values())

    print()
    print(
        "DONE: Review runtime session "
        "registry test completed."
    )


if __name__ == "__main__":
    main()