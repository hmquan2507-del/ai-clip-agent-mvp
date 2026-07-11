from __future__ import annotations

from typing import Any

from app.product.adapters.models import (
    ProductQualitySummary,
)
from app.product.adapters.utils import (
    float_or_none,
    int_or_none,
    normalize,
    read_value,
    value_of,
)


class ProductQualityAdapter:
    def adapt(
        self,
        quality_report: Any | None,
    ) -> ProductQualitySummary:
        if quality_report is None:
            return ProductQualitySummary(
                available=False,
                metadata={
                    "adapter": "ProductQualityAdapter",
                },
            )

        status = value_of(
            read_value(
                quality_report,
                "status",
            )
        )

        return ProductQualitySummary(
            available=True,
            approved=bool(
                read_value(
                    quality_report,
                    "approved",
                    status == "approved",
                )
            ),
            status=(
                str(status)
                if status is not None
                else None
            ),
            quality_score=float_or_none(
                read_value(
                    quality_report,
                    "quality_score",
                )
            ),
            warning_count=(
                int_or_none(
                    read_value(
                        quality_report,
                        "warning_count",
                        0,
                    )
                )
                or 0
            ),
            failure_count=(
                int_or_none(
                    read_value(
                        quality_report,
                        "failure_count",
                        0,
                    )
                )
                or 0
            ),
            report_path=read_value(
                quality_report,
                "report_path",
            ),
            checks=normalize(
                read_value(
                    quality_report,
                    "checks",
                    [],
                )
            ),
            metadata={
                "adapter": "ProductQualityAdapter",
            },
        )