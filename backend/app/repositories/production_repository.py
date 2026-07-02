from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.production import Production
from app.schemas.production import ProductionCreate, ProductionUpdate


class ProductionRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_workspace(self, workspace_id: UUID) -> list[Production]:
        statement = (
            select(Production)
            .where(Production.workspace_id == workspace_id)
            .where(Production.deleted_at.is_(None))
            .order_by(Production.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def get_by_id(self, production_id: UUID) -> Production | None:
        statement = (
            select(Production)
            .where(Production.id == production_id)
            .where(Production.deleted_at.is_(None))
        )

        return self.db.scalars(statement).first()

    def create(self, payload: ProductionCreate) -> Production:
        production = Production(
            workspace_id=payload.workspace_id,
            title=payload.title,
            description=payload.description,
            style=payload.style,
        )

        self.db.add(production)
        self.db.commit()
        self.db.refresh(production)

        return production

    def update(
        self,
        production: Production,
        payload: ProductionUpdate,
    ) -> Production:
        data = payload.model_dump(exclude_unset=True)

        for field, value in data.items():
            setattr(production, field, value)

        production.version += 1

        self.db.add(production)
        self.db.commit()
        self.db.refresh(production)

        return production

    def soft_delete(self, production: Production) -> Production:
        from datetime import datetime

        production.deleted_at = datetime.utcnow()
        production.version += 1

        self.db.add(production)
        self.db.commit()
        self.db.refresh(production)

        return production