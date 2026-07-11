from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.product.contracts.enums import (
    ProductAction,
    ProductErrorCode,
    ProductEventType,
    ProductProductionStatus,
    ProductStage,
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ProductProgress:
    stage: ProductStage | str
    progress: float
    message: str

    status: ProductProductionStatus | str | None = None
    estimated_seconds_remaining: int | None = None

    updated_at: str = field(
        default_factory=utc_now_iso
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        self.progress = min(
            100.0,
            max(0.0, float(self.progress)),
        )

        if (
            self.estimated_seconds_remaining
            is not None
            and self.estimated_seconds_remaining < 0
        ):
            self.estimated_seconds_remaining = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self._value(self.stage),
            "progress": self.progress,
            "message": self.message,
            "status": (
                self._value(self.status)
                if self.status is not None
                else None
            ),
            "estimated_seconds_remaining": (
                self.estimated_seconds_remaining
            ),
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }

    def _value(self, value: Any) -> str:
        return (
            value.value
            if hasattr(value, "value")
            else str(value)
        )


@dataclass
class ProductEvent:
    event_type: ProductEventType | str
    production_id: str

    stage: ProductStage | str | None = None
    status: ProductProductionStatus | str | None = None

    progress: float | None = None
    message: str | None = None

    created_at: str = field(
        default_factory=utc_now_iso
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self._value(
                self.event_type
            ),
            "production_id": self.production_id,
            "stage": (
                self._value(self.stage)
                if self.stage is not None
                else None
            ),
            "status": (
                self._value(self.status)
                if self.status is not None
                else None
            ),
            "progress": self.progress,
            "message": self.message,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    def _value(self, value: Any) -> str:
        return (
            value.value
            if hasattr(value, "value")
            else str(value)
        )


@dataclass
class ProductFailure:
    code: ProductErrorCode | str
    message: str

    technical_message: str | None = None
    retryable: bool = False
    failed_stage: ProductStage | str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self._value(self.code),
            "message": self.message,
            "technical_message": self.technical_message,
            "retryable": self.retryable,
            "failed_stage": (
                self._value(self.failed_stage)
                if self.failed_stage is not None
                else None
            ),
            "metadata": self.metadata,
        }

    def _value(self, value: Any) -> str:
        return (
            value.value
            if hasattr(value, "value")
            else str(value)
        )


@dataclass
class ProductArtifactSummary:
    artifact_id: str
    artifact_type: str

    local_path: str | None = None
    download_url: str | None = None

    file_size: int | None = None
    mime_type: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "local_path": self.local_path,
            "download_url": self.download_url,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "metadata": self.metadata,
        }


@dataclass
class ProductProductionSnapshot:
    production_id: str
    name: str

    status: ProductProductionStatus | str
    stage: ProductStage | str

    progress: ProductProgress

    version: int = 1

    platform: str | None = None
    editing_style: str | None = None
    language: str = "vi"

    allowed_actions: list[
        ProductAction | str
    ] = field(default_factory=list)

    artifacts: list[
        ProductArtifactSummary
    ] = field(default_factory=list)

    failure: ProductFailure | None = None

    created_at: str | None = None
    updated_at: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "name": self.name,
            "status": self._value(self.status),
            "stage": self._value(self.stage),
            "progress": self.progress.to_dict(),
            "version": self.version,
            "platform": self.platform,
            "editing_style": self.editing_style,
            "language": self.language,
            "allowed_actions": [
                self._value(action)
                for action in self.allowed_actions
            ],
            "artifacts": [
                artifact.to_dict()
                for artifact in self.artifacts
            ],
            "failure": (
                self.failure.to_dict()
                if self.failure
                else None
            ),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }

    def _value(self, value: Any) -> str:
        return (
            value.value
            if hasattr(value, "value")
            else str(value)
        )