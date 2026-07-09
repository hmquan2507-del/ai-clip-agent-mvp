from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.asset import AssetLibraryItem


class AssetRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(
        self,
        provider_key: str,
        asset_type: str,
        status: str = "discovered",
        provider_asset_id: str | None = None,
        title: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        keywords: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        local_path: str | None = None,
        remote_url: str | None = None,
        thumbnail_url: str | None = None,
        preview_url: str | None = None,
        checksum: str | None = None,
        duration: float | None = None,
        width: int | None = None,
        height: int | None = None,
        fps: float | None = None,
        file_size: int | None = None,
        license: str | None = None,
        language: str | None = None,
    ) -> AssetLibraryItem:

        row = AssetLibraryItem(
            provider_key=provider_key,
            provider_asset_id=provider_asset_id,
            asset_type=asset_type,
            status=status,
            title=title,
            description=description,
            tags_json=json.dumps(tags or [], ensure_ascii=False),
            keywords_json=json.dumps(keywords or [], ensure_ascii=False),
            metadata_json=json.dumps(metadata or {}, ensure_ascii=False),
            local_path=local_path,
            remote_url=remote_url,
            thumbnail_url=thumbnail_url,
            preview_url=preview_url,
            checksum=checksum,
            duration=duration,
            width=width,
            height=height,
            fps=fps,
            file_size=file_size,
            license=license,
            language=language,
        )

        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)

        return row

    def find_by_id(
        self,
        asset_id: str,
    ) -> AssetLibraryItem | None:

        return (
            self.db.query(AssetLibraryItem)
            .filter(AssetLibraryItem.id == asset_id)
            .first()
        )

    def find_by_provider(
        self,
        provider_key: str,
        provider_asset_id: str,
    ) -> AssetLibraryItem | None:

        return (
            self.db.query(AssetLibraryItem)
            .filter(
                AssetLibraryItem.provider_key == provider_key,
                AssetLibraryItem.provider_asset_id == provider_asset_id,
            )
            .first()
        )

    def list_assets(
        self,
        asset_type: str | None = None,
        provider_key: str | None = None,
        limit: int = 50,
    ) -> list[AssetLibraryItem]:

        query = self.db.query(AssetLibraryItem)

        if asset_type:
            query = query.filter(
                AssetLibraryItem.asset_type == asset_type
            )

        if provider_key:
            query = query.filter(
                AssetLibraryItem.provider_key == provider_key
            )

        return (
            query.order_by(AssetLibraryItem.created_at.desc())
            .limit(limit)
            .all()
        )

    def delete(
        self,
        asset_id: str,
    ) -> bool:

        asset = self.find_by_id(asset_id)

        if asset is None:
            return False

        self.db.delete(asset)
        self.db.commit()

        return True
    
    def find_by_checksum(
        self,
        checksum: str,
    ) -> AssetLibraryItem | None:
        return (
            self.db.query(AssetLibraryItem)
            .filter(AssetLibraryItem.checksum == checksum)
            .first()
        )

    def find_ready_by_provider_asset(
        self,
        provider_key: str,
        provider_asset_id: str,
    ) -> AssetLibraryItem | None:
        return (
            self.db.query(AssetLibraryItem)
            .filter(
                AssetLibraryItem.provider_key == provider_key,
                AssetLibraryItem.provider_asset_id == provider_asset_id,
                AssetLibraryItem.status == "ready",
            )
            .first()
        )

    def find_ready_by_type(
        self,
        asset_type: str,
        limit: int = 50,
    ) -> list[AssetLibraryItem]:
        return (
            self.db.query(AssetLibraryItem)
            .filter(
                AssetLibraryItem.asset_type == asset_type,
                AssetLibraryItem.status == "ready",
            )
            .order_by(AssetLibraryItem.created_at.desc())
            .limit(limit)
            .all()
        )