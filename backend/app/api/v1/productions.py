from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.domain.production.dependencies import get_production_service
from app.domain.production.exceptions import ProductionNotFoundError
from app.schemas.production import (
    ProductionCreate,
    ProductionRead,
    ProductionUpdate,
)
from app.services.production_service import ProductionService

router = APIRouter(
    prefix="/productions",
    tags=["Productions"],
)


def handle_production_not_found(error: ProductionNotFoundError):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=str(error),
    )


@router.get(
    "/workspace/{workspace_id}",
    response_model=list[ProductionRead],
)
def list_productions_by_workspace(
    workspace_id: UUID,
    service: ProductionService = Depends(get_production_service),
):
    return service.list_by_workspace(workspace_id)


@router.get(
    "/{production_id}",
    response_model=ProductionRead,
)
def get_production(
    production_id: UUID,
    service: ProductionService = Depends(get_production_service),
):
    try:
        return service.get_by_id(production_id)
    except ProductionNotFoundError as error:
        handle_production_not_found(error)


@router.post(
    "",
    response_model=ProductionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_production(
    payload: ProductionCreate,
    service: ProductionService = Depends(get_production_service),
):
    return service.create(payload)


@router.patch(
    "/{production_id}",
    response_model=ProductionRead,
)
def update_production(
    production_id: UUID,
    payload: ProductionUpdate,
    service: ProductionService = Depends(get_production_service),
):
    try:
        return service.update(production_id, payload)
    except ProductionNotFoundError as error:
        handle_production_not_found(error)


@router.delete(
    "/{production_id}",
    response_model=ProductionRead,
)
def delete_production(
    production_id: UUID,
    service: ProductionService = Depends(get_production_service),
):
    try:
        return service.delete(production_id)
    except ProductionNotFoundError as error:
        handle_production_not_found(error)