from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.asset_repository import AssetRepository
from app.storage.base import StorageProvider
from app.storage.factory import get_storage_provider


class AssetService:
    def __init__(
        self,
        db: Session,
        storage: StorageProvider | None = None,
    ):
        self.repository = AssetRepository(db)
        self.storage = storage or get_storage_provider()

    def list_by_production(self, production_id: UUID):
        return self.repository.list_by_production(production_id)

    def get_by_id(self, asset_id: UUID):
        asset = self.repository.get_by_id(asset_id)

        if asset is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found",
            )

        return asset

    def get_public_url(self, asset_id: UUID) -> str:
        asset = self.get_by_id(asset_id)

        return self.storage.get_public_url(
            asset.storage_path,
        )

    def get_signed_url(self, asset_id: UUID) -> str:
        asset = self.get_by_id(asset_id)

        return self.storage.get_signed_url(
            asset.storage_path,
        )

    def delete(self, asset_id: UUID):
        asset = self.get_by_id(asset_id)

        self.storage.delete_file(
            asset.storage_path,
        )

        return self.repository.soft_delete(asset)