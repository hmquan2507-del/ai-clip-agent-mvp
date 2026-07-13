from __future__ import annotations
from app.product.workspace.loaders import InMemoryProductWorkspaceLoader
from app.product.workspace.service import ProductWorkspaceService
from app.review.builders.workspace_builder import ReviewWorkspaceBuilder
from app.review.services.review_workspace_service import ReviewWorkspaceService


def create_review_workspace_service() -> ReviewWorkspaceService:
    """
    Factory function to create a ReviewWorkspaceService with in-memory dependencies.
    """
    loader = InMemoryProductWorkspaceLoader()
    
    product_workspace_service = ProductWorkspaceService(
        production_loader=loader,
        timeline_loader=loader,
        artifact_loader=loader,
        quality_loader=loader,
        ai_summary_loader=loader,
        issue_loader=loader,
    )
    
    review_workspace_builder = ReviewWorkspaceBuilder()
    
    review_workspace_service = ReviewWorkspaceService(
        product_workspace_service=product_workspace_service,
        workspace_builder=review_workspace_builder,
    )
    
    return review_workspace_service

# For convenience, we can alias the function to the name requested in the prompt
build_review_workspace = create_review_workspace_service
