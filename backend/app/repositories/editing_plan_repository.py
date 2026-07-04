from sqlalchemy.orm import Session, selectinload

from app.db.enums import EditingPlanStatus
from app.db.models.editing_plan import EditingPlan, EditingPlanItem


class EditingPlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_plan(
        self,
        production_id: str,
        provider: str | None = None,
    ) -> EditingPlan:
        plan = EditingPlan(
            production_id=production_id,
            provider=provider,
            status=EditingPlanStatus.PROCESSING,
        )

        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)

        return plan

    def get_by_id(self, plan_id: str) -> EditingPlan | None:
        return (
            self.db.query(EditingPlan)
            .options(selectinload(EditingPlan.items))
            .filter(EditingPlan.id == plan_id)
            .first()
        )

    def get_latest_by_production(
        self,
        production_id: str,
    ) -> EditingPlan | None:
        return (
            self.db.query(EditingPlan)
            .options(selectinload(EditingPlan.items))
            .filter(EditingPlan.production_id == production_id)
            .order_by(EditingPlan.created_at.desc())
            .first()
        )

    def add_item(
        self,
        plan_id: str,
        start_time: float,
        end_time: float,
        action,
        reason: str | None = None,
        priority: int = 0,
        metadata_json: str | None = None,
    ) -> EditingPlanItem:
        item = EditingPlanItem(
            editing_plan_id=plan_id,
            start_time=start_time,
            end_time=end_time,
            action=action,
            reason=reason,
            priority=priority,
            metadata_json=metadata_json,
        )

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return item

    def mark_completed(
        self,
        plan_id: str,
        summary: str | None = None,
    ) -> EditingPlan:
        plan = self.get_by_id(plan_id)
        if plan is None:
            raise ValueError("Editing plan not found")

        plan.status = EditingPlanStatus.COMPLETED
        plan.summary = summary

        self.db.commit()
        self.db.refresh(plan)

        return plan

    def mark_failed(
        self,
        plan_id: str,
        error_message: str,
    ) -> EditingPlan:
        plan = self.get_by_id(plan_id)
        if plan is None:
            raise ValueError("Editing plan not found")

        plan.status = EditingPlanStatus.FAILED
        plan.summary = error_message

        self.db.commit()
        self.db.refresh(plan)

        return plan

    def delete_by_production(self, production_id: str) -> bool:
        plan = self.get_latest_by_production(production_id)
        if plan is None:
            return False

        self.db.delete(plan)
        self.db.commit()

        return True