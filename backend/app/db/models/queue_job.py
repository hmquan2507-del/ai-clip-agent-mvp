from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.db.enums import QueueStatus, QueueType


class QueueJob(BaseEntity):
    __tablename__ = "queue_jobs"

    production_id: Mapped[str] = mapped_column(ForeignKey("productions.id"))

    type: Mapped[QueueType] = mapped_column(
        Enum(QueueType),
        index=True,
    )
    status: Mapped[QueueStatus] = mapped_column(
        Enum(QueueStatus),
        default=QueueStatus.PENDING,
        index=True,
    )

    progress: Mapped[int] = mapped_column(Integer, default=0)

    payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    worker_name: Mapped[str | None] = mapped_column(String, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    production = relationship("Production", back_populates="queue_jobs")