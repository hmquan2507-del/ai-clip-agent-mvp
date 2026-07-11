from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


GRAPH_PATH = Path(
    "storage/demo_outputs/ffmpeg_filtergraph.json"
)

OUTPUT_DIR = Path(
    "storage/demo_outputs/debug_video_stages"
)

VIDEO_STAGE_ORDER = {
    "primary_trim": 10,
    "primary_scale": 20,
    "primary_concat": 30,
    "broll_trim": 40,
    "broll_scale": 50,
    "broll_timing": 60,
    "overlay": 70,
    "effect": 80,
    "transition": 90,
    "subtitle": 100,
}

DEBUG_STAGES = [
    "primary_concat",
    "overlay",
    "effect",
    "transition",
    "subtitle",
]


def main() -> None:
    if not GRAPH_PATH.exists():
        raise RuntimeError(
            f"FilterGraph JSON does not exist: {GRAPH_PATH}"
        )

    payload = json.loads(
        GRAPH_PATH.read_text(encoding="utf-8")
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    input_arguments = build_input_arguments(payload)

    video_chains = [
        chain
        for chain in payload["chains"]
        if chain.get("stage") in VIDEO_STAGE_ORDER
    ]

    print("=== Available video chains ===")

    for chain in video_chains:
        print(
            chain["stage"],
            chain["chain_id"],
            "=>",
            chain.get("output_label"),
        )

    results: list[dict[str, Any]] = []

    for debug_stage in DEBUG_STAGES:
        result = render_stage(
            payload=payload,
            video_chains=video_chains,
            input_arguments=input_arguments,
            debug_stage=debug_stage,
        )

        results.append(result)

    report_path = (
        OUTPUT_DIR / "debug_video_stages_report.json"
    )

    report_path.write_text(
        json.dumps(
            results,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n=== Summary ===")

    for result in results:
        print(
            result["stage"],
            "render_success=",
            result["render_success"],
            "black_detected=",
            result["black_detected"],
            "black_ratio=",
            result["black_ratio"],
        )

    print("\nreport:", report_path)


def render_stage(
    payload: dict[str, Any],
    video_chains: list[dict[str, Any]],
    input_arguments: list[str],
    debug_stage: str,
) -> dict[str, Any]:
    print(f"\n=== Rendering stage: {debug_stage} ===")

    stage_rank = VIDEO_STAGE_ORDER[debug_stage]

    selected_chains = [
        chain
        for chain in video_chains
        if VIDEO_STAGE_ORDER[chain["stage"]] <= stage_rank
    ]

    stage_matches = [
        chain
        for chain in selected_chains
        if chain["stage"] == debug_stage
        and chain.get("output_label")
    ]

    if not stage_matches:
        print("No output label found for stage.")

        return {
            "stage": debug_stage,
            "render_success": False,
            "returncode": None,
            "output_label": None,
            "output_path": None,
            "black_detected": False,
            "black_duration": 0.0,
            "black_ratio": 0.0,
            "error": "stage_output_label_not_found",
        }

    # Lấy chain cuối cùng của stage.
    final_chain = sorted(
        stage_matches,
        key=lambda item: (
            item.get("order", 0),
            item["chain_id"],
        ),
    )[-1]

    output_label = final_chain["output_label"]

    selected_chains = remove_unused_video_branches(
        chains=selected_chains,
        required_output_label=output_label,
    )

    filter_complex = ";".join(
        chain["filter_text"]
        for chain in sorted(
            selected_chains,
            key=lambda item: (
                item.get("order", 0),
                item["chain_id"],
            ),
        )
        if chain.get("filter_text")
    )

    output_path = (
        OUTPUT_DIR / f"{debug_stage}.mp4"
    )

    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        *input_arguments,
        "-filter_complex",
        filter_complex,
        "-map",
        f"[{output_label}]",
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-r",
        str(
            payload.get("metadata", {}).get(
                "fps",
                30,
            )
        ),
        "-t",
        str(
            payload.get("metadata", {}).get(
                "duration",
                18,
            )
        ),
        str(output_path),
    ]

    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )

    print("output_label:", output_label)
    print("chain_count:", len(selected_chains))
    print("returncode:", completed.returncode)

    if completed.returncode != 0:
        print(completed.stderr)

        return {
            "stage": debug_stage,
            "render_success": False,
            "returncode": completed.returncode,
            "output_label": output_label,
            "output_path": str(output_path),
            "black_detected": False,
            "black_duration": 0.0,
            "black_ratio": 0.0,
            "error": completed.stderr.strip(),
        }

    detection = detect_black_frames(
        output_path=output_path,
        duration=float(
            payload.get("metadata", {}).get(
                "duration",
                18.0,
            )
        ),
    )

    print(
        "black_detected:",
        detection["black_detected"],
    )
    print(
        "black_duration:",
        detection["black_duration"],
    )
    print(
        "black_ratio:",
        detection["black_ratio"],
    )

    for line in detection["black_lines"]:
        print(line)

    return {
        "stage": debug_stage,
        "render_success": True,
        "returncode": completed.returncode,
        "output_label": output_label,
        "output_path": str(output_path),
        **detection,
        "error": None,
    }


def remove_unused_video_branches(
    chains: list[dict[str, Any]],
    required_output_label: str,
) -> list[dict[str, Any]]:
    """
    Đi ngược từ output label cần debug để chỉ giữ các chain
    thực sự cần thiết. Việc này tránh output pad bị bỏ trống
    hoặc các branch chưa được consume.
    """
    chain_by_output = {
        chain["output_label"]: chain
        for chain in chains
        if chain.get("output_label")
    }

    required_chain_ids: set[str] = set()
    pending_labels = [required_output_label]

    while pending_labels:
        label = pending_labels.pop()

        chain = chain_by_output.get(label)

        if chain is None:
            # Đây có thể là input stream như 0:v.
            continue

        chain_id = chain["chain_id"]

        if chain_id in required_chain_ids:
            continue

        required_chain_ids.add(chain_id)

        for input_label in chain.get(
            "input_labels",
            [],
        ):
            normalized = normalize_label(
                input_label
            )

            if normalized in chain_by_output:
                pending_labels.append(normalized)

    return [
        chain
        for chain in chains
        if chain["chain_id"] in required_chain_ids
    ]


def build_input_arguments(
    payload: dict[str, Any],
) -> list[str]:
    arguments: list[str] = []

    for item in sorted(
        payload["input_arguments"],
        key=lambda value: value["input_index"],
    ):
        arguments.extend(
            item["arguments"]
        )

    return arguments


def detect_black_frames(
    output_path: Path,
    duration: float,
) -> dict[str, Any]:
    command = [
        "ffmpeg",
        "-hide_banner",
        "-i",
        str(output_path),
        "-vf",
        "blackdetect=d=1:pic_th=0.98:pix_th=0.10",
        "-an",
        "-f",
        "null",
        "-",
    ]

    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )

    black_lines = [
        line
        for line in completed.stderr.splitlines()
        if "black_start:" in line
    ]

    black_duration = 0.0

    for line in black_lines:
        marker = "black_duration:"

        if marker not in line:
            continue

        try:
            value = (
                line.split(marker, 1)[1]
                .strip()
                .split()[0]
            )

            black_duration += float(value)

        except (IndexError, ValueError):
            continue

    black_ratio = (
        black_duration / duration
        if duration > 0
        else 0.0
    )

    return {
        "black_detected": bool(black_lines),
        "black_duration": round(
            black_duration,
            6,
        ),
        "black_ratio": round(
            black_ratio,
            6,
        ),
        "black_lines": black_lines,
    }


def normalize_label(
    value: str,
) -> str:
    return (
        value.strip()
        .removeprefix("[")
        .removesuffix("]")
    )


if __name__ == "__main__":
    main()