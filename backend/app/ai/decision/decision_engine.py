from __future__ import annotations

from typing import Any

from app.ai.base.base_engine import BaseAIEngine
from app.ai.decision.decision_builder import DecisionBuilder
from app.ai.decision.models import DecisionEngineResult, EditingDecision
from app.ai.runtime.ai_context import AIContext


class DecisionEngine(BaseAIEngine):
    engine_name = "rule_based_decision_engine"

    def __init__(self, max_decisions: int = 80):
        self.max_decisions = max_decisions
        self.builder = DecisionBuilder()

    def run(self, context: AIContext) -> DecisionEngineResult:
        hook_result = context.get_runtime_result("hook_detection", {})
        story_result = context.get_runtime_result("story_engine", {})
        emotion_result = context.get_runtime_result("emotion_engine", {})
        style_result = context.get_runtime_result("editing_style_engine", {})

        decisions: list[EditingDecision] = []

        decisions.extend(
            self.builder.build_global_style_decisions(
                style_result=style_result,
            )
        )

        for hook in self._safe_list(hook_result.get("hooks")):
            decisions.extend(
                self.builder.build_from_hook(
                    hook=hook,
                    style_result=style_result,
                )
            )

        for beat in self._safe_list(story_result.get("beats")):
            decisions.extend(
                self.builder.build_from_story_beat(
                    beat=beat,
                    style_result=style_result,
                )
            )

        for emotion_segment in self._safe_list(emotion_result.get("segments")):
            decisions.extend(
                self.builder.build_from_emotion_segment(
                    emotion_segment=emotion_segment,
                    style_result=style_result,
                )
            )

        decisions = self._deduplicate(decisions)
        decisions = self._sort_decisions(decisions)

        return DecisionEngineResult(
            production_id=context.production_id,
            decisions=decisions[: self.max_decisions],
            metadata={
                "engine": self.engine_name,
                "total_decisions": len(decisions),
                "max_decisions": self.max_decisions,
                "used_context": {
                    "has_hook_detection": bool(hook_result),
                    "has_story_engine": bool(story_result),
                    "has_emotion_engine": bool(emotion_result),
                    "has_editing_style_engine": bool(style_result),
                },
            },
        )

    def _safe_list(self, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []

        return [item for item in value if isinstance(item, dict)]

    def _sort_decisions(
        self,
        decisions: list[EditingDecision],
    ) -> list[EditingDecision]:
        priority_order = {
            "high": 0,
            "medium": 1,
            "low": 2,
        }

        return sorted(
            decisions,
            key=lambda item: (
                item.start_time,
                priority_order.get(item.priority, 99),
                item.decision_type,
            ),
        )

    def _deduplicate(
        self,
        decisions: list[EditingDecision],
    ) -> list[EditingDecision]:
        seen: set[tuple[str, float, float, str, str | None]] = set()
        unique: list[EditingDecision] = []

        for decision in decisions:
            key = (
                decision.decision_type,
                round(decision.start_time, 2),
                round(decision.end_time, 2),
                decision.action,
                decision.source_segment_id,
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(decision)

        return unique