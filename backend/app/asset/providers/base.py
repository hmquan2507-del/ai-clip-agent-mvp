from __future__ import annotations

from abc import ABC, abstractmethod

from app.asset.providers.models import (
    AssetProviderHealthResult,
    AssetProviderSearchRequest,
    AssetProviderSearchResponse,
)


class BaseAssetProvider(ABC):
    provider_key: str

    @abstractmethod
    def search(
        self,
        request: AssetProviderSearchRequest,
    ) -> AssetProviderSearchResponse:
        raise NotImplementedError

    @abstractmethod
    def health(self) -> AssetProviderHealthResult:
        raise NotImplementedError