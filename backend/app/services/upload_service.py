from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.db.enums import AssetType, UploadStatus
from app.db.models.asset import Asset
from app.repositories.production_repository import ProductionRepository
from app.services.upload_validation_service import (
    UploadValidationError,
    UploadValidationService,
)
from app.storage.local_storage import LocalStorageProvider


class UploadService:
    def __init__(self, db: Session):
        self.db = db
        self.production_repository = ProductionRepository(db)
        self.validation_service = UploadValidationService()
        self.storage = LocalStorageProvider()

    def upload_source_video(
        self,
        production_id: UUID,
        file: UploadFile,
    ) -> Asset:
        production = self.production_repository.get_by_id(production_id)

        if production is None:
            raise UploadValidationError("Production not found.")

        self.validation_service.validate_video_file(file)

        storage_path, size_bytes = self.storage.save_upload(
            file=file,
            production_id=str(production_id),
        )

        asset = Asset(
            production_id=production_id,
            type=AssetType.SOURCE_VIDEO,
            filename=file.filename or "upload.mp4",
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