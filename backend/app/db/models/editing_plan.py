from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.db.enums import EditingPlanItemAction, EditingPlanStatus


class EditingPlan(BaseEntity):
    __tablename__ = "editing_plans"

    production_id: Mapped[str] = mapped_column(
        ForeignKey("productions.id"),
        index=True,
        nullable=False,
    )

    status: Mapped[EditingPlanStatus] = mapped_column(
        Enum(EditingPlanStatus),
        default=EditingPlanStatus.DRAFT,
        index=True,
        nullable=False,
    )

    provider: Mapped[str | None] = mapped_column(String, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    items = relationship(
        "EditingPlanItem",
        back_populates="editing_plan",
        cascade="all, delete-orphan",
    )


class EditingPlanItem(BaseEntity):
    __tablename__ = "editing_plan_items"

    editing_plan_id: Mapped[str] = mapped_column(
        ForeignKey("editing_plans.id"),
        index=True,
        nullable=False,
    )

    start_time: Mapped[float] = mapped_column(nullable=False)
    end_time: Mapped[float] = mapped_column(nullable=False)

    action: Mapped[EditingPlanItemAction] = mapped_column(
        Enum(EditingPlanItemAction),
        index=True,
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    editing_plan = relationship(
        "EditingPlan",
        back_populates="items",
    )