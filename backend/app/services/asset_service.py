from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.asset_repository import AssetRepository


class AssetService:
    def __init__(self, db: Session):
        self.repository = AssetRepository(db)

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

    def delete(self, asset_id: UUID):
        asset = self.get_by_id(asset_id)
        return self.repository.soft_delete(asset)