from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    Float,
    ForeignKey,
    Integer,
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

    # Populated by a real ffprobe pass at upload time
    # (app/services/upload_service.py) so the editor knows the source
    # video's real duration/resolution before the timeline or render
    # pipeline ever touches it.
    duration: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    width: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    height: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    fps: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    video_codec: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    audio_codec: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    has_audio: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )