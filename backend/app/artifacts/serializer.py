from __future__ import annotations

import hashlib
import json
from typing import Any


class ArtifactSerializer:
    def serialize(self, payload: dict[str, Any]) -> str:
        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
        )

    def deserialize(self, payload_json: str | None) -> dict[str, Any]:
        if not payload_json:
            return {}

        try:
            value = json.loads(payload_json)
        except json.JSONDecodeError:
            return {}

        return value if isinstance(value, dict) else {}

    def checksum(self, payload_json: str) -> str:
        return hashlib.sha256(
            payload_json.encode("utf-8")
        ).hexdigest()