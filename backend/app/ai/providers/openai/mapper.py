from __future__ import annotations

from typing import Any


def response_text(response: Any) -> str:
    choices = getattr(response, "choices", None)

    if not choices:
        return ""

    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", None)

    return str(content or "")


def response_raw(response: Any) -> dict[str, Any]:
    if hasattr(response, "model_dump"):
        try:
            return response.model_dump()
        except Exception:
            return {}

    return {
        "response_class": response.__class__.__name__,
    }


def finish_reason(response: Any) -> str:
    choices = getattr(response, "choices", None)

    if not choices:
        return ""

    return str(getattr(choices[0], "finish_reason", "") or "")


def usage(response: Any) -> dict[str, Any]:
    raw_usage = getattr(response, "usage", None)

    if raw_usage is None:
        return {}

    if hasattr(raw_usage, "model_dump"):
        try:
            return raw_usage.model_dump()
        except Exception:
            return {}

    return {}


def token_count_from_usage(response: Any) -> int:
    data = usage(response)
    total = data.get("total_tokens")

    if isinstance(total, int):
        return total

    return 0


def embedding_from_response(response: Any) -> list[float]:
    data = getattr(response, "data", None)

    if not data:
        return []

    embedding = getattr(data[0], "embedding", None)

    if isinstance(embedding, list):
        return [float(item) for item in embedding]

    return []