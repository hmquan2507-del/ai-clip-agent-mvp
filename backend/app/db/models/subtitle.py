from __future__ import annotations

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.db.enums import SubtitleStatus, SubtitleStyle


class Subtitle(BaseEntity):
    __tablename__ = "subtitles"

    production_id: Mapped[str] = mapped_column(
        ForeignKey("productions.id"),
        index=True,
        nullable=False,
    )

    timeline_id: Mapped[str | None] = mapped_column(
        ForeignKey("timelines.id"),
        index=True,
        nullable=True,
    )

    status: Mapped[SubtitleStatus] = mapped_column(
        Enum(SubtitleStatus),
        default=SubtitleStatus.DRAFT,
        index=True,
        nullable=False,
    )

    style: Mapped[SubtitleStyle] = mapped_column(
        Enum(SubtitleStyle),
        default=SubtitleStyle.DEFAULT,
        nullable=False,
    )

    language: Mapped[str | None] = mapped_column(String, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    cues: Mapped[list["SubtitleCue"]] = relationship(
        "SubtitleCue",
        back_populates="subtitle",
        cascade="all, delete-orphan",
    )


class SubtitleCue(BaseEntity):
    __tablename__ = "subtitle_cues"

    subtitle_id: Mapped[str] = mapped_column(
        ForeignKey("subtitles.id"),
        index=True,
        nullable=False,
    )

    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)

    text: Mapped[str] = mapped_column(Text, nullable=False)
    style_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    subtitle: Mapped["Subtitle"] = relationship(
        "Subtitle",
        back_populates="cues",
    )