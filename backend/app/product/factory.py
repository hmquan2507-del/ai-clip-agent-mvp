from __future__ import annotations

from app.product.adapters import (
    ProductSnapshotBuilder,
)
from app.product.lifecycle import (
    ProductStateMachine,
)
from app.product.workspace import (
    build_in_memory_product_workspace_service,
)

def build_product_state_machine() -> (
    ProductStateMachine
):
    return ProductStateMachine()


def build_product_snapshot_builder() -> (
    ProductSnapshotBuilder
):
    return ProductSnapshotBuilder()