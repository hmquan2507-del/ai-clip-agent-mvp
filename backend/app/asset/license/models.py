from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AssetAttribution:
    provider_key: str
    provider_asset_id: str
    title: str | None = None
    author: str | None = None
    source_url: str | None = None
    license: str | None = None
    requires_attribution: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_key": self.provider_key,
            "provider_asset_id": self.provider_asset_id,
            "title": self.title,
            "author": self.author,
            "source_url": self.source_url,
            "license": self.license,
            "requires_attribution": self.requires_attribution,
            "metadata": self.metadata,
        }