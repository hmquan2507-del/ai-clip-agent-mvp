from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient


sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.product import (
    build_in_memory_product_workspace_service,
)
from app.product.api.dependencies import (
    get_product_workspace_service,
)
from app.review.api.dependencies import (
    get_review_runtime_session_registry,
)
from app.review.api.router import (
    router as review_workspace_router,
)
from test_review_workspace_application_service import (
    register_workspace,
)


PRODUCTION_A = "221e4b01-5fb9-4b4a-a549-4fb32c455059"
PRODUCTION_B = "331e4b01-5fb9-4b4a-a549-4fb32c455059"


def review_path(production_id: str) -> str:
    return (
        f"/api/v1/productions/"
        f"{production_id}/review"
    )


def build_test_app() -> FastAPI:
    application = FastAPI()
    application.include_router(
        review_workspace_router,
        prefix="/api/v1",
    )
    return application


def snapshot_clip_count(
    snapshot: dict[str, Any],
) -> int:
    return sum(
        len(track.get("clips", []))
        for track in snapshot["timeline"].get(
            "tracks",
            [],
        )
    )


def request_delete(
    client: TestClient,
    path: str,
    payload: dict[str, Any],
):
    return client.request(
        "DELETE",
        path,
        json=payload,
    )


def main() -> None:
    product_service, loader = (
        build_in_memory_product_workspace_service(
            ttl_seconds=60,
        )
    )
    source_a = register_workspace(
        loader,
        PRODUCTION_A,
    )
    source_b = register_workspace(
        loader,
        PRODUCTION_B,
    )
    source_a_before = deepcopy(source_a)
    source_b_before = deepcopy(source_b)

    registry = get_review_runtime_session_registry()
    registry.clear(close_sessions=True)

    application = build_test_app()
    application.dependency_overrides[
        get_product_workspace_service
    ] = lambda: product_service

    try:
        with TestClient(application) as client:
            openapi = client.get(
                "/openapi.json"
            ).json()
            route_base = review_path(
                "{production_id}"
            )
            expected_routes = {
                f"{route_base}/clipboard/copy": {"post"},
                f"{route_base}/clipboard/cut": {"post"},
                f"{route_base}/clipboard/paste": {"post"},
                (
                    f"{route_base}/clipboard/"
                    "history/restore"
                ): {"post"},
                f"{route_base}/clipboard": {"delete"},
                (
                    f"{route_base}/clipboard/history"
                ): {"delete"},
            }
            openapi_routes_complete = all(
                path in openapi["paths"]
                and methods.issubset(
                    openapi["paths"][path].keys()
                )
                for path, methods in expected_routes.items()
            )

            open_a = client.post(
                f"{review_path(PRODUCTION_A)}/session",
                json={},
            )
            open_b = client.post(
                f"{review_path(PRODUCTION_B)}/session",
                json={},
            )
            session_a_id = open_a.json()["session_id"]
            session_b_id = open_b.json()["session_id"]
            session_a = registry.get(
                PRODUCTION_A,
                session_id=session_a_id,
            )
            session_b = registry.get(
                PRODUCTION_B,
                session_id=session_b_id,
            )

            initial_a = session_a.snapshot()
            initial_b = session_b.snapshot()
            initial_timeline = (
                session_a.graph.timeline_store.snapshot()
            )
            source_track = next(
                track
                for track in initial_timeline.tracks
                if not track.locked and track.clips
            )
            source_clip = source_track.clips[0]
            source_clip_id = source_clip.clip_id
            paste_time = (
                float(initial_timeline.duration) + 1.0
            )
            initial_clip_count = sum(
                len(track.clips)
                for track in initial_timeline.tracks
            )
            initial_change_count = len(
                session_a.graph.timeline_store.changes
            )

            copy_response = client.post(
                (
                    f"{review_path(PRODUCTION_A)}"
                    "/clipboard/copy"
                ),
                json={
                    "session_id": session_a_id,
                    "clip_ids": [source_clip_id],
                    "expected_revision": (
                        initial_a.timeline.revision
                    ),
                },
            )
            copy_payload = copy_response.json()
            copy_no_timeline_change = (
                copy_response.status_code == 200
                and copy_payload["operation"] == "copy"
                and copy_payload["previous_revision"]
                == initial_a.timeline.revision
                and copy_payload["current_revision"]
                == initial_a.timeline.revision
                and copy_payload["clipboard"]["content"][
                    "item_count"
                ]
                == 1
                and copy_payload["snapshot"]["history"][
                    "undo_count"
                ]
                == 0
                and len(
                    session_a.graph.timeline_store.changes
                )
                == initial_change_count
            )

            paste_response = client.post(
                (
                    f"{review_path(PRODUCTION_A)}"
                    "/clipboard/paste"
                ),
                json={
                    "session_id": session_a_id,
                    "at_time": paste_time,
                    "expected_revision": (
                        copy_payload["current_revision"]
                    ),
                },
            )
            paste_payload = paste_response.json()
            paste_atomic = (
                paste_response.status_code == 200
                and paste_payload["operation"] == "paste"
                and paste_payload["current_revision"]
                == paste_payload["previous_revision"] + 1
                and snapshot_clip_count(
                    paste_payload["snapshot"]
                )
                == initial_clip_count + 1
                and paste_payload["snapshot"]["history"][
                    "undo_count"
                ]
                == 1
                and paste_payload["timeline_history"][
                    "success"
                ]
                is True
            )

            undo_paste_response = client.post(
                (
                    f"{review_path(PRODUCTION_A)}"
                    "/timeline/undo"
                ),
                json={
                    "session_id": session_a_id,
                    "expected_revision": (
                        paste_payload["current_revision"]
                    ),
                },
            )
            undo_paste_payload = (
                undo_paste_response.json()
            )
            undo_paste = (
                undo_paste_response.status_code == 200
                and snapshot_clip_count(
                    undo_paste_payload["snapshot"]
                )
                == initial_clip_count
                and undo_paste_payload["snapshot"][
                    "clipboard"
                ]["content"]["item_count"]
                == 1
            )

            redo_paste_response = client.post(
                (
                    f"{review_path(PRODUCTION_A)}"
                    "/timeline/redo"
                ),
                json={
                    "session_id": session_a_id,
                    "expected_revision": (
                        undo_paste_payload["metadata"]
                        ["current_revision"]
                    ),
                },
            )
            redo_paste_payload = (
                redo_paste_response.json()
            )
            redo_paste = (
                redo_paste_response.status_code == 200
                and snapshot_clip_count(
                    redo_paste_payload["snapshot"]
                )
                == initial_clip_count + 1
            )

            cut_response = client.post(
                (
                    f"{review_path(PRODUCTION_A)}"
                    "/clipboard/cut"
                ),
                json={
                    "session_id": session_a_id,
                    "clip_ids": [source_clip_id],
                    "expected_revision": (
                        redo_paste_payload["metadata"]
                        ["current_revision"]
                    ),
                },
            )
            cut_payload = cut_response.json()
            cut_atomic = (
                cut_response.status_code == 200
                and cut_payload["operation"] == "cut"
                and snapshot_clip_count(
                    cut_payload["snapshot"]
                )
                == initial_clip_count
                and cut_payload["clipboard"]["content"][
                    "action"
                ]
                == "cut"
                and cut_payload["timeline_history"][
                    "success"
                ]
                is True
            )

            undo_cut_response = client.post(
                (
                    f"{review_path(PRODUCTION_A)}"
                    "/timeline/undo"
                ),
                json={
                    "session_id": session_a_id,
                    "expected_revision": (
                        cut_payload["current_revision"]
                    ),
                },
            )
            undo_cut_payload = undo_cut_response.json()
            undo_cut = (
                undo_cut_response.status_code == 200
                and snapshot_clip_count(
                    undo_cut_payload["snapshot"]
                )
                == initial_clip_count + 1
            )

            history_entries = cut_payload[
                "clipboard"
            ]["history"]
            first_history_entry = history_entries[0]
            revision_after_undo_cut = (
                undo_cut_payload["metadata"]
                ["current_revision"]
            )
            restore_response = client.post(
                (
                    f"{review_path(PRODUCTION_A)}"
                    "/clipboard/history/restore"
                ),
                json={
                    "session_id": session_a_id,
                    "entry_id": first_history_entry[
                        "entry_id"
                    ],
                    "expected_revision": (
                        revision_after_undo_cut
                    ),
                },
            )
            restore_payload = restore_response.json()
            restore_history_works = (
                restore_response.status_code == 200
                and restore_payload["operation"]
                == "restore_history"
                and restore_payload["current_revision"]
                == revision_after_undo_cut
                and restore_payload["clipboard"]["content"][
                    "clipboard_id"
                ]
                == first_history_entry["content"][
                    "clipboard_id"
                ]
            )

            clear_history_response = request_delete(
                client,
                (
                    f"{review_path(PRODUCTION_A)}"
                    "/clipboard/history"
                ),
                {
                    "session_id": session_a_id,
                    "expected_revision": (
                        revision_after_undo_cut
                    ),
                },
            )
            clear_history_payload = (
                clear_history_response.json()
            )
            clear_history_preserves_content = (
                clear_history_response.status_code == 200
                and clear_history_payload["clipboard"][
                    "history_state"
                ]["entry_count"]
                == 0
                and clear_history_payload["clipboard"][
                    "content"
                ]["available"]
                is True
                and clear_history_payload["current_revision"]
                == revision_after_undo_cut
            )

            clear_content_response = request_delete(
                client,
                (
                    f"{review_path(PRODUCTION_A)}"
                    "/clipboard"
                ),
                {
                    "session_id": session_a_id,
                    "expected_revision": (
                        revision_after_undo_cut
                    ),
                },
            )
            clear_content_payload = (
                clear_content_response.json()
            )
            clear_content_works = (
                clear_content_response.status_code == 200
                and clear_content_payload["clipboard"][
                    "content"
                ]["available"]
                is False
                and clear_content_payload["current_revision"]
                == revision_after_undo_cut
            )

            state_before_failures = (
                session_a.snapshot()
            )
            change_count_before_failures = len(
                session_a.graph.timeline_store.changes
            )
            conflict_response = client.post(
                (
                    f"{review_path(PRODUCTION_A)}"
                    "/clipboard/copy"
                ),
                json={
                    "session_id": session_a_id,
                    "clip_ids": [source_clip_id],
                    "expected_revision": 999999,
                },
            )
            empty_paste_response = client.post(
                (
                    f"{review_path(PRODUCTION_A)}"
                    "/clipboard/paste"
                ),
                json={
                    "session_id": session_a_id,
                    "at_time": paste_time,
                    "expected_revision": (
                        revision_after_undo_cut
                    ),
                },
            )
            state_after_failures = session_a.snapshot()
            failures_are_read_only = (
                conflict_response.status_code == 409
                and conflict_response.json()["error"]["code"]
                == "review_session_conflict"
                and empty_paste_response.status_code == 409
                and empty_paste_response.json()["error"]["code"]
                == "review_clipboard_command_failed"
                and state_after_failures.timeline.to_dict()
                == state_before_failures.timeline.to_dict()
                and state_after_failures.clipboard_state.to_dict()
                == state_before_failures.clipboard_state.to_dict()
                and state_after_failures.clipboard_content.to_dict()
                == state_before_failures.clipboard_content.to_dict()
                and len(session_a.graph.timeline_store.changes)
                == change_count_before_failures
            )

            recopy_response = client.post(
                (
                    f"{review_path(PRODUCTION_A)}"
                    "/clipboard/copy"
                ),
                json={
                    "session_id": session_a_id,
                    "clip_ids": [source_clip_id],
                    "expected_revision": (
                        revision_after_undo_cut
                    ),
                },
            )
            revision_before_invalid_mapping = (
                session_a.snapshot().timeline.revision
            )
            change_count_before_invalid_mapping = len(
                session_a.graph.timeline_store.changes
            )
            invalid_mapping_response = client.post(
                (
                    f"{review_path(PRODUCTION_A)}"
                    "/clipboard/paste"
                ),
                json={
                    "session_id": session_a_id,
                    "at_time": paste_time + 20.0,
                    "target_track_id": "missing_track",
                    "expected_revision": (
                        revision_before_invalid_mapping
                    ),
                },
            )
            invalid_mapping_atomic = (
                recopy_response.status_code == 200
                and invalid_mapping_response.status_code == 409
                and session_a.snapshot().timeline.revision
                == revision_before_invalid_mapping
                and len(session_a.graph.timeline_store.changes)
                == change_count_before_invalid_mapping
            )

            current_b = session_b.snapshot()
            production_isolation = (
                current_b.timeline.to_dict()
                == initial_b.timeline.to_dict()
                and current_b.history_state.to_dict()
                == initial_b.history_state.to_dict()
                and current_b.clipboard_state.to_dict()
                == initial_b.clipboard_state.to_dict()
                and current_b.clipboard_content.to_dict()
                == initial_b.clipboard_content.to_dict()
            )

            copy_payload["snapshot"]["metadata"][
                "client_mutation"
            ] = True
            copy_payload["clipboard"]["content"][
                "items"
            ].clear()
            response_payload_isolated = (
                "client_mutation"
                not in session_a.snapshot().metadata
                and session_a.graph.clipboard_runtime
                .content.item_count
                == 1
            )

            final_change_count_valid = (
                len(session_a.graph.timeline_store.changes)
                == initial_change_count + 5
            )
            source_unchanged = (
                source_a == source_a_before
                and source_b == source_b_before
            )

            close_a = request_delete(
                client,
                f"{review_path(PRODUCTION_A)}/session",
                {"session_id": session_a_id},
            )
            close_b = request_delete(
                client,
                f"{review_path(PRODUCTION_B)}/session",
                {"session_id": session_b_id},
            )
            lifecycle_cleanup_complete = (
                close_a.status_code == 200
                and close_b.status_code == 200
                and registry.count == 0
                and session_a.closed
                and session_b.closed
            )

            checks = {
                "openapi_routes_complete": openapi_routes_complete,
                "sessions_opened": (
                    open_a.status_code == 200
                    and open_b.status_code == 200
                ),
                "copy_no_timeline_change": copy_no_timeline_change,
                "paste_atomic": paste_atomic,
                "undo_paste": undo_paste,
                "redo_paste": redo_paste,
                "cut_atomic": cut_atomic,
                "undo_cut": undo_cut,
                "restore_history_works": restore_history_works,
                "clear_history_preserves_content": (
                    clear_history_preserves_content
                ),
                "clear_content_works": clear_content_works,
                "failures_are_read_only": failures_are_read_only,
                "invalid_mapping_atomic": invalid_mapping_atomic,
                "production_isolation": production_isolation,
                "response_payload_isolated": response_payload_isolated,
                "final_change_count_valid": final_change_count_valid,
                "source_unchanged": source_unchanged,
                "lifecycle_cleanup_complete": lifecycle_cleanup_complete,
            }

            assert all(checks.values()), checks

            print("=== Review Timeline Clipboard API Integration ===")
            for name, passed in checks.items():
                print(f"{name}: {passed}")

            output_path = Path(
                "storage/demo_outputs/"
                "review_timeline_clipboard_api_integration.json"
            )
            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            output_path.write_text(
                json.dumps(
                    {
                        "checks": checks,
                        "copy": copy_payload,
                        "paste": paste_payload,
                        "cut": cut_payload,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            print(f"output: {output_path}")
            print(
                "\nDONE: Review timeline clipboard "
                "API integration test completed."
            )
    finally:
        registry.clear(close_sessions=True)
        application.dependency_overrides.clear()


if __name__ == "__main__":
    main()
