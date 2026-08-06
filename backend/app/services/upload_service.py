import uuid
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.db.enums import AssetType, UploadStatus
from app.db.models.production_asset import (
    ProductionAsset,
)
from app.media.validation.factory import (
    build_media_validation_runtime,
)
from app.repositories.production_repository import ProductionRepository
from app.services.upload_validation_service import (
    UploadValidationError,
    UploadValidationService,
)
from app.storage.base import StorageProvider
from app.storage.factory import get_storage_provider

LOCAL_UPLOAD_BASE_PATH = Path("data/uploads")


class UploadService:
    def __init__(
        self,
        db: Session,
        storage: StorageProvider | None = None,
    ):
        self.db = db
        self.production_repository = ProductionRepository(db)
        self.validation_service = UploadValidationService()
        self.media_validator = build_media_validation_runtime()
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

        # Real ffprobe pass so the editor knows the actual duration and
        # resolution before the timeline or render pipeline ever touches
        # this file - a corrupt or non-video upload is rejected here
        # instead of failing silently much later at render time.
        analysis = self.media_validator.validate(
            local_path=str(LOCAL_UPLOAD_BASE_PATH / storage_path),
            require_video=True,
        )

        if not analysis.valid:
            self.storage.delete_file(storage_path)
            raise UploadValidationError(
                "Uploaded file failed video validation: "
                + ", ".join(analysis.errors)
            )

        asset = ProductionAsset(
            production_id=production_id,
            type=AssetType.SOURCE_VIDEO,
            filename=filename,
            mime_type=file.content_type,
            size_bytes=size_bytes,
            storage_path=storage_path,
            duration=analysis.duration,
            width=analysis.width,
            height=analysis.height,
            fps=analysis.fps,
            video_codec=analysis.video_codec,
            audio_codec=analysis.audio_codec,
            has_audio=analysis.has_audio,
        )

        self.db.add(asset)

        production.status = UploadStatus.ATTACHED.value
        production.progress = 10
        production.version += 1

        self.db.add(production)
        self.db.commit()
        self.db.refresh(asset)

        return asset