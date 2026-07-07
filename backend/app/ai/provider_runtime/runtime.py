from __future__ import annotations

from app.ai.prompt_runtime import PromptRuntime
from app.ai.provider_runtime.models import ProviderRuntimeRequest, ProviderRuntimeResult
from app.ai.providers import AIProviderJSONRequest, AIProviderRequest, AIProviderManager
from app.ai.structured_output import StructuredOutputRuntime


class ProviderRuntime:
    def __init__(
        self,
        prompt_runtime: PromptRuntime,
        provider_manager: AIProviderManager,
        structured_output_runtime: StructuredOutputRuntime,
    ):
        self.prompt_runtime = prompt_runtime
        self.provider_manager = provider_manager
        self.structured_output_runtime = structured_output_runtime

    def generate_text(
        self,
        request: ProviderRuntimeRequest,
    ) -> ProviderRuntimeResult:
        rendered = self.prompt_runtime.render(
            prompt_key=request.prompt_key,
            variables=request.variables,
        )

        provider_response = self.provider_manager.generate(
            provider_key=request.provider_key,
            request=AIProviderRequest(
                prompt=rendered["prompt"],
                system_prompt=rendered["system_prompt"],
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ),
        )

        return ProviderRuntimeResult(
            provider_key=request.provider_key,
            prompt_key=request.prompt_key,
            text=provider_response.text,
            data={},
            is_valid=True,
            errors=[],
            metadata={
                "mode": "text",
                "provider": provider_response.provider,
                "model": provider_response.model,
                "provider_metadata": provider_response.metadata,
            },
        )

    def generate_structured(
        self,
        request: ProviderRuntimeRequest,
        schema: dict | None = None,
    ) -> ProviderRuntimeResult:
        rendered = self.prompt_runtime.render(
            prompt_key=request.prompt_key,
            variables=request.variables,
        )

        provider_response = self.provider_manager.generate_json(
            provider_key=request.provider_key,
            request=AIProviderJSONRequest(
                prompt=rendered["prompt"],
                system_prompt=rendered["system_prompt"],
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                schema=schema or {},
            ),
        )

        raw_text = provider_response.raw_text

        if not raw_text and provider_response.data:
            raw_text = "{}"

        parsed = self.structured_output_runtime.parse_and_validate(
            raw_text=raw_text,
            required_keys=request.required_keys,
        )

        data = parsed.data if parsed.data else provider_response.data

        return ProviderRuntimeResult(
            provider_key=request.provider_key,
            prompt_key=request.prompt_key,
            text=raw_text,
            data=data,
            is_valid=parsed.is_valid or bool(provider_response.data),
            errors=parsed.errors,
            metadata={
                "mode": "structured",
                "provider": provider_response.provider,
                "model": provider_response.model,
                "provider_metadata": provider_response.metadata,
            },
        )