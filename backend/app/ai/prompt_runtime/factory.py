from __future__ import annotations

from app.ai.prompt_runtime.loader import PromptLoader
from app.ai.prompt_runtime.models import PromptTemplate
from app.ai.prompt_runtime.runtime import PromptRuntime


def build_default_prompt_loader() -> PromptLoader:
    loader = PromptLoader()

    loader.register(
        PromptTemplate(
            key="hook.detect",
            system_prompt=(
                "You are an AI video editing assistant. "
                "You detect strong hooks for short-form videos. "
                "Return only valid JSON."
            ),
            user_prompt=(
                "Analyze this transcript and find the strongest hook candidates.\n\n"
                "Transcript:\n{transcript}\n\n"
                "Return only valid JSON with this shape:\n"
                '{{"hooks":[{{"text":"...","score":8,"reason":"..."}}]}}'
            )
        )
    )

    loader.register(
        PromptTemplate(
            key="editing.decision",
            system_prompt="You are an AI video editing assistant.",
            user_prompt=(
                "Analyze this content graph and return editing decisions.\n\n"
                "Content:\n{content}"
            ),
        )
    )

    return loader


def build_default_prompt_runtime() -> PromptRuntime:
    return PromptRuntime(
        loader=build_default_prompt_loader(),
    )