from app.product.api.dependencies import (
    get_product_workspace_service,
)
from app.product.api.router import router

__all__ = [
    "get_product_workspace_service",
    "router",
]