from __future__ import annotations

from typing import Any

from app.product.workspace.interfaces import (
    IssueWorkspaceLoader,
)
from app.product.workspace.repository.utils import (
    call_first_supported,
    ensure_list,
    normalize_production_id,
)


class RepositoryIssueWorkspaceAdapter(
    IssueWorkspaceLoader
):
    METHOD_NAMES = (
        "list_by_production_id",
        "find_by_production_id",
        "get_by_production_id",
        "list_issues",
        "get_issues",
    )

    def __init__(
        self,
        issue_repository: Any | None = None,
        *,
        quality_loader: Any | None = None,
    ):
        self.issue_repository = (
            issue_repository
        )
        self.quality_loader = (
            quality_loader
        )

    def load_issues(
        self,
        production_id: str,
    ) -> list[Any]:
        normalized_id = (
            normalize_production_id(
                production_id
            )
        )

        repository_result = (
            call_first_supported(
                self.issue_repository,
                self.METHOD_NAMES,
                production_id=normalized_id,
                default=None,
            )
        )

        issues = ensure_list(
            repository_result
        )

        if issues:
            return issues

        return self._issues_from_quality(
            normalized_id
        )

    def _issues_from_quality(
        self,
        production_id: str,
    ) -> list[dict[str, Any]]:
        if self.quality_loader is None:
            return []

        report = (
            self.quality_loader
            .load_quality_report(
                production_id
            )
        )

        if report is None:
            return []

        checks = (
            report.get("checks", [])
            if isinstance(report, dict)
            else getattr(
                report,
                "checks",
                [],
            )
        )

        result: list[
            dict[str, Any]
        ] = []

        for check in checks or []:
            status = (
                check.get("status")
                if isinstance(check, dict)
                else getattr(
                    check,
                    "status",
                    None,
                )
            )

            if hasattr(status, "value"):
                status = status.value

            if status not in {
                "warning",
                "fail",
            }:
                continue

            check_type = (
                check.get("check_type")
                if isinstance(check, dict)
                else getattr(
                    check,
                    "check_type",
                    "quality",
                )
            )

            if hasattr(check_type, "value"):
                check_type = (
                    check_type.value
                )

            message = (
                check.get("message")
                if isinstance(check, dict)
                else getattr(
                    check,
                    "message",
                    "Video có vấn đề chất lượng.",
                )
            )

            result.append(
                {
                    "source": "quality_gate",
                    "level": (
                        "error"
                        if status == "fail"
                        else "warning"
                    ),
                    "code": str(
                        check_type
                    ),
                    "message": message,
                }
            )

        return result