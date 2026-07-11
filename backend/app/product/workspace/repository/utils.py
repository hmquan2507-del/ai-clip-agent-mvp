from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable
from uuid import UUID


class RepositoryMethodNotFoundError(
    AttributeError
):
    pass


def normalize_production_id(
    production_id: str,
) -> str:
    value = str(production_id).strip()

    if not value:
        raise ValueError(
            "production_id is required."
        )

    return value


def id_candidates(
    production_id: str,
) -> list[Any]:
    candidates: list[Any] = [
        production_id,
    ]

    try:
        candidates.append(
            UUID(production_id)
        )
    except ValueError:
        pass

    return candidates


def call_first_supported(
    target: Any,
    method_names: Iterable[str],
    *,
    production_id: str,
    default: Any = None,
    required: bool = False,
) -> Any:
    if target is None:
        if required:
            raise RepositoryMethodNotFoundError(
                "Repository dependency is missing."
            )

        return default

    available_method = False
    last_type_error: TypeError | None = None

    for method_name in method_names:
        method = getattr(
            target,
            method_name,
            None,
        )

        if not callable(method):
            continue

        available_method = True

        for candidate in id_candidates(
            production_id
        ):
            try:
                return method(candidate)
            except TypeError as error:
                last_type_error = error
                continue

    if required:
        if available_method and last_type_error:
            raise RepositoryMethodNotFoundError(
                "Repository methods were found but "
                "their signatures were incompatible."
            ) from last_type_error

        raise RepositoryMethodNotFoundError(
            "Repository does not implement any "
            "supported method: "
            f"{', '.join(method_names)}"
        )

    return default


def ensure_list(
    value: Any,
) -> list[Any]:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    if isinstance(value, set):
        return list(value)

    if isinstance(value, dict):
        for key in (
            "items",
            "results",
            "artifacts",
            "issues",
            "data",
        ):
            nested = value.get(key)

            if isinstance(nested, list):
                return nested

        return [value]

    try:
        return list(value)
    except TypeError:
        return [value]


def read_json_file(
    path: Path,
) -> dict[str, Any] | list[Any] | None:
    if not path.exists():
        return None

    if not path.is_file():
        return None

    try:
        payload = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ):
        return None

    if isinstance(payload, (dict, list)):
        return payload

    return None


def find_first_json(
    candidates: Iterable[Path],
) -> dict[str, Any] | list[Any] | None:
    for candidate in candidates:
        payload = read_json_file(
            candidate
        )

        if payload is not None:
            return payload

    return None


def value_of(
    source: Any,
    key: str,
    default: Any = None,
) -> Any:
    if source is None:
        return default

    if isinstance(source, dict):
        return source.get(key, default)

    return getattr(source, key, default)


def plain_value(
    value: Any,
) -> Any:
    if value is None:
        return None

    if hasattr(value, "value"):
        return value.value

    return value