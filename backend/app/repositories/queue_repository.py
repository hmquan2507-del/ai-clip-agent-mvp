from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.enums import QueueStatus, QueueType
from app.db.models.queue_job import QueueJob


class QueueRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        production_id: UUID,
        queue_type: QueueType,
        payload: str | None = None,
    ) -> QueueJob:
        job = QueueJob(
            production_id=production_id,
            type=queue_type,
            status=QueueStatus.PENDING,
            progress=0,
            payload=payload,
        )

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        return job

    def get_by_id(
        self,
        queue_id: UUID,
    ) -> QueueJob | None:
        statement = select(QueueJob).where(
            QueueJob.id == queue_id,
            QueueJob.deleted_at.is_(None),
        )

        return self.db.scalars(statement).first()

    def get_latest_completed_transcript(
        self,
        production_id: UUID,
    ) -> QueueJob | None:
        statement = (
            select(QueueJob)
            .where(
                QueueJob.production_id == production_id,
                QueueJob.type == QueueType.TRANSCRIPT,
                QueueJob.status == QueueStatus.COMPLETED,
                QueueJob.deleted_at.is_(None),
            )
            .order_by(QueueJob.created_at.desc())
        )

        return self.db.scalars(statement).first()
    def list_by_production(
        self,
        production_id: UUID,
    ) -> list[QueueJob]:
        statement = (
            select(QueueJob)
            .where(
                QueueJob.production_id == production_id,
                QueueJob.deleted_at.is_(None),
            )
            .order_by(QueueJob.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    
    def update(self, job: QueueJob) -> QueueJob:
        job.version += 1

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        return job
    
    