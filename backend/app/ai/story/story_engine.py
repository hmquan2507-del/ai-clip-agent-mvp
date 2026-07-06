from __future__ import annotations

from typing import Any

from app.ai.base.base_engine import BaseAIEngine
from app.ai.runtime.ai_context import AIContext
from app.ai.story.models import StoryArc, StoryBeat, StoryDetectionResult
from app.ai.story.story_scoring import score_story_beat


class StoryEngine(BaseAIEngine):
    engine_name = "rule_based_story_engine"

    def __init__(self, min_score: float = 0.25):
        self.min_score = min_score

    def run(self, context: AIContext) -> StoryDetectionResult:
        segments = context.get_segments()

        beats: list[StoryBeat] = []

        for segment in segments:
            text = segment.get("text", "")
            start_time = self._safe_float(segment.get("start_time", 0.0))
            end_time = self._safe_float(segment.get("end_time", start_time + 3.0))

            beat_type, score, reasons = score_story_beat(
                text=text,
                start_time=start_time,
            )

            if score < self.min_score or beat_type == "unknown":
                continue

            beats.append(
                StoryBeat(
                    beat_type=beat_type,
                    start_time=start_time,
                    end_time=end_time,
                    text=text,
                    score=score,
                    reasons=reasons,
                    source_segment_id=segment.get("id") or segment.get("segment_id"),
                )
            )

        arcs = self._build_arcs(beats)

        return StoryDetectionResult(
            production_id=context.production_id,
            arcs=arcs,
            beats=beats,
            metadata={
                "engine": self.engine_name,
                "total_segments": len(segments),
                "total_beats": len(beats),
                "total_arcs": len(arcs),
                "min_score": self.min_score,
            },
        )

    def _build_arcs(self, beats: list[StoryBeat]) -> list[StoryArc]:
        if not beats:
            return []

        ordered = sorted(beats, key=lambda beat: beat.start_time)
        required_order = ["setup", "problem", "insight", "resolution", "payoff"]

        selected: list[StoryBeat] = []
        last_time = -1.0

        for beat_type in required_order:
            candidates = [
                beat
                for beat in ordered
                if beat.beat_type == beat_type and beat.start_time >= last_time
            ]

            if not candidates:
                continue

            best = max(candidates, key=lambda beat: beat.score)
            selected.append(best)
            last_time = best.start_time

        if len(selected) < 2:
            return []

        score = sum(beat.score for beat in selected) / len(selected)

        return [
            StoryArc(
                arc_type=self._detect_arc_type(selected),
                beats=selected,
                score=round(score, 4),
                metadata={
                    "beat_count": len(selected),
                    "has_problem": any(beat.beat_type == "problem" for beat in selected),
                    "has_resolution": any(
                        beat.beat_type == "resolution" for beat in selected
                    ),
                    "has_payoff": any(beat.beat_type == "payoff" for beat in selected),
                },
            )
        ]

    def _detect_arc_type(self, beats: list[StoryBeat]) -> str:
        beat_types = {beat.beat_type for beat in beats}

        if {"problem", "resolution", "payoff"}.issubset(beat_types):
            return "problem_solution_payoff"

        if {"setup", "problem", "insight"}.issubset(beat_types):
            return "setup_problem_insight"

        if {"problem", "insight"}.issubset(beat_types):
            return "problem_insight"

        return "partial_story_arc"

    def _safe_float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0