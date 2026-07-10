from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.render.execution import (
    build_render_architecture_runtime,
    build_render_asset_preloader,
)
from scripts.test_render_architecture_runtime import (
    load_execution_timeline,
)


def main() -> None:
    input_path = Path(
        "storage/demo_outputs/"
        "execution_timeline.json"
    )

    if not input_path.exists():
        raise RuntimeError(
            "Run test_timeline_compiler_runtime.py first."
        )

    execution = load_execution_timeline(
        input_path
    )

    context = (
        build_render_architecture_runtime()
        .build_context(
            execution_timeline=execution,
            storage_root=(
                "storage/render_preloader_test"
            ),
        )
    )

    preloader = build_render_asset_preloader()

    result = preloader.preload(context)

    output_path = Path(
        "storage/demo_outputs/"
        "render_asset_preload_result.json"
    )

    output_path.write_text(
        json.dumps(
            result.to_dict(),
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print("=== Render Asset Preloader ===")
    print("success:", result.success)
    print(
        "prepared_input_count:",
        len(result.prepared_inputs),
    )
    print(
        "issue_count:",
        len(result.issues),
    )
    print(
        "manifest_path:",
        result.manifest_path,
    )
    print(
        "linked_count:",
        sum(
            1
            for item in result.prepared_inputs
            if item.linked
        ),
    )
    print(
        "copied_count:",
        sum(
            1
            for item in result.prepared_inputs
            if item.copied
        ),
    )
    print(
        "reused_count:",
        sum(
            1
            for item in result.prepared_inputs
            if item.reused
        ),
    )
    print("output:", output_path)

    assert result.success is True
    assert len(result.issues) == 0
    assert len(result.prepared_inputs) == len(
        execution.inputs
    )

    for item in result.prepared_inputs:
        prepared_path = Path(
            item.prepared_path
        )

        assert prepared_path.exists()
        assert prepared_path.is_file()
        assert prepared_path.stat().st_size > 0
        assert item.checksum
        assert item.file_size
        assert item.duration is not None
        assert item.duration > 0

    second_result = preloader.preload(
        context
    )

    assert second_result.success is True
    assert all(
        item.reused
        for item in second_result.prepared_inputs
    )

    print(
        "\nDONE: Render asset preloader test "
        "completed."
    )


if __name__ == "__main__":
    main()