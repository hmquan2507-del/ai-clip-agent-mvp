from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.production_service import ProductionService


def get_production_service(
    db: Session = Depends(get_db),
) -> ProductionService:
    return ProductionService(db)