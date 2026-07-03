from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.asset import AssetRead
from app.services.asset_service import AssetService

router = APIRouter(
    prefix="/assets",
    tags=["Assets"],
)


def get_asset_service(db: Session = Depends(get_db)) -> AssetService:
    return AssetService(db)


@router.get(
    "/production/{production_id}",
    response_model=list[AssetRead],
)
def list_assets_by_production(
    production_id: UUID,
    service: AssetService = Depends(get_asset_service),
):
    return service.list_by_production(production_id)


@router.get(
    "/{asset_id}",
    response_model=AssetRead,
)
def get_asset(
    asset_id: UUID,
    service: AssetService = Depends(get_asset_service),
):
    return service.get_by_id(asset_id)


@router.get("/{asset_id}/url")
def get_asset_url(
    asset_id: UUID,
    service: AssetService = Depends(get_asset_service),
):
    return {
        "url": service.get_public_url(asset_id),
    }


@router.get("/{asset_id}/signed-url")
def get_signed_asset_url(
    asset_id: UUID,
    service: AssetService = Depends(get_asset_service),
):
    return {
        "url": service.get_signed_url(asset_id),
    }


@router.delete(
    "/{asset_id}",
    response_model=AssetRead,
)
def delete_asset(
    asset_id: UUID,
    service: AssetService = Depends(get_asset_service),
):
    return service.delete(asset_id)