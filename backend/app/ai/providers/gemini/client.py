from __future__ import annotations

from typing import Any

from google import genai
from google.genai import types

from app.ai.providers.gemini.exceptions import GeminiConfigurationError
from app.core.config import settings


class GeminiClient:
    def __init__(
        self,
        api_key: str | None = None,
    ):
        self.api_key = api_key or settings.gemini_api_key

        if not self.api_key:
            raise GeminiConfigurationError("GEMINI_API_KEY is required")

        self.client = genai.Client(api_key=self.api_key)

    def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> Any:
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature if temperature is not None else settings.ai_temperature,
            max_output_tokens=max_tokens,
        )

        return self.client.models.generate_content(
            model=model or settings.gemini_model,
            contents=prompt,
            config=config,
        )

    def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        schema: dict[str, Any] | None = None,
    ) -> Any:
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature if temperature is not None else settings.ai_temperature,
            max_output_tokens=max_tokens or 2048,
            response_mime_type="application/json",
            response_schema=schema,
        )

        return self.client.models.generate_content(
            model=model or settings.gemini_model,
            contents=prompt,
            config=config,
        )

    def count_tokens(
        self,
        text: str,
        model: str | None = None,
    ) -> Any:
        return self.client.models.count_tokens(
            model=model or settings.gemini_model,
            contents=text,
        )