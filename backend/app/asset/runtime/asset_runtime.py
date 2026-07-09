from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.asset.license import build_asset_attribution_runtime
from app.asset.models import AssetDomain
from app.repositories.asset_repository import AssetRepository


class AssetRuntime:
    def __init__(self, db: Session):
        self.repository = AssetRepository(db)

    def save_asset(self, asset: AssetDomain):
        return self.repository.save(
            provider_key=self._enum_value(asset.provider_key),
            provider_asset_id=asset.provider_asset_id,
            asset_type=self._enum_value(asset.asset_type),
            status=self._enum_value(asset.status),
            title=asset.title,
            description=asset.description,
            tags=asset.tags,
            keywords=asset.keywords,
            metadata=asset.metadata,
            local_path=asset.local_path,
            remote_url=asset.remote_url,
            thumbnail_url=asset.thumbnail_url,
            preview_url=asset.preview_url,
            checksum=asset.checksum,
            duration=asset.duration,
            width=asset.width,
            height=asset.height,
            fps=asset.fps,
            file_size=asset.file_size,
            license=asset.license,
            language=asset.language,
        )

    def save_provider_asset(
        self,
        asset,
        download_result,
        status: str = "ready",
    ):
        attribution = build_asset_attribution_runtime().build_from_provider_asset(asset)

        return self.repository.save(
            provider_key=asset.provider_key,
            provider_asset_id=asset.provider_asset_id,
            asset_type=asset.asset_type,
            status=status,
            title=asset.title,
            description=asset.description,
            tags=asset.tags,
            keywords=asset.tags,
            metadata={
                **(asset.metadata or {}),
                "download": download_result.metadata,
                "source_provider": asset.provider_key,
                "attribution": attribution.to_dict(),
            },
            local_path=download_result.local_path,
            remote_url=asset.remote_url,
            thumbnail_url=asset.thumbnail_url,
            preview_url=asset.preview_url,
            checksum=download_result.checksum,
            duration=asset.duration,
            width=asset.width,
            height=asset.height,
            fps=None,
            file_size=download_result.file_size,
            license=asset.license,
            language=None,
        )

    def load_asset_payload(self, asset_id: str) -> dict[str, Any]:
        row = self.repository.find_by_id(asset_id)

        if row is None:
            return {}

        return {
            "id": str(row.id),
            "provider_key": row.provider_key,
            "provider_asset_id": row.provider_asset_id,
            "asset_type": row.asset_type,
            "status": row.status,
            "title": row.title,
            "description": row.description,
            "tags": self._safe_json_list(row.tags_json),
            "keywords": self._safe_json_list(row.keywords_json),
            "metadata": self._safe_json_dict(row.metadata_json),
            "local_path": row.local_path,
            "remote_url": row.remote_url,
            "thumbnail_url": row.thumbnail_url,
            "preview_url": row.preview_url,
            "checksum": row.checksum,
            "duration": row.duration,
            "width": row.width,
            "height": row.height,
            "fps": row.fps,
            "file_size": row.file_size,
            "license": row.license,
            "language": row.language,
        }

    def _safe_json_list(self, value: str | None) -> list:
        if not value:
            return []

        try:
            data = json.loads(value)
        except json.JSONDecodeError:
            return []

        return data if isinstance(data, list) else []

    def _safe_json_dict(self, value: str | None) -> dict:
        if not value:
            return {}

        try:
            data = json.loads(value)
        except json.JSONDecodeError:
            return {}

        return data if isinstance(data, dict) else {}

    def _enum_value(self, value) -> str:
        return str(value.value if hasattr(value, "value") else value)