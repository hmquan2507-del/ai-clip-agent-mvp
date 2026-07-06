from __future__ import annotations

from typing import Any

from app.ai.base.base_engine import BaseAIEngine
from app.ai.hook.hook_scoring import score_hook_segment
from app.ai.hook.models import HookCandidate, HookDetectionResult
from app.ai.runtime.ai_context import AIContext


class HookDetectionEngine(BaseAIEngine):
    engine_name = "rule_based_hook_detection"

    def __init__(self, max_hooks: int = 5, min_score: float = 0.25):
        self.max_hooks = max_hooks
        self.min_score = min_score

    def run(self, context: AIContext) -> HookDetectionResult:
        segments = context.get_segments()

        candidates: list[HookCandidate] = []

        for segment in segments:
            text = segment.get("text", "")
            start_time = self._safe_float(segment.get("start_time", 0.0))
            end_time = self._safe_float(segment.get("end_time", start_time + 3.0))

            score, reasons = score_hook_segment(
                text=text,
                start_time=start_time,
            )

            if score < self.min_score:
                continue

            candidates.append(
                HookCandidate(
                    start_time=start_time,
                    end_time=end_time,
                    text=text,
                    score=round(score, 4),
                    reasons=reasons,
                    source_segment_id=segment.get("id") or segment.get("segment_id"),
                )
            )

        candidates.sort(key=lambda item: item.score, reverse=True)

        return HookDetectionResult(
            production_id=context.production_id,
            hooks=candidates[: self.max_hooks],
            metadata={
                "engine": self.engine_name,
                "total_segments": len(segments),
                "total_candidates": len(candidates),
                "max_hooks": self.max_hooks,
                "min_score": self.min_score,
            },
        )

    def _safe_float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0