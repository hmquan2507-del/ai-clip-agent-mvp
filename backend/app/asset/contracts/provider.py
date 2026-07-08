from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.asset.models import AssetDomain


class AssetProviderContract(ABC):
    provider_key: str

    @abstractmethod
    def search(self, query: str, asset_type: str, **kwargs: Any) -> list[AssetDomain]:
        raise NotImplementedError

    @abstractmethod
    def download(self, asset: AssetDomain, **kwargs: Any) -> AssetDomain:
        raise NotImplementedError

    @abstractmethod
    def health(self) -> dict[str, Any]:
        raise NotImplementedError