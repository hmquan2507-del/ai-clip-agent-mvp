from __future__ import annotations

from app.product.contracts.enums import (
    ProductAction,
    ProductProductionStatus,
    ProductStage,
)


class InvalidProductStateTransitionError(
    ValueError
):
    pass


class ProductStateMachine:
    TRANSITIONS: dict[
        ProductProductionStatus,
        set[ProductProductionStatus],
    ] = {
        ProductProductionStatus.DRAFT: {
            ProductProductionStatus.UPLOADING,
            ProductProductionStatus.CANCELLED,
        },
        ProductProductionStatus.UPLOADING: {
            ProductProductionStatus.UPLOADED,
            ProductProductionStatus.FAILED,
            ProductProductionStatus.CANCELLED,
        },
        ProductProductionStatus.UPLOADED: {
            ProductProductionStatus.QUEUED,
            ProductProductionStatus.UPLOADING,
            ProductProductionStatus.CANCELLED,
        },
        ProductProductionStatus.QUEUED: {
            ProductProductionStatus.TRANSCRIBING,
            ProductProductionStatus.FAILED,
            ProductProductionStatus.CANCELLED,
        },
        ProductProductionStatus.TRANSCRIBING: {
            ProductProductionStatus.ANALYZING,
            ProductProductionStatus.FAILED,
            ProductProductionStatus.CANCELLED,
        },
        ProductProductionStatus.ANALYZING: {
            ProductProductionStatus.PLANNING,
            ProductProductionStatus.FAILED,
            ProductProductionStatus.CANCELLED,
        },
        ProductProductionStatus.PLANNING: {
            ProductProductionStatus.RESOLVING_ASSETS,
            ProductProductionStatus.FAILED,
            ProductProductionStatus.CANCELLED,
        },
        ProductProductionStatus.RESOLVING_ASSETS: {
            ProductProductionStatus.BUILDING_TIMELINE,
            ProductProductionStatus.FAILED,
            ProductProductionStatus.CANCELLED,
        },
        ProductProductionStatus.BUILDING_TIMELINE: {
            ProductProductionStatus.RENDERING_PREVIEW,
            ProductProductionStatus.FAILED,
            ProductProductionStatus.CANCELLED,
        },
        ProductProductionStatus.RENDERING_PREVIEW: {
            ProductProductionStatus.READY_FOR_REVIEW,
            ProductProductionStatus.FAILED,
            ProductProductionStatus.CANCELLED,
        },
        ProductProductionStatus.READY_FOR_REVIEW: {
            ProductProductionStatus.RENDERING_PREVIEW,
            ProductProductionStatus.RENDERING_FINAL,
            ProductProductionStatus.CANCELLED,
        },
        ProductProductionStatus.RENDERING_FINAL: {
            ProductProductionStatus.QUALITY_CHECK,
            ProductProductionStatus.FAILED,
            ProductProductionStatus.CANCELLED,
        },
        ProductProductionStatus.QUALITY_CHECK: {
            ProductProductionStatus.COMPLETED,
            ProductProductionStatus.READY_FOR_REVIEW,
            ProductProductionStatus.FAILED,
        },
        ProductProductionStatus.COMPLETED: {
            ProductProductionStatus.RENDERING_FINAL,
        },
        ProductProductionStatus.FAILED: {
            ProductProductionStatus.QUEUED,
            ProductProductionStatus.RENDERING_PREVIEW,
            ProductProductionStatus.RENDERING_FINAL,
            ProductProductionStatus.CANCELLED,
        },
        ProductProductionStatus.CANCELLED: set(),
    }

    STATUS_STAGE_MAP: dict[
        ProductProductionStatus,
        ProductStage,
    ] = {
        ProductProductionStatus.DRAFT: (
            ProductStage.PROJECT_SETUP
        ),
        ProductProductionStatus.UPLOADING: (
            ProductStage.UPLOAD
        ),
        ProductProductionStatus.UPLOADED: (
            ProductStage.UPLOAD
        ),
        ProductProductionStatus.QUEUED: (
            ProductStage.QUEUE
        ),
        ProductProductionStatus.TRANSCRIBING: (
            ProductStage.TRANSCRIPT
        ),
        ProductProductionStatus.ANALYZING: (
            ProductStage.CONTENT_ANALYSIS
        ),
        ProductProductionStatus.PLANNING: (
            ProductStage.AI_PLANNING
        ),
        ProductProductionStatus.RESOLVING_ASSETS: (
            ProductStage.ASSET_RESOLUTION
        ),
        ProductProductionStatus.BUILDING_TIMELINE: (
            ProductStage.TIMELINE
        ),
        ProductProductionStatus.RENDERING_PREVIEW: (
            ProductStage.PREVIEW_RENDER
        ),
        ProductProductionStatus.READY_FOR_REVIEW: (
            ProductStage.REVIEW
        ),
        ProductProductionStatus.RENDERING_FINAL: (
            ProductStage.FINAL_RENDER
        ),
        ProductProductionStatus.QUALITY_CHECK: (
            ProductStage.QUALITY
        ),
        ProductProductionStatus.COMPLETED: (
            ProductStage.EXPORT
        ),
        ProductProductionStatus.FAILED: (
            ProductStage.FAILED
        ),
        ProductProductionStatus.CANCELLED: (
            ProductStage.CANCELLED
        ),
    }

    def can_transition(
        self,
        current_status: ProductProductionStatus | str,
        next_status: ProductProductionStatus | str,
    ) -> bool:
        current = ProductProductionStatus(
            current_status
        )
        target = ProductProductionStatus(
            next_status
        )

        return target in self.TRANSITIONS[current]

    def transition(
        self,
        current_status: ProductProductionStatus | str,
        next_status: ProductProductionStatus | str,
    ) -> ProductProductionStatus:
        current = ProductProductionStatus(
            current_status
        )
        target = ProductProductionStatus(
            next_status
        )

        if not self.can_transition(
            current_status=current,
            next_status=target,
        ):
            raise InvalidProductStateTransitionError(
                "Invalid product production state "
                f"transition: {current.value} "
                f"-> {target.value}"
            )

        return target

    def stage_for_status(
        self,
        status: ProductProductionStatus | str,
    ) -> ProductStage:
        normalized = ProductProductionStatus(
            status
        )

        return self.STATUS_STAGE_MAP[normalized]

    def allowed_actions(
        self,
        status: ProductProductionStatus | str,
    ) -> list[ProductAction]:
        value = ProductProductionStatus(status)

        mapping: dict[
            ProductProductionStatus,
            list[ProductAction],
        ] = {
            ProductProductionStatus.DRAFT: [
                ProductAction.EDIT_DETAILS,
                ProductAction.START_UPLOAD,
                ProductAction.DELETE_PRODUCTION,
            ],
            ProductProductionStatus.UPLOADING: [
                ProductAction.CANCEL_UPLOAD,
            ],
            ProductProductionStatus.UPLOADED: [
                ProductAction.START_UPLOAD,
                ProductAction.RUN_AI_PIPELINE,
                ProductAction.DELETE_PRODUCTION,
            ],
            ProductProductionStatus.QUEUED: [
                ProductAction.CANCEL_PIPELINE,
            ],
            ProductProductionStatus.TRANSCRIBING: [
                ProductAction.CANCEL_PIPELINE,
            ],
            ProductProductionStatus.ANALYZING: [
                ProductAction.CANCEL_PIPELINE,
            ],
            ProductProductionStatus.PLANNING: [
                ProductAction.CANCEL_PIPELINE,
            ],
            ProductProductionStatus.RESOLVING_ASSETS: [
                ProductAction.CANCEL_PIPELINE,
            ],
            ProductProductionStatus.BUILDING_TIMELINE: [
                ProductAction.CANCEL_PIPELINE,
            ],
            ProductProductionStatus.RENDERING_PREVIEW: [
                ProductAction.CANCEL_PIPELINE,
            ],
            ProductProductionStatus.READY_FOR_REVIEW: [
                ProductAction.OPEN_REVIEW,
                ProductAction.EDIT_TIMELINE,
                ProductAction.SAVE_TIMELINE,
                ProductAction.RENDER_PREVIEW,
                ProductAction.RENDER_FINAL,
                ProductAction.DELETE_PRODUCTION,
            ],
            ProductProductionStatus.RENDERING_FINAL: [
                ProductAction.CANCEL_PIPELINE,
            ],
            ProductProductionStatus.QUALITY_CHECK: [],
            ProductProductionStatus.COMPLETED: [
                ProductAction.OPEN_REVIEW,
                ProductAction.EDIT_TIMELINE,
                ProductAction.RENDER_FINAL,
                ProductAction.DOWNLOAD_VIDEO,
                ProductAction.DOWNLOAD_SUBTITLE,
                ProductAction.DOWNLOAD_THUMBNAIL,
                ProductAction.DOWNLOAD_TIMELINE,
                ProductAction.DELETE_PRODUCTION,
            ],
            ProductProductionStatus.FAILED: [
                ProductAction.RETRY_PIPELINE,
                ProductAction.OPEN_REVIEW,
                ProductAction.DELETE_PRODUCTION,
            ],
            ProductProductionStatus.CANCELLED: [
                ProductAction.DELETE_PRODUCTION,
            ],
        }

        return list(mapping[value])