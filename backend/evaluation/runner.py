from __future__ import annotations

import time
from typing import Any

from app.ai.hook.gemini_hook_detector import GeminiHookDetector
from app.ai.provider_runtime import ProviderRuntimeRequest, build_default_provider_runtime
from evaluation.dataset_loader import EvaluationDatasetLoader
from evaluation.scoring import EvaluationScorer


class GeminiEvaluationRunner:
    def __init__(self):
        self.loader = EvaluationDatasetLoader()
        self.scorer = EvaluationScorer()
        self.provider_runtime = build_default_provider_runtime()
        self.hook_detector = GeminiHookDetector()

    def run_task(self, task: str) -> dict[str, Any]:
        samples = self.loader.load(task)

        results: list[dict[str, Any]] = []

        for sample in samples:
            started_at = time.perf_counter()

            result = self._run_sample(
                task=task,
                transcript=str(sample.get("transcript", "")),
            )

            latency_ms = round((time.perf_counter() - started_at) * 1000, 2)

            score = self._score_sample(
                task=task,
                result=result,
                expected=sample.get("expected", {}),
            )

            results.append(
                {
                    "id": sample.get("id"),
                    "latency_ms": latency_ms,
                    "score": score,
                    "result": result,
                }
            )

        average_score = (
            round(sum(item["score"]["score"] for item in results) / len(results), 4)
            if results
            else 0
        )

        average_latency_ms = (
            round(sum(item["latency_ms"] for item in results) / len(results), 2)
            if results
            else 0
        )

        return {
            "provider": "gemini",
            "task": task,
            "sample_count": len(samples),
            "average_score": average_score,
            "average_latency_ms": average_latency_ms,
            "results": results,
        }

    def _run_sample(
        self,
        task: str,
        transcript: str,
    ) -> dict[str, Any]:
        if task == "hook_detection":
            return self.hook_detector.detect(transcript)

        if task == "story_engine":
            return self.provider_runtime.generate_structured(
                ProviderRuntimeRequest(
                    provider_key="gemini",
                    prompt_key="story.detect",
                    variables={"transcript": transcript},
                    required_keys=["story_points"],
                    max_tokens=2048,
                ),
                schema={
                    "type": "object",
                    "properties": {
                        "story_points": {
                            "type": "array",
                            "items": {"type": "string"},
                        }
                    },
                    "required": ["story_points"],
                },
            ).to_dict()

        if task == "emotion":
            return self.provider_runtime.generate_structured(
                ProviderRuntimeRequest(
                    provider_key="gemini",
                    prompt_key="emotion.detect",
                    variables={"transcript": transcript},
                    required_keys=["emotions"],
                    max_tokens=2048,
                ),
                schema={
                    "type": "object",
                    "properties": {
                        "emotions": {
                            "type": "array",
                            "items": {"type": "string"},
                        }
                    },
                    "required": ["emotions"],
                },
            ).to_dict()

        raise ValueError(f"Unsupported evaluation task: {task}")

    def _score_sample(
        self,
        task: str,
        result: dict[str, Any],
        expected: dict[str, Any],
    ) -> dict[str, Any]:
        if task == "hook_detection":
            return self.scorer.score_hook_result(result, expected)

        return self.scorer.score_generic_keywords(result, expected)