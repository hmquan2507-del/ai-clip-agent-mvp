from sqlalchemy.orm import Session

from app.db.models.production_asset import (
    ProductionAsset,
)
from app.db.models.queue_job import QueueJob


class TranscriptRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_source_video_asset(self, production_id):
        return (
            self.db.query(ProductionAsset)
            .filter(
            ProductionAsset.production_id
            == str(production_id),
            ProductionAsset.type
            == AssetType.SOURCE_VIDEO.value,
            ProductionAsset.deleted_at.is_(None),
        )
        .order_by(
            ProductionAsset.created_at.desc()
    )
    .first()
)
    def save_transcript_result(
        self,
        job: QueueJob,
        transcript_text: str,
        provider: str,
        language: str | None = None,
        duration: float | None = None,
    ) -> QueueJob:
        job.result = {
            "provider": provider,
            "language": language,
            "duration": duration,
            "text": transcript_text,
        }.__str__()

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        return job