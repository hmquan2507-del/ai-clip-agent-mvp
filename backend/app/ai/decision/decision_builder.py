from __future__ import annotations

from typing import Any

from app.ai.decision.decision_rules import (
    priority_from_score,
    should_add_broll,
    should_add_sfx,
    should_add_zoom,
)
from app.ai.decision.models import EditingDecision


class DecisionBuilder:
    def build_from_hook(
        self,
        hook: dict[str, Any],
        style_result: dict[str, Any],
    ) -> list[EditingDecision]:
        start_time = self._safe_float(hook.get("start_time", 0.0))
        end_time = self._safe_float(hook.get("end_time", start_time + 3.0))
        score = self._safe_float(hook.get("score", 0.0))
        priority = priority_from_score(score)

        source_segment_id = hook.get("source_segment_id")

        decisions = [
            EditingDecision(
                decision_type="subtitle_emphasis",
                start_time=start_time,
                end_time=end_time,
                priority=priority,
                target="subtitle",
                action="emphasize_hook_text",
                reason="hook_segment",
                metadata={
                    "hook_score": score,
                    "hook_reasons": hook.get("reasons", []),
                },
                source_segment_id=source_segment_id,
            )
        ]

        if should_add_zoom(style_result, priority):
            decisions.append(
                EditingDecision(
                    decision_type="zoom_in",
                    start_time=start_time,
                    end_time=end_time,
                    priority=priority,
                    target="camera",
                    action="apply_hook_zoom",
                    reason="hook_segment_with_style_zoom",
                    metadata={"hook_score": score},
                    source_segment_id=source_segment_id,
                )
            )

        if should_add_sfx(style_result, priority):
            decisions.append(
                EditingDecision(
                    decision_type="sound_effect",
                    start_time=start_time,
                    end_time=min(end_time, start_time + 1.0),
                    priority=priority,
                    target="audio",
                    action="add_pop_or_impact_sfx",
                    reason="hook_segment_with_style_sfx",
                    metadata={"hook_score": score},
                    source_segment_id=source_segment_id,
                )
            )

        return decisions

    def build_from_story_beat(
        self,
        beat: dict[str, Any],
        style_result: dict[str, Any],
    ) -> list[EditingDecision]:
        beat_type = beat.get("beat_type", "unknown")
        start_time = self._safe_float(beat.get("start_time", 0.0))
        end_time = self._safe_float(beat.get("end_time", start_time + 3.0))
        score = self._safe_float(beat.get("score", 0.0))
        priority = priority_from_score(score)

        source_segment_id = beat.get("source_segment_id")

        decisions: list[EditingDecision] = []

        if beat_type in {"problem", "insight", "payoff"}:
            decisions.append(
                EditingDecision(
                    decision_type="subtitle_emphasis",
                    start_time=start_time,
                    end_time=end_time,
                    priority=priority,
                    target="subtitle",
                    action=f"emphasize_{beat_type}_beat",
                    reason=f"story_{beat_type}",
                    metadata={
                        "story_score": score,
                        "story_reasons": beat.get("reasons", []),
                    },
                    source_segment_id=source_segment_id,
                )
            )

        if beat_type == "problem" and should_add_zoom(style_result, priority):
            decisions.append(
                EditingDecision(
                    decision_type="zoom_in",
                    start_time=start_time,
                    end_time=end_time,
                    priority=priority,
                    target="camera",
                    action="apply_problem_zoom",
                    reason="story_problem_with_style_zoom",
                    metadata={"story_score": score},
                    source_segment_id=source_segment_id,
                )
            )

        if beat_type in {"insight", "payoff"} and should_add_broll(
            style_result,
            priority,
        ):
            decisions.append(
                EditingDecision(
                    decision_type="broll",
                    start_time=start_time,
                    end_time=end_time,
                    priority=priority,
                    target="visual",
                    action=f"insert_{beat_type}_supporting_broll",
                    reason=f"story_{beat_type}_needs_visual_support",
                    metadata={"story_score": score},
                    source_segment_id=source_segment_id,
                )
            )

        return decisions

    def build_from_emotion_segment(
        self,
        emotion_segment: dict[str, Any],
        style_result: dict[str, Any],
    ) -> list[EditingDecision]:
        emotion = emotion_segment.get("emotion", "neutral")
        intensity = self._safe_float(emotion_segment.get("intensity", 0.0))
        priority = priority_from_score(intensity)

        start_time = self._safe_float(emotion_segment.get("start_time", 0.0))
        end_time = self._safe_float(emotion_segment.get("end_time", start_time + 3.0))
        source_segment_id = emotion_segment.get("source_segment_id")

        decisions: list[EditingDecision] = []

        if emotion in {"pain", "urgency", "surprise"}:
            decisions.append(
                EditingDecision(
                    decision_type="pace_change",
                    start_time=start_time,
                    end_time=end_time,
                    priority=priority,
                    target="timeline",
                    action="increase_cut_speed",
                    reason=f"emotion_{emotion}",
                    metadata={"emotion": emotion, "intensity": intensity},
                    source_segment_id=source_segment_id,
                )
            )

        if emotion in {"curiosity", "surprise"} and should_add_zoom(
            style_result,
            priority,
        ):
            decisions.append(
                EditingDecision(
                    decision_type="zoom_in",
                    start_time=start_time,
                    end_time=end_time,
                    priority=priority,
                    target="camera",
                    action=f"apply_{emotion}_zoom",
                    reason=f"emotion_{emotion}_with_style_zoom",
                    metadata={"emotion": emotion, "intensity": intensity},
                    source_segment_id=source_segment_id,
                )
            )

        if emotion in {"excitement", "surprise", "urgency"} and should_add_sfx(
            style_result,
            priority,
        ):
            decisions.append(
                EditingDecision(
                    decision_type="sound_effect",
                    start_time=start_time,
                    end_time=min(end_time, start_time + 1.0),
                    priority=priority,
                    target="audio",
                    action=f"add_{emotion}_sfx",
                    reason=f"emotion_{emotion}_with_style_sfx",
                    metadata={"emotion": emotion, "intensity": intensity},
                    source_segment_id=source_segment_id,
                )
            )

        return decisions

    def build_global_style_decisions(
        self,
        style_result: dict[str, Any],
    ) -> list[EditingDecision]:
        editing_style = style_result.get("editing_style", {})

        if not isinstance(editing_style, dict):
            return []

        return [
            EditingDecision(
                decision_type="global_style",
                start_time=0.0,
                end_time=0.0,
                priority="high",
                target="global",
                action="apply_editing_style_profile",
                reason="editing_style_engine_output",
                metadata={
                    "style_profile": style_result.get("style_profile"),
                    "editing_style": editing_style,
                },
            )
        ]

    def _safe_float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0