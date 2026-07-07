from __future__ import annotations

from typing import Any


class StructuredOutputValidator:
    def validate(
        self,
        data: dict[str, Any],
        required_keys: list[str] | None = None,
    ) -> list[str]:
        errors: list[str] = []

        if not isinstance(data, dict):
            return ["output_is_not_object"]

        for key in required_keys or []:
            if key not in data:
                errors.append(f"missing_required_key:{key}")

        return errors