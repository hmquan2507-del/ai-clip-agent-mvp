from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.db.enums import ClipStatus


class Clip(BaseEntity):
    __tablename__ = "clips"

    production_id: Mapped[str] = mapped_column(ForeignKey("productions.id"))

    title: Mapped[str | None] = mapped_column(String, nullable=True)
    start_seconds: Mapped[float] = mapped_column(Float)
    end_seconds: Mapped[float] = mapped_column(Float)

    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    status: Mapped[ClipStatus] = mapped_column(
        Enum(ClipStatus),
        default=ClipStatus.DRAFT,
        index=True,
    )

    production = relationship("Production", back_populates="clips")