from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.product.adapters import (
    ProductPreviewSummary,
    ProductQualitySummary,
    ProductTimelineSummary,
    ProductWorkspaceSnapshot,
)
from app.product.contracts import (
    ProductProductionSnapshot,
    ProductProgress,
)
from app.review import (
    ReviewWorkspaceBuilder,
    build_review_runtime_graph,
    build_review_runtime_graph_from_snapshot,
    build_review_runtime_graph_from_workspace,
)


PRODUCTION_ID = (
    "221e4b01-5fb9-4b4a-a549-4fb32c455059"
)


def build_snapshot() -> ProductWorkspaceSnapshot:
    production = ProductProductionSnapshot(
        production_id=PRODUCTION_ID,
        name="Review graph test",
        status="completed",
        stage="review",
        progress=ProductProgress(
            stage="review",
            progress=100.0,
            message="Ready for review",
            status="completed",
        ),
    )

    timeline = ProductTimelineSummary(
        available=True,
        version="16.1.7",
        duration=8.0,
        track_count=2,
        clip_count=2,
        canvas={
            "width": 1080,
            "height": 1920,
            "fps": 30.0,
        },
        tracks=[
            {
                "track_id": "video_primary",
                "track_type": "video_primary",
                "name": "Video",
                "position": 0,
                "clips": [
                    {
                        "clip_id": "clip_1",
                        "track_id": "video_primary",
                        "clip_type": "video",
                        "start_time": 0.0,
                        "end_time": 4.0,
                        "source_start": 0.0,
                        "source_end": 4.0,
                        "source_duration": 20.0,
                    },
                    {
                        "clip_id": "clip_2",
                        "track_id": "video_primary",
                        "clip_type": "video",
                        "start_time": 4.0,
                        "end_time": 8.0,
                        "source_start": 4.0,
                        "source_end": 8.0,
                        "source_duration": 20.0,
                    },
                ],
            },
            {
                "track_id": "video_overlay",
                "track_type": "video_overlay",
                "name": "Overlay",
                "position": 1,
                "clips": [],
            },
        ],
        metadata={
            "source": "graph_test",
        },
    )

    preview = ProductPreviewSummary(
        available=True,
        video_path=(
            "storage/render/final.mp4"
        ),
        video_url="/media/final.mp4",
        duration=8.0,
        width=1080,
        height=1920,
        fps=30.0,
    )

    quality = ProductQualitySummary(
        available=True,
        approved=True,
        status="passed",
        quality_score=100.0,
    )

    return ProductWorkspaceSnapshot(
        production=production,
        timeline=timeline,
        preview=preview,
        quality=quality,
        metadata={
            "contract_version": "16.1.7.2",
        },
    )


def main() -> None:
    source = build_snapshot()
    source_before = deepcopy(
        source.to_dict()
    )

    graph = build_review_runtime_graph(
        source,
        maximum_history_size=25,
        maximum_clipboard_history_size=10,
    )

    shared_store = graph.shared_store
    production_ids_match = (
        graph.production_ids_match
    )

    graph.validate()

    source_unchanged = (
        source.to_dict() == source_before
    )

    timeline_snapshot = (
        graph.timeline_store.snapshot()
    )

    timeline_created = (
        timeline_snapshot.production_id
        == PRODUCTION_ID
        and timeline_snapshot.track_count == 2
        and timeline_snapshot.clip_count == 2
        and timeline_snapshot.width == 1080
        and timeline_snapshot.height == 1920
        and timeline_snapshot.fps == 30.0
    )

    preview_created = (
        graph.preview_runtime
        .source.production_id
        == PRODUCTION_ID
        and graph.preview_runtime
        .source.available
        and graph.preview_runtime
        .source.video_path
        == "storage/render/final.mp4"
    )

    selection_created = (
        graph.selection_runtime
        .catalog.production_id
        == PRODUCTION_ID
        and len(
            graph.selection_runtime
            .catalog.tracks
        )
        == 2
        and len(
            graph.selection_runtime
            .catalog.clips
        )
        == 2
    )

    limits_applied = (
        graph.history_runtime
        .state().maximum_history_size
        == 25
        and graph.clipboard_runtime
        .maximum_history_size
        == 10
    )

    trim_result = (
        graph.history_runtime.trim_clip_end(
            "clip_2",
            7.0,
        )
    )

    mutation_operational = (
        trim_result.success
        and graph.timeline_store.revision == 2
        and graph.timeline_store.snapshot()
        .get_clip("clip_2")
        .end_time
        == 7.0
        and graph.history_runtime.can_undo
    )

    isolated_snapshot = (
        graph.timeline_store.snapshot()
    )
    isolated_snapshot.tracks[0].clips[
        0
    ].start_time = 2.0

    store_snapshot_isolated = (
        graph.timeline_store.snapshot()
        .get_clip("clip_1")
        .start_time
        == 0.0
    )

    alias_graph = (
        build_review_runtime_graph_from_snapshot(
            source
        )
    )

    snapshot_alias_works = (
        alias_graph.shared_store
        and alias_graph.production_ids_match
    )

    review_workspace = (
        ReviewWorkspaceBuilder()
        .build_from_snapshot(source)
    )

    workspace_graph = (
        build_review_runtime_graph_from_workspace(
            review_workspace
        )
    )

    workspace_alias_works = (
        workspace_graph.shared_store
        and workspace_graph
        .production_ids_match
        and workspace_graph
        .timeline_store.snapshot()
        .clip_count
        == 2
        and workspace_graph
        .preview_runtime.source.available
    )

    output_payload = graph.to_dict()
    graph_summary_valid = (
        output_payload["shared_store"]
        and output_payload[
            "production_ids_match"
        ]
        and output_payload["components"]
        ["timeline_store"]
        == "TimelineRuntimeStore"
    )

    output = Path(
        "storage/demo_outputs/"
        "review_runtime_graph_factory.json"
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
        "=== Review Runtime Graph Factory ==="
    )
    print("shared_store:", shared_store)
    print(
        "production_ids_match:",
        production_ids_match,
    )
    print(
        "source_unchanged:",
        source_unchanged,
    )
    print(
        "timeline_created:",
        timeline_created,
    )
    print(
        "preview_created:",
        preview_created,
    )
    print(
        "selection_created:",
        selection_created,
    )
    print(
        "limits_applied:",
        limits_applied,
    )
    print(
        "mutation_operational:",
        mutation_operational,
    )
    print(
        "store_snapshot_isolated:",
        store_snapshot_isolated,
    )
    print(
        "snapshot_alias_works:",
        snapshot_alias_works,
    )
    print(
        "workspace_alias_works:",
        workspace_alias_works,
    )
    print(
        "graph_summary_valid:",
        graph_summary_valid,
    )
    print("output:", output)

    assert shared_store
    assert production_ids_match
    assert source_unchanged
    assert timeline_created
    assert preview_created
    assert selection_created
    assert limits_applied
    assert mutation_operational
    assert store_snapshot_isolated
    assert snapshot_alias_works
    assert workspace_alias_works
    assert graph_summary_valid

    print()
    print(
        "DONE: Review runtime graph "
        "factory test completed."
    )


if __name__ == "__main__":
    main()