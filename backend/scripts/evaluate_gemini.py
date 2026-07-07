from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from evaluation.runner import GeminiEvaluationRunner


def main():
    runner = GeminiEvaluationRunner()

    tasks = [
        "hook_detection",
        "story_engine",
        "emotion",
    ]

    report = {
        "provider": "gemini",
        "tasks": {},
    }

    for task in tasks:
        print(f"\n=== Evaluating {task} ===")
        result = runner.run_task(task)
        report["tasks"][task] = {
            "sample_count": result["sample_count"],
            "average_score": result["average_score"],
            "average_latency_ms": result["average_latency_ms"],
        }

        print(json.dumps(report["tasks"][task], ensure_ascii=False, indent=2))

    output_path = Path("evaluation/evaluation_report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\nDONE")
    print(f"Report saved to: {output_path}")


if __name__ == "__main__":
    main()