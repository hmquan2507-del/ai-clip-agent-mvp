from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.db.enums import ExportStatus


class Export(BaseEntity):
    __tablename__ = "exports"

    production_id: Mapped[str] = mapped_column(ForeignKey("productions.id"))

    status: Mapped[ExportStatus] = mapped_column(
        Enum(ExportStatus),
        default=ExportStatus.COMPLETED,
        index=True,
    )
    format: Mapped[str] = mapped_column(String, default="mp4")
    resolution: Mapped[str | None] = mapped_column(String, nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String, nullable=True)

    production = relationship("Production", back_populates="exports")