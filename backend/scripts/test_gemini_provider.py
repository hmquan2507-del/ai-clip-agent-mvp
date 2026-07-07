from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.ai.providers import (
    AIProviderJSONRequest,
    AIProviderRequest,
    AIProviderTokenCountRequest,
    build_default_provider_manager,
)


def main():
    manager = build_default_provider_manager()

    print("=== Gemini Text Test ===")
    text_response = manager.generate(
        provider_key="gemini",
        request=AIProviderRequest(
            prompt="Say hello to AI Clip Agent in one short sentence.",
            temperature=0.2,
            max_tokens=80,
        ),
    )
    print(text_response.to_dict())

    print("\n=== Gemini JSON Test ===")
    json_response = manager.generate_json(
        provider_key="gemini",
        request=AIProviderJSONRequest(
            prompt='Return only valid JSON with title="AI Clip Agent" and score=8.',            
            temperature=0.1,
            max_tokens=2048,
            schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "score": {"type": "number"},
                },
                "required": ["title", "score"],
            },
        ),
    )
    print(json_response.to_dict())

    print("\n=== Gemini Token Count Test ===")
    token_response = manager.count_tokens(
        provider_key="gemini",
        request=AIProviderTokenCountRequest(
            text="AI Clip Agent turns raw video into edited clips.",
        ),
    )
    print(token_response.to_dict())


if __name__ == "__main__":
    main()