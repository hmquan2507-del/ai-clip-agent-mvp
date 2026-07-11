from __future__ import annotations

from typing import Any

from app.product.contracts import (
    ProductFailure,
    ProductProductionSnapshot,
    ProductProgress,
    ProductProductionStatus,
    ProductStage,
)
from app.product.lifecycle import ProductStateMachine
from app.product.adapters.utils import (
    int_or_none,
    read_value,
    value_of,
)


class ProductProductionAdapter:
    def __init__(
        self,
        state_machine: ProductStateMachine | None = None,
    ):
        self.state_machine = (
            state_machine or ProductStateMachine()
        )

    def adapt(
        self,
        production: Any,
        *,
        status: ProductProductionStatus | str | None = None,
        stage: ProductStage | str | None = None,
        progress: float | None = None,
        progress_message: str | None = None,
        failure: ProductFailure | None = None,
    ) -> ProductProductionSnapshot:
        production_id = str(
            read_value(
                production,
                "id",
                read_value(
                    production,
                    "production_id",
                    "",
                ),
            )
        )

        if not production_id:
            raise ValueError(
                "Production adapter requires production_id."
            )

        resolved_status = self._resolve_status(
            production=production,
            explicit_status=status,
        )

        resolved_stage = (
            ProductStage(stage)
            if stage is not None
            else self.state_machine.stage_for_status(
                resolved_status
            )
        )

        resolved_progress = (
            float(progress)
            if progress is not None
            else self._default_progress(
                resolved_status
            )
        )

        message = (
            progress_message
            or self._default_message(
                resolved_status
            )
        )

        version = int_or_none(
            read_value(production, "version", 1)
        ) or 1

        name = str(
            read_value(
                production,
                "name",
                read_value(
                    production,
                    "title",
                    "Dự án video chưa đặt tên",
                ),
            )
        )

        return ProductProductionSnapshot(
            production_id=production_id,
            name=name,
            status=resolved_status,
            stage=resolved_stage,
            progress=ProductProgress(
                stage=resolved_stage,
                status=resolved_status,
                progress=resolved_progress,
                message=message,
            ),
            version=version,
            platform=read_value(
                production,
                "platform",
            ),
            editing_style=read_value(
                production,
                "editing_style",
            ),
            language=str(
                read_value(
                    production,
                    "language",
                    "vi",
                )
            ),
            allowed_actions=(
                self.state_machine.allowed_actions(
                    resolved_status
                )
            ),
            failure=failure,
            created_at=self._string_or_none(
                read_value(
                    production,
                    "created_at",
                )
            ),
            updated_at=self._string_or_none(
                read_value(
                    production,
                    "updated_at",
                )
            ),
            metadata={
                "adapter": (
                    "ProductProductionAdapter"
                ),
                "source_status": value_of(
                    read_value(
                        production,
                        "status",
                    )
                ),
            },
        )

    def _resolve_status(
        self,
        production: Any,
        explicit_status: (
            ProductProductionStatus | str | None
        ),
    ) -> ProductProductionStatus:
        if explicit_status is not None:
            return ProductProductionStatus(
                explicit_status
            )

        raw_status = value_of(
            read_value(
                production,
                "product_status",
                read_value(
                    production,
                    "status",
                    "draft",
                ),
            )
        )

        aliases = {
            "created": "draft",
            "pending": "queued",
            "processing": "analyzing",
            "ready": "ready_for_review",
            "rendering": "rendering_final",
            "done": "completed",
            "success": "completed",
            "error": "failed",
        }

        normalized = aliases.get(
            str(raw_status).lower(),
            str(raw_status).lower(),
        )

        try:
            return ProductProductionStatus(
                normalized
            )
        except ValueError:
            return ProductProductionStatus.DRAFT

    def _default_progress(
        self,
        status: ProductProductionStatus,
    ) -> float:
        mapping = {
            ProductProductionStatus.DRAFT: 0,
            ProductProductionStatus.UPLOADING: 5,
            ProductProductionStatus.UPLOADED: 10,
            ProductProductionStatus.QUEUED: 12,
            ProductProductionStatus.TRANSCRIBING: 22,
            ProductProductionStatus.ANALYZING: 35,
            ProductProductionStatus.PLANNING: 48,
            ProductProductionStatus.RESOLVING_ASSETS: 60,
            ProductProductionStatus.BUILDING_TIMELINE: 72,
            ProductProductionStatus.RENDERING_PREVIEW: 85,
            ProductProductionStatus.READY_FOR_REVIEW: 100,
            ProductProductionStatus.RENDERING_FINAL: 90,
            ProductProductionStatus.QUALITY_CHECK: 96,
            ProductProductionStatus.COMPLETED: 100,
            ProductProductionStatus.FAILED: 0,
            ProductProductionStatus.CANCELLED: 0,
        }

        return float(mapping[status])

    def _default_message(
        self,
        status: ProductProductionStatus,
    ) -> str:
        mapping = {
            ProductProductionStatus.DRAFT:
                "Dự án đang được chuẩn bị.",
            ProductProductionStatus.UPLOADING:
                "Đang tải video lên.",
            ProductProductionStatus.UPLOADED:
                "Video đã được tải lên.",
            ProductProductionStatus.QUEUED:
                "Dự án đang chờ xử lý.",
            ProductProductionStatus.TRANSCRIBING:
                "AI đang đọc nội dung video.",
            ProductProductionStatus.ANALYZING:
                "AI đang phân tích nội dung.",
            ProductProductionStatus.PLANNING:
                "AI đang lên kế hoạch dựng video.",
            ProductProductionStatus.RESOLVING_ASSETS:
                "AI đang tìm video minh họa và âm thanh.",
            ProductProductionStatus.BUILDING_TIMELINE:
                "AI đang dựng dòng thời gian.",
            ProductProductionStatus.RENDERING_PREVIEW:
                "Đang tạo bản xem trước.",
            ProductProductionStatus.READY_FOR_REVIEW:
                "Video đã sẵn sàng để xem và chỉnh sửa.",
            ProductProductionStatus.RENDERING_FINAL:
                "Đang xuất video hoàn chỉnh.",
            ProductProductionStatus.QUALITY_CHECK:
                "Đang kiểm tra chất lượng video.",
            ProductProductionStatus.COMPLETED:
                "Video đã hoàn thành.",
            ProductProductionStatus.FAILED:
                "Không thể hoàn thành xử lý video.",
            ProductProductionStatus.CANCELLED:
                "Dự án đã được hủy.",
        }

        return mapping[status]

    def _string_or_none(
        self,
        value: Any,
    ) -> str | None:
        return (
            str(value)
            if value is not None
            else None
        )