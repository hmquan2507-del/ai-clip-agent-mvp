from __future__ import annotations

from app.planner.models import PlannerInstruction, PlannerPriority


class PlannerScoringEngine:
    PRIORITY_SCORE = {
        PlannerPriority.LOW: 0.35,
        PlannerPriority.MEDIUM: 0.55,
        PlannerPriority.HIGH: 0.75,
        PlannerPriority.CRITICAL: 0.95,
    }

    def score_instruction(
        self,
        instruction: PlannerInstruction,
    ) -> float:
        base = self.PRIORITY_SCORE.get(instruction.priority, 0.5)

        if instruction.query:
            base += 0.03

        if instruction.reason:
            base += 0.02

        return round(min(base, 0.99), 4)