from __future__ import annotations

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.db.enums import MusicMood, MusicStatus


class MusicPlan(BaseEntity):
    __tablename__ = "music_plans"

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

    status: Mapped[MusicStatus] = mapped_column(
        Enum(MusicStatus),
        default=MusicStatus.DRAFT,
        index=True,
        nullable=False,
    )

    mood: Mapped[MusicMood] = mapped_column(
        Enum(MusicMood),
        default=MusicMood.CUSTOM,
        index=True,
        nullable=False,
    )

    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    cues: Mapped[list["MusicCue"]] = relationship(
        "MusicCue",
        back_populates="music_plan",
        cascade="all, delete-orphan",
    )


class MusicCue(BaseEntity):
    __tablename__ = "music_cues"

    music_plan_id: Mapped[str] = mapped_column(
        ForeignKey("music_plans.id"),
        index=True,
        nullable=False,
    )

    asset_id: Mapped[str | None] = mapped_column(
        ForeignKey("assets.id"),
        index=True,
        nullable=True,
    )

    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)

    mood: Mapped[MusicMood] = mapped_column(
        Enum(MusicMood),
        default=MusicMood.CUSTOM,
        index=True,
        nullable=False,
    )

    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    keyword: Mapped[str | None] = mapped_column(String, nullable=True)
    volume: Mapped[float] = mapped_column(Float, default=0.35, nullable=False)
    fade_in: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    fade_out: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    music_plan: Mapped["MusicPlan"] = relationship(
        "MusicPlan",
        back_populates="cues",
    )