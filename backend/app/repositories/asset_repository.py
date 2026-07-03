from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.asset import Asset


class AssetRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_production(self, production_id: UUID) -> list[Asset]:
        statement = (
            select(Asset)
            .where(Asset.production_id == production_id)
            .where(Asset.deleted_at.is_(None))
            .order_by(Asset.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def get_by_id(self, asset_id: UUID) -> Asset | None:
        statement = (
            select(Asset)
            .where(Asset.id == asset_id)
            .where(Asset.deleted_at.is_(None))
        )

        return self.db.scalars(statement).first()

    def soft_delete(self, asset: Asset) -> Asset:
        from datetime import datetime

        asset.deleted_at = datetime.utcnow()
        asset.version += 1

        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)

        return asset