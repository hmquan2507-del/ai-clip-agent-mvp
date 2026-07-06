from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.render_graph_service import RenderGraphService

router = APIRouter(
    prefix="/productions",
    tags=["Render Graph"],
)


@router.post("/{production_id}/render-graph/run")
def run_render_graph(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = RenderGraphService(db)
    return service.run(production_id=production_id)