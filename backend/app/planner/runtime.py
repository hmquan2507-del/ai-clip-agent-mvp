from __future__ import annotations

from app.planner.ai_provider import BasePlannerAIProvider, MockPlannerAIProvider
from app.planner.models import EditingPlan, PlannerRequest
from app.planner.prompts import PlannerPromptBuilder
from app.planner.rules import PlannerRuleEngine
from app.planner.scoring import PlannerScoringEngine


class AIPlannerRuntime:
    def __init__(
        self,
        rule_engine: PlannerRuleEngine | None = None,
        prompt_builder: PlannerPromptBuilder | None = None,
        ai_provider: BasePlannerAIProvider | None = None,
        scoring_engine: PlannerScoringEngine | None = None,
    ):
        self.rule_engine = rule_engine or PlannerRuleEngine()
        self.prompt_builder = prompt_builder or PlannerPromptBuilder()
        self.ai_provider = ai_provider or MockPlannerAIProvider()
        self.scoring_engine = scoring_engine or PlannerScoringEngine()

    def build_plan(
        self,
        request: PlannerRequest,
    ) -> EditingPlan:
        hints = self.rule_engine.build_hints(
            context=request.context,
            segments=request.segments,
        )

        prompt = self.prompt_builder.build_asset_planner_prompt(
            context=request.context,
            segments=request.segments,
            hints=hints,
        )

        instructions = self.ai_provider.build_plan(
            request=request,
            hints=hints,
            prompt=prompt,
        )

        for instruction in instructions:
            instruction.confidence = self.scoring_engine.score_instruction(instruction)

        return EditingPlan(
            production_id=request.context.production_id,
            planner_version="13.12.4",
            instructions=instructions,
            metadata={
                "planner": "ai_asset_planner",
                "provider": self.ai_provider.__class__.__name__,
                "hint_count": len(hints),
                "instruction_count": len(instructions),
                "prompt_preview": prompt[:1000],
                "context": {
                    "platform": request.context.platform,
                    "editing_style": request.context.editing_style,
                    "story_type": request.context.story_type,
                    "language": request.context.language,
                },
            },
        )