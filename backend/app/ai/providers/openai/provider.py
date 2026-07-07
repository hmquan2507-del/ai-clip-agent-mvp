from __future__ import annotations

import json
import time

from app.ai.providers.base import BaseAIProvider
from app.ai.providers.models import (
    AIProviderEmbeddingRequest,
    AIProviderEmbeddingResponse,
    AIProviderJSONRequest,
    AIProviderJSONResponse,
    AIProviderRequest,
    AIProviderResponse,
    AIProviderTokenCountRequest,
    AIProviderTokenCountResponse,
    AIProviderVisionRequest,
    AIProviderVisionResponse,
)
from app.ai.providers.openai.client import OpenAIClient
from app.ai.providers.openai.mapper import (
    embedding_from_response,
    finish_reason,
    response_raw,
    response_text,
    token_count_from_usage,
)
from app.ai.providers.retry_runtime import AIProviderRetryRuntime
from app.core.config import settings


class OpenAIProvider(BaseAIProvider):
    provider_key = "openai"
    default_model = settings.openai_model

    def __init__(
        self,
        client: OpenAIClient | None = None,
        retry_runtime: AIProviderRetryRuntime | None = None,
    ):
        self.client = client or OpenAIClient()
        self.retry_runtime = retry_runtime or AIProviderRetryRuntime()

    def generate(self, request: AIProviderRequest) -> AIProviderResponse:
        retry_result = self.retry_runtime.run_call(
            lambda: self.client.generate_text(
                prompt=request.prompt,
                system_prompt=request.system_prompt,
                model=request.model or self.default_model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
        )

        response = retry_result.value

        return AIProviderResponse(
            provider=self.provider_key,
            model=request.model or self.default_model,
            text=response_text(response),
            raw=response_raw(response),
            metadata={
                "uses_real_api": True,
                "finish_reason": finish_reason(response),
                "usage": token_count_from_usage(response),
                "retry": {
                    "attempts": retry_result.attempts,
                    "retried": retry_result.retried,
                    "retry_reasons": retry_result.retry_reasons,
                },
            },
        )

    def generate_json(self, request: AIProviderJSONRequest) -> AIProviderJSONResponse:
        retry_reasons: list[str] = []
        prompt = request.prompt
        max_tokens = request.max_tokens

        for attempt in range(1, self.retry_runtime.max_attempts + 1):
            retry_result = self.retry_runtime.run_call(
                lambda: self.client.generate_json(
                    prompt=prompt,
                    system_prompt=request.system_prompt,
                    model=request.model or self.default_model,
                    temperature=request.temperature,
                    max_tokens=max_tokens,
                    schema=request.schema or None,
                )
            )

            response = retry_result.value
            raw_text = response_text(response)
            data = self._safe_json(raw_text)
            reason = finish_reason(response)

            if retry_result.retry_reasons:
                retry_reasons.extend(retry_result.retry_reasons)

            decision = self.retry_runtime.policy.should_retry_json_result(
                data=data,
                raw_text=raw_text,
                finish_reason=reason,
                attempt=attempt,
                max_attempts=self.retry_runtime.max_attempts,
                current_max_tokens=max_tokens,
            )

            if not decision.should_retry:
                return AIProviderJSONResponse(
                    provider=self.provider_key,
                    model=request.model or self.default_model,
                    data=data,
                    raw_text=raw_text,
                    raw=response_raw(response),
                    metadata={
                        "uses_real_api": True,
                        "schema_provided": bool(request.schema),
                        "finish_reason": reason,
                        "is_truncated": reason in {"length", "max_output_tokens"},
                        "usage": token_count_from_usage(response),
                        "retry": {
                            "attempts": attempt,
                            "retried": attempt > 1,
                            "retry_reasons": retry_reasons,
                            "final_decision": decision.reason,
                        },
                    },
                )

            retry_reasons.append(decision.reason)

            if decision.next_max_tokens:
                max_tokens = decision.next_max_tokens

            if decision.next_prompt_suffix:
                prompt = f"{request.prompt}{decision.next_prompt_suffix}"

            time.sleep(self.retry_runtime.sleep_seconds * attempt)

        return AIProviderJSONResponse(
            provider=self.provider_key,
            model=request.model or self.default_model,
            data={},
            raw_text="",
            raw={},
            metadata={
                "uses_real_api": True,
                "schema_provided": bool(request.schema),
                "finish_reason": "retry_exhausted",
                "is_truncated": False,
                "retry": {
                    "attempts": self.retry_runtime.max_attempts,
                    "retried": True,
                    "retry_reasons": retry_reasons,
                    "final_decision": "retry_exhausted",
                },
            },
        )

    def embed(self, request: AIProviderEmbeddingRequest) -> AIProviderEmbeddingResponse:
        retry_result = self.retry_runtime.run_call(
            lambda: self.client.embed(
                input_text=request.input_text,
                model=request.model,
            )
        )

        response = retry_result.value

        return AIProviderEmbeddingResponse(
            provider=self.provider_key,
            model=request.model or "text-embedding-3-small",
            embedding=embedding_from_response(response),
            metadata={
                "uses_real_api": True,
                "retry": {
                    "attempts": retry_result.attempts,
                    "retried": retry_result.retried,
                    "retry_reasons": retry_result.retry_reasons,
                },
            },
        )

    def vision(self, request: AIProviderVisionRequest) -> AIProviderVisionResponse:
        raise NotImplementedError("OpenAI vision is not implemented yet")

    def count_tokens(
        self,
        request: AIProviderTokenCountRequest,
    ) -> AIProviderTokenCountResponse:
        return AIProviderTokenCountResponse(
            provider=self.provider_key,
            model=request.model or self.default_model,
            input_tokens=self.client.count_tokens(
                text=request.text,
                model=request.model or self.default_model,
            ),
            metadata={
                "uses_real_api": False,
                "strategy": "word_count_estimate",
            },
        )

    def _safe_json(self, raw_text: str) -> dict:
        try:
            value = json.loads(raw_text)
        except json.JSONDecodeError:
            return {}

        return value if isinstance(value, dict) else {}