from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.asset_resolver_service import AssetResolverService

router = APIRouter(
    prefix="/productions",
    tags=["Asset Resolver"],
)


@router.post("/{production_id}/asset-resolver/run")
def run_asset_resolver(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = AssetResolverService(db)
    return service.run(production_id=production_id)