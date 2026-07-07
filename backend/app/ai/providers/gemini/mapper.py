from __future__ import annotations

from typing import Any


def response_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if text:
        return str(text)

    return ""


def response_raw(response: Any) -> dict[str, Any]:
    if hasattr(response, "model_dump"):
        try:
            return response.model_dump()
        except Exception:
            return {}

    if hasattr(response, "to_dict"):
        try:
            return response.to_dict()
        except Exception:
            return {}

    return {
        "response_class": response.__class__.__name__,
    }


def token_count(response: Any) -> int:
    total_tokens = getattr(response, "total_tokens", None)

    if isinstance(total_tokens, int):
        return total_tokens

    return 0

def finish_reason(response: Any) -> str:
    candidates = getattr(response, "candidates", None)

    if not candidates:
        return ""

    first = candidates[0]
    reason = getattr(first, "finish_reason", "")

    return str(reason)