from __future__ import annotations

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.db.enums import RenderAssetType, RenderPlanStatus, RenderTrackType


class RenderPlan(BaseEntity):
    __tablename__ = "render_plans"

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

    status: Mapped[RenderPlanStatus] = mapped_column(
        Enum(RenderPlanStatus),
        default=RenderPlanStatus.DRAFT,
        index=True,
        nullable=False,
    )

    duration_seconds: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    resolution: Mapped[str] = mapped_column(String, default="1080x1920", nullable=False)
    fps: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    tracks: Mapped[list["RenderTrack"]] = relationship(
        "RenderTrack",
        back_populates="render_plan",
        cascade="all, delete-orphan",
    )


class RenderTrack(BaseEntity):
    __tablename__ = "render_tracks"

    render_plan_id: Mapped[str] = mapped_column(
        ForeignKey("render_plans.id"),
        index=True,
        nullable=False,
    )

    type: Mapped[RenderTrackType] = mapped_column(
        Enum(RenderTrackType),
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    render_plan: Mapped["RenderPlan"] = relationship(
        "RenderPlan",
        back_populates="tracks",
    )

    assets: Mapped[list["RenderAsset"]] = relationship(
        "RenderAsset",
        back_populates="render_track",
        cascade="all, delete-orphan",
    )


class RenderAsset(BaseEntity):
    __tablename__ = "render_assets"

    render_track_id: Mapped[str] = mapped_column(
        ForeignKey("render_tracks.id"),
        index=True,
        nullable=False,
    )

    asset_id: Mapped[str | None] = mapped_column(
        ForeignKey("assets.id"),
        index=True,
        nullable=True,
    )

    type: Mapped[RenderAssetType] = mapped_column(
        Enum(RenderAssetType),
        index=True,
        nullable=False,
    )

    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)

    source_start: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_end: Mapped[float | None] = mapped_column(Float, nullable=True)

    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)

    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    render_track: Mapped["RenderTrack"] = relationship(
        "RenderTrack",
        back_populates="assets",
    )