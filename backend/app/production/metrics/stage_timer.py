from __future__ import annotations

import time


class StageTimer:

    def __init__(self):
        self.started: dict[str, float] = {}

    def start(
        self,
        stage: str,
    ):
        self.started[stage] = time.perf_counter()

    def stop(
        self,
        stage: str,
    ) -> float:

        value = self.started.pop(stage, None)

        if value is None:
            return 0

        return round(
            (time.perf_counter() - value) * 1000,
            2,
        )