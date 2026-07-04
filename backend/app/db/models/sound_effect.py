from __future__ import annotations

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.db.enums import SoundEffectStatus, SoundEffectType


class SoundEffectPlan(BaseEntity):
    __tablename__ = "sound_effect_plans"

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

    status: Mapped[SoundEffectStatus] = mapped_column(
        Enum(SoundEffectStatus),
        default=SoundEffectStatus.DRAFT,
        index=True,
        nullable=False,
    )

    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    cues: Mapped[list["SoundEffectCue"]] = relationship(
        "SoundEffectCue",
        back_populates="sound_effect_plan",
        cascade="all, delete-orphan",
    )


class SoundEffectCue(BaseEntity):
    __tablename__ = "sound_effect_cues"

    sound_effect_plan_id: Mapped[str] = mapped_column(
        ForeignKey("sound_effect_plans.id"),
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

    effect_type: Mapped[SoundEffectType] = mapped_column(
        Enum(SoundEffectType),
        default=SoundEffectType.CUSTOM,
        index=True,
        nullable=False,
    )

    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    keyword: Mapped[str | None] = mapped_column(String, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    sound_effect_plan: Mapped["SoundEffectPlan"] = relationship(
        "SoundEffectPlan",
        back_populates="cues",
    )