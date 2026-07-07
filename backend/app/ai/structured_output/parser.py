from __future__ import annotations

import json
from typing import Any


class StructuredOutputParser:
    def parse_json(self, text: str) -> dict[str, Any]:
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return {}

        return value if isinstance(value, dict) else {}