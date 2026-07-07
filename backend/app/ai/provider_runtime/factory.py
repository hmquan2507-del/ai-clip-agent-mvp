from __future__ import annotations

from app.ai.prompt_runtime import build_default_prompt_runtime
from app.ai.provider_runtime.runtime import ProviderRuntime
from app.ai.providers import build_default_provider_manager
from app.ai.structured_output import StructuredOutputRuntime


def build_default_provider_runtime() -> ProviderRuntime:
    return ProviderRuntime(
        prompt_runtime=build_default_prompt_runtime(),
        provider_manager=build_default_provider_manager(),
        structured_output_runtime=StructuredOutputRuntime(),
    )