from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RenderAsset:
    asset_id: str
    asset_type: str
    uri: str | None = None
    local_path: str | None = None
    is_placeholder: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "uri": self.uri,
            "local_path": self.local_path,
            "is_placeholder": self.is_placeholder,
            "metadata": self.metadata,
        }


@dataclass
class ResolvedAssets:
    production_id: str
    assets: list[RenderAsset] = field(default_factory=list)
    output_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "assets": [asset.to_dict() for asset in self.assets],
            "output_path": self.output_path,
            "metadata": self.metadata,
        }