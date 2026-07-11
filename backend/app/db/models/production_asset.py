from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import BaseEntity


class ProductionAsset(BaseEntity):
    __tablename__ = "production_assets"

    production_id: Mapped[str] = mapped_column(
        ForeignKey(
            "productions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    filename: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    mime_type: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    size_bytes: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    storage_path: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )