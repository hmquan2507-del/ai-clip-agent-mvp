from __future__ import annotations

from app.ai.base.base_engine import BaseAIEngine
from app.ai.runtime.ai_context import AIContext
from app.ai.style.models import EditingStyleResult
from app.ai.style.strategy_builder import build_style_plan_from_dict
from app.ai.style.style_profiles import DEFAULT_STYLE_PROFILE, STYLE_PROFILES
from app.ai.style.style_rules import adjust_style_by_emotion, infer_style_profile


class EditingStyleEngine(BaseAIEngine):
    engine_name = "rule_based_editing_style_engine"

    def run(self, context: AIContext) -> EditingStyleResult:
        hook_result = context.get_runtime_result("hook_detection", {})
        story_result = context.get_runtime_result("story_engine", {})
        emotion_result = context.get_runtime_result("emotion_engine", {})

        style_profile, profile_reasons = infer_style_profile(
            hook_result=hook_result,
            story_result=story_result,
            emotion_result=emotion_result,
        )

        base_profile = STYLE_PROFILES.get(style_profile) or STYLE_PROFILES[
            DEFAULT_STYLE_PROFILE
        ]

        adjusted_profile, adjustment_reasons = adjust_style_by_emotion(
            plan=base_profile,
            emotion_result=emotion_result,
        )

        reasons = profile_reasons + adjustment_reasons

        plan = build_style_plan_from_dict(
            profile=adjusted_profile,
            reasons=reasons,
        )

        return EditingStyleResult(
            production_id=context.production_id,
            style_profile=style_profile,
            editing_style=plan,
            metadata={
                "engine": self.engine_name,
                "used_context": {
                    "has_hook_detection": bool(hook_result),
                    "has_story_engine": bool(story_result),
                    "has_emotion_engine": bool(emotion_result),
                },
            },
        )