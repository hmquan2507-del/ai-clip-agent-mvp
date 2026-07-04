from __future__ import annotations

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.db.enums import TimelineClipType, TimelineStatus, TimelineTrackType


class Timeline(BaseEntity):
    __tablename__ = "timelines"

    production_id: Mapped[str] = mapped_column(
        ForeignKey("productions.id"),
        index=True,
        nullable=False,
    )

    editing_plan_id: Mapped[str | None] = mapped_column(
        ForeignKey("editing_plans.id"),
        index=True,
        nullable=True,
    )

    status: Mapped[TimelineStatus] = mapped_column(
        Enum(TimelineStatus),
        default=TimelineStatus.DRAFT,
        index=True,
        nullable=False,
    )

    duration_seconds: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    tracks = relationship(
        "TimelineTrack",
        back_populates="timeline",
        cascade="all, delete-orphan",
    )


class TimelineTrack(BaseEntity):
    __tablename__ = "timeline_tracks"

    timeline_id: Mapped[str] = mapped_column(
        ForeignKey("timelines.id"),
        index=True,
        nullable=False,
    )

    type: Mapped[TimelineTrackType] = mapped_column(
        Enum(TimelineTrackType),
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    timeline = relationship(
        "Timeline",
        back_populates="tracks",
    )

    clips = relationship(
        "TimelineClip",
        back_populates="track",
        cascade="all, delete-orphan",
    )


class TimelineClip(BaseEntity):
    __tablename__ = "timeline_clips"

    track_id: Mapped[str] = mapped_column(
        ForeignKey("timeline_tracks.id"),
        index=True,
        nullable=False,
    )

    asset_id: Mapped[str | None] = mapped_column(
        ForeignKey("assets.id"),
        index=True,
        nullable=True,
    )

    source_start: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_end: Mapped[float | None] = mapped_column(Float, nullable=True)

    timeline_start: Mapped[float] = mapped_column(Float, nullable=False)
    timeline_end: Mapped[float] = mapped_column(Float, nullable=False)

    type: Mapped[TimelineClipType] = mapped_column(
        Enum(TimelineClipType),
        index=True,
        nullable=False,
    )

    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    track = relationship(
        "TimelineTrack",
        back_populates="clips",
    )