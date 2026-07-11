from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID


def value_of(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, (datetime, UUID, Path)):
        return str(value)

    return value


def read_value(
    source: Any,
    key: str,
    default: Any = None,
) -> Any:
    if source is None:
        return default

    if isinstance(source, dict):
        return source.get(key, default)

    return getattr(source, key, default)


def to_plain_dict(source: Any) -> dict[str, Any]:
    if source is None:
        return {}

    if isinstance(source, dict):
        return {
            str(key): normalize(value)
            for key, value in source.items()
        }

    if hasattr(source, "to_dict"):
        payload = source.to_dict()

        if isinstance(payload, dict):
            return normalize(payload)

    if is_dataclass(source):
        return normalize(asdict(source))

    if hasattr(source, "__dict__"):
        return {
            key: normalize(value)
            for key, value in vars(source).items()
            if not key.startswith("_")
        }

    return {}


def normalize(value: Any) -> Any:
    value = value_of(value)

    if value is None:
        return None

    if isinstance(value, dict):
        return {
            str(key): normalize(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [
            normalize(item)
            for item in value
        ]

    if is_dataclass(value):
        return normalize(asdict(value))

    if hasattr(value, "to_dict"):
        return normalize(value.to_dict())

    if hasattr(value, "__dict__"):
        return {
            key: normalize(item)
            for key, item in vars(value).items()
            if not key.startswith("_")
        }

    return value


def float_or_none(value: Any) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def int_or_none(value: Any) -> int | None:
    if value is None:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None