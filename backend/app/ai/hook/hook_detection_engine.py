from __future__ import annotations

from typing import Any

from app.ai.base.base_engine import BaseAIEngine
from app.ai.hook.gemini_hook_detector import GeminiHookDetector
from app.ai.hook.hook_scoring import score_hook_segment
from app.ai.hook.models import HookCandidate, HookDetectionResult
from app.ai.runtime.ai_context import AIContext
from app.core.config import settings


class HookDetectionEngine(BaseAIEngine):
    engine_name = "rule_based_hook_detection"

    def __init__(
        self,
        max_hooks: int = 5,
        min_score: float = 0.25,
    ):
        self.max_hooks = max_hooks
        self.min_score = min_score
        self.gemini_detector = self._build_gemini_detector()

    def run(self, context: AIContext) -> HookDetectionResult:
        segments = context.get_segments()
        candidates: list[HookCandidate] = []

        for segment in segments:
            text = str(segment.get("text") or "")
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

        metadata: dict[str, Any] = {
            "engine": self.engine_name,
            "total_segments": len(segments),
            "total_candidates": len(candidates),
            "max_hooks": self.max_hooks,
            "min_score": self.min_score,
            "gemini_enabled": self.gemini_detector is not None,
        }

        if self.gemini_detector is not None:
            transcript_text = self._build_transcript_text(segments)

            if transcript_text:
                metadata["gemini_hook_detection"] = self._safe_run_gemini(
                    transcript_text=transcript_text,
                )

        return HookDetectionResult(
            production_id=context.production_id,
            hooks=candidates[: self.max_hooks],
            metadata=metadata,
        )

    def _build_gemini_detector(self) -> GeminiHookDetector | None:
        if not settings.enable_gemini:
            return None

        if settings.default_ai_provider != "gemini":
            return None

        if not settings.gemini_api_key:
            return None

        return GeminiHookDetector()

    def _safe_run_gemini(
        self,
        transcript_text: str,
    ) -> dict[str, Any]:
        if self.gemini_detector is None:
            return {}

        try:
            return self.gemini_detector.detect(transcript_text)
        except Exception as error:
            return {
                "status": "failed",
                "error": str(error),
            }

    def _build_transcript_text(
        self,
        segments: list[dict[str, Any]],
    ) -> str:
        texts: list[str] = []

        for segment in segments:
            if not isinstance(segment, dict):
                continue

            text = str(segment.get("text") or "").strip()
            if text:
                texts.append(text)

        return "\n".join(texts)

    def _safe_float(
        self,
        value: Any,
    ) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0