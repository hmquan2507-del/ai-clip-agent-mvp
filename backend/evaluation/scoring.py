from __future__ import annotations

from typing import Any


class EvaluationScorer:
    def score_keywords(
        self,
        text: str,
        keywords: list[str],
    ) -> float:
        if not keywords:
            return 1.0

        normalized = text.lower()
        matched = sum(1 for keyword in keywords if keyword.lower() in normalized)

        return round(matched / len(keywords), 4)

    def score_hook_result(
        self,
        result: dict[str, Any],
        expected: dict[str, Any],
    ) -> dict[str, Any]:
        hooks = result.get("data", {}).get("hooks", [])
        combined_text = " ".join(
            str(item.get("text", "")) for item in hooks if isinstance(item, dict)
        )

        keyword_score = self.score_keywords(
            text=combined_text,
            keywords=expected.get("keywords", []),
        )

        min_hooks = int(expected.get("min_hooks", 1))
        hook_count_score = 1.0 if isinstance(hooks, list) and len(hooks) >= min_hooks else 0.0

        return {
            "score": round((keyword_score + hook_count_score) / 2, 4),
            "keyword_score": keyword_score,
            "hook_count_score": hook_count_score,
            "hook_count": len(hooks) if isinstance(hooks, list) else 0,
        }

    def score_generic_keywords(
        self,
        result: dict[str, Any],
        expected: dict[str, Any],
    ) -> dict[str, Any]:
        text = str(result)
        keywords = expected.get("keywords") or expected.get("emotions") or []

        score = self.score_keywords(text=text, keywords=keywords)

        return {
            "score": score,
            "keyword_score": score,
        }