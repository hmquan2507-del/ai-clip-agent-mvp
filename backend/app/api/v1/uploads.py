from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.upload import UploadRead
from app.services.upload_service import UploadService
from app.services.upload_validation_service import UploadValidationError

router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
)


def get_upload_service(db: Session = Depends(get_db)) -> UploadService:
    return UploadService(db)


@router.post(
    "/production/{production_id}/source-video",
    response_model=UploadRead,
    status_code=status.HTTP_201_CREATED,
)
def upload_source_video(
    production_id: UUID,
    file: UploadFile = File(...),
    service: UploadService = Depends(get_upload_service),
):
    try:
        return service.upload_source_video(
            production_id=production_id,
            file=file,
        )
    except UploadValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error