from __future__ import annotations

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.db.enums import BrollSourceType, BrollStatus


class BrollPlan(BaseEntity):
    __tablename__ = "broll_plans"

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

    status: Mapped[BrollStatus] = mapped_column(
        Enum(BrollStatus),
        default=BrollStatus.DRAFT,
        index=True,
        nullable=False,
    )

    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    cues: Mapped[list["BrollCue"]] = relationship(
        "BrollCue",
        back_populates="broll_plan",
        cascade="all, delete-orphan",
    )


class BrollCue(BaseEntity):
    __tablename__ = "broll_cues"

    broll_plan_id: Mapped[str] = mapped_column(
        ForeignKey("broll_plans.id"),
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

    source_type: Mapped[BrollSourceType] = mapped_column(
        Enum(BrollSourceType),
        default=BrollSourceType.SUGGESTION,
        index=True,
        nullable=False,
    )

    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    keyword: Mapped[str | None] = mapped_column(String, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    broll_plan: Mapped["BrollPlan"] = relationship(
        "BrollPlan",
        back_populates="cues",
    )
    