from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class EvaluationDatasetLoader:
    def __init__(self, base_path: str = "evaluation/datasets"):
        self.base_path = Path(base_path)

    def load(self, task: str) -> list[dict[str, Any]]:
        path = self.base_path / task / "samples.json"

        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []