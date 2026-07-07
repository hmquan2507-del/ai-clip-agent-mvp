from __future__ import annotations

from typing import Any

from openai import OpenAI

from app.ai.providers.openai.exceptions import OpenAIConfigurationError
from app.core.config import settings


class OpenAIClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.openai_api_key

        if not self.api_key:
            raise OpenAIConfigurationError("OPENAI_API_KEY is required")

        self.client = OpenAI(api_key=self.api_key)

    def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> Any:
        messages = self._messages(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        return self.client.chat.completions.create(
            model=model or settings.openai_model,
            messages=messages,
            temperature=temperature if temperature is not None else settings.ai_temperature,
            max_tokens=max_tokens,
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
        messages = self._messages(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        return self.client.chat.completions.create(
            model=model or settings.openai_model,
            messages=messages,
            temperature=temperature if temperature is not None else settings.ai_temperature,
            max_tokens=max_tokens or 2048,
            response_format={"type": "json_object"},
        )

    def embed(
        self,
        input_text: str,
        model: str | None = None,
    ) -> Any:
        return self.client.embeddings.create(
            model=model or "text-embedding-3-small",
            input=input_text,
        )

    def count_tokens(
        self,
        text: str,
        model: str | None = None,
    ) -> int:
        # Fallback estimate. Later we can replace with tiktoken.
        return max(1, int(len(text.split()) * 1.3))

    def _messages(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []

        if system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": system_prompt,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        return messages