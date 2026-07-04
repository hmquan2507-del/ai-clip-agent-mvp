from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.production_repository import ProductionRepository


class BaseRuntimeService:
    def __init__(self, db: Session):
        self.db = db
        self.production_repo = ProductionRepository(db)

    def ensure_production_exists(self, production_id: UUID):
        production = self.production_repo.get_by_id(production_id)

        if production is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Production not found",
            )

        return production

    def raise_missing_dependency(self, detail: str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

    def raise_not_found(self, detail: str):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )