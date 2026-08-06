from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.production.dependencies import get_production_service
from app.domain.production.exceptions import ProductionNotFoundError
from app.schemas.production import (
    ProductionCreate,
    ProductionRead,
    ProductionUpdate,
)
from app.services.production_service import ProductionService
from app.services.render_export_service import get_latest_export

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
    "",
    response_model=list[ProductionRead],
)
@router.get(
    "/",
    response_model=list[ProductionRead],
    include_in_schema=False,
)
def list_productions(
    workspace_id: UUID = UUID("00000000-0000-0000-0000-000000000001"),
    service: ProductionService = Depends(get_production_service),
):
    return service.list_by_workspace(workspace_id)


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


@router.get(
    "/{production_id}/download",
)
def download_production_video(
    production_id: UUID,
    service: ProductionService = Depends(get_production_service),
    db: Session = Depends(get_db),
):
    try:
        service.get_by_id(production_id)
    except ProductionNotFoundError as error:
        handle_production_not_found(error)

    export = get_latest_export(db, production_id)

    if export is None or export.status != "completed" or not export.storage_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "This production has not been rendered yet. "
                "Submit a render before downloading."
            ),
        )

    file_path = Path(export.storage_path)

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The rendered file for this production is missing on disk.",
        )

    return FileResponse(
        path=str(file_path),
        media_type="video/mp4",
        filename=f"{production_id}.mp4",
    )


@router.post(
    "",
    response_model=ProductionRead,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/",
    response_model=ProductionRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
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