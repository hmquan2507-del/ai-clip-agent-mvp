import uuid
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.db.enums import AssetType, UploadStatus
from app.db.models.production_asset import (
    ProductionAsset,
)
from app.repositories.production_repository import ProductionRepository
from app.services.upload_validation_service import (
    UploadValidationError,
    UploadValidationService,
)
from app.storage.base import StorageProvider
from app.storage.factory import get_storage_provider


class UploadService:
    def __init__(
        self,
        db: Session,
        storage: StorageProvider | None = None,
    ):
        self.db = db
        self.production_repository = ProductionRepository(db)
        self.validation_service = UploadValidationService()
        self.storage = storage or get_storage_provider()

    def upload_source_video(
        self,
        production_id: UUID,
        file: UploadFile,
        ) -> ProductionAsset:        
        production = self.production_repository.get_by_id(production_id)

        if production is None:
            raise UploadValidationError("Production not found.")

        self.validation_service.validate_video_file(file)

        filename = file.filename or "upload.mp4"
        object_key = f"{production_id}/{uuid.uuid4()}_{filename}"

        storage_path = self.storage.save_file(
            file=file.file,
            object_key=object_key,
            content_type=file.content_type,
        )

        size_bytes = None

        try:
            file.file.seek(0, 2)
            size_bytes = file.file.tell()
            file.file.seek(0)
        except Exception:
            size_bytes = None

        asset = ProductionAsset(
            production_id=production_id,
            type=AssetType.SOURCE_VIDEO,
            filename=filename,
            mime_type=file.content_type,
            size_bytes=size_bytes,
            storage_path=storage_path,
        )

        self.db.add(asset)

        production.status = UploadStatus.ATTACHED.value
        production.progress = 10
        production.version += 1

        self.db.add(production)
        self.db.commit()
        self.db.refresh(asset)

        return asset