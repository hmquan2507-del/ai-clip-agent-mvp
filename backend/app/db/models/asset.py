from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.db.enums import AssetType


class Asset(BaseEntity):
    __tablename__ = "assets"

    production_id: Mapped[str] = mapped_column(ForeignKey("productions.id"))

    type: Mapped[AssetType] = mapped_column(
        Enum(AssetType),
        index=True,
    )
    filename: Mapped[str] = mapped_column(String)
    mime_type: Mapped[str | None] = mapped_column(String, nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    storage_path: Mapped[str] = mapped_column(String)

    production = relationship("Production", back_populates="assets")