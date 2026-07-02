from sqlalchemy import Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.db.enums import RenderJobStatus


class RenderJob(BaseEntity):
    __tablename__ = "render_jobs"

    production_id: Mapped[str] = mapped_column(ForeignKey("productions.id"))

    status: Mapped[RenderJobStatus] = mapped_column(
        Enum(RenderJobStatus),
        default=RenderJobStatus.QUEUED,
        index=True,
    )
    progress: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    production = relationship("Production", back_populates="render_jobs")