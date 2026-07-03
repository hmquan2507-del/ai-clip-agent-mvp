from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageProvider(ABC):
    @abstractmethod
    def save_file(
        self,
        file: BinaryIO,
        object_key: str,
        content_type: str | None = None,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def delete_file(self, object_key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def file_exists(self, object_key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_public_url(self, object_key: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_signed_url(
        self,
        object_key: str,
        expires_in_seconds: int = 3600,
    ) -> str:
        raise NotImplementedError