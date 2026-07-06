from __future__ import annotations

import json
from typing import Any


class MetadataManager:
    @staticmethod
    def load(metadata_json: str | None) -> dict[str, Any]:
        if not metadata_json:
            return {}

        try:
            value = json.loads(metadata_json)
        except json.JSONDecodeError:
            return {"legacy_metadata": metadata_json}

        if not isinstance(value, dict):
            return {"legacy_metadata": value}

        return value

    @staticmethod
    def dump(metadata: dict[str, Any]) -> str:
        return json.dumps(metadata, ensure_ascii=False)

    @staticmethod
    def merge_result(
        metadata_json: str | None,
        key: str,
        result: dict[str, Any],
    ) -> str:
        metadata = MetadataManager.load(metadata_json)
        metadata[key] = result
        return MetadataManager.dump(metadata)