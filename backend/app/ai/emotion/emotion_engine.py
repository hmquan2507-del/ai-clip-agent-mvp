from __future__ import annotations

from collections import Counter
from typing import Any

from app.ai.base.base_engine import BaseAIEngine
from app.ai.emotion.emotion_scoring import score_emotion
from app.ai.emotion.models import EmotionDetectionResult, EmotionSegment
from app.ai.runtime.ai_context import AIContext


class EmotionEngine(BaseAIEngine):
    engine_name = "rule_based_emotion_engine"

    def __init__(self, min_intensity: float = 0.15):
        self.min_intensity = min_intensity

    def run(self, context: AIContext) -> EmotionDetectionResult:
        segments = context.get_segments()

        hook_result = context.get_runtime_result("hook_detection", {})
        story_result = context.get_runtime_result("story_engine", {})

        emotion_segments: list[EmotionSegment] = []

        for segment in segments:
            text = segment.get("text", "")
            start_time = self._safe_float(segment.get("start_time", 0.0))
            end_time = self._safe_float(segment.get("end_time", start_time + 3.0))

            emotion, intensity, reasons = score_emotion(
                text=text,
                start_time=start_time,
            )

            intensity, reasons = self._enrich_with_context(
                segment=segment,
                intensity=intensity,
                reasons=reasons,
                hook_result=hook_result,
                story_result=story_result,
            )

            if intensity < self.min_intensity:
                continue

            emotion_segments.append(
                EmotionSegment(
                    start_time=start_time,
                    end_time=end_time,
                    text=text,
                    emotion=emotion,
                    intensity=round(min(intensity, 1.0), 4),
                    reasons=reasons,
                    source_segment_id=segment.get("id") or segment.get("segment_id"),
                )
            )

        dominant_emotion = self._dominant_emotion(emotion_segments)
        average_intensity = self._average_intensity(emotion_segments)

        return EmotionDetectionResult(
            production_id=context.production_id,
            segments=emotion_segments,
            dominant_emotion=dominant_emotion,
            average_intensity=average_intensity,
            metadata={
                "engine": self.engine_name,
                "total_segments": len(segments),
                "emotion_segments": len(emotion_segments),
                "min_intensity": self.min_intensity,
                "used_context": {
                    "has_hook_detection": bool(hook_result),
                    "has_story_engine": bool(story_result),
                },
            },
        )

    def _enrich_with_context(
        self,
        segment: dict[str, Any],
        intensity: float,
        reasons: list[str],
        hook_result: dict[str, Any],
        story_result: dict[str, Any],
    ) -> tuple[float, list[str]]:
        source_id = segment.get("id") or segment.get("segment_id")

        if self._segment_in_hook(source_id, hook_result):
            intensity += 0.12
            reasons.append("context:hook_segment")

        story_beat = self._find_story_beat(source_id, story_result)

        if story_beat:
            beat_type = story_beat.get("beat_type")

            if beat_type in {"problem", "payoff"}:
                intensity += 0.10
                reasons.append(f"context:story_{beat_type}")

            elif beat_type == "insight":
                intensity += 0.06
                reasons.append("context:story_insight")

        return intensity, reasons

    def _segment_in_hook(
        self,
        source_id: str | None,
        hook_result: dict[str, Any],
    ) -> bool:
        if not source_id:
            return False

        hooks = hook_result.get("hooks", [])

        if not isinstance(hooks, list):
            return False

        return any(
            hook.get("source_segment_id") == source_id
            for hook in hooks
            if isinstance(hook, dict)
        )

    def _find_story_beat(
        self,
        source_id: str | None,
        story_result: dict[str, Any],
    ) -> dict[str, Any] | None:
        if not source_id:
            return None

        beats = story_result.get("beats", [])

        if not isinstance(beats, list):
            return None

        for beat in beats:
            if not isinstance(beat, dict):
                continue

            if beat.get("source_segment_id") == source_id:
                return beat

        return None

    def _dominant_emotion(self, segments: list[EmotionSegment]) -> str:
        if not segments:
            return "neutral"

        counter = Counter(segment.emotion for segment in segments)
        return counter.most_common(1)[0][0]

    def _average_intensity(self, segments: list[EmotionSegment]) -> float:
        if not segments:
            return 0.0

        return round(
            sum(segment.intensity for segment in segments) / len(segments),
            4,
        )

    def _safe_float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0