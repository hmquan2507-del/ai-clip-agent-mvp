class ProductionError(Exception):
    """Base exception for Production domain."""


class ProductionNotFoundError(ProductionError):
    """Raised when a production cannot be found."""

    def __init__(self, production_id: str):
        self.production_id = production_id
        super().__init__(f"Production not found: {production_id}")