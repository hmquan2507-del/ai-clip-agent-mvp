from __future__ import annotations

from sqlalchemy.orm import Session

from app.timeline.asset_injector.runtime import TimelineAssetInjectionRuntime


def build_timeline_asset_injection_runtime(
    db: Session,
) -> TimelineAssetInjectionRuntime:
    return TimelineAssetInjectionRuntime(db=db)