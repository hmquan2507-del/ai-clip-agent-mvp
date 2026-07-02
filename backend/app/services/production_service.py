from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.production_repository import ProductionRepository
from app.schemas.production import ProductionCreate, ProductionUpdate


class ProductionService:
    def __init__(self, db: Session):
        self.repository = ProductionRepository(db)

    def list_by_workspace(self, workspace_id: UUID):
        return self.repository.list_by_workspace(workspace_id)

    def get_by_id(self, production_id: UUID):
        production = self.repository.get_by_id(production_id)

        if production is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Production not found",
            )

        return production

    def create(self, payload: ProductionCreate):
        return self.repository.create(payload)

    def update(self, production_id: UUID, payload: ProductionUpdate):
        production = self.get_by_id(production_id)
        return self.repository.update(production, payload)

    def delete(self, production_id: UUID):
        production = self.get_by_id(production_id)
        return self.repository.soft_delete(production)