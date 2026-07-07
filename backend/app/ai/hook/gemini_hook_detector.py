from __future__ import annotations

from typing import Any

from app.ai.provider_runtime import ProviderRuntimeRequest, build_default_provider_runtime


class GeminiHookDetector:
    def __init__(self):
        self.runtime = build_default_provider_runtime()

    def detect(
        self,
        transcript: str,
    ) -> dict[str, Any]:
        result = self.runtime.generate_structured(
            ProviderRuntimeRequest(
                provider_key="gemini",
                prompt_key="hook.detect",
                variables={
                    "transcript": transcript,
                },
                required_keys=["hooks"],
                max_tokens=2048,
                temperature=0.2,
            ),
            schema={
                "type": "object",
                "properties": {
                    "hooks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string"},
                                "score": {"type": "number"},
                                "reason": {"type": "string"},
                            },
                            "required": ["text", "score", "reason"],
                        },
                    }
                },
                "required": ["hooks"],
            },
        )

        return result.to_dict()