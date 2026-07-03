import shutil
from pathlib import Path
from typing import BinaryIO

from app.storage.base import StorageProvider


class LocalStorageProvider(StorageProvider):
    def __init__(self, base_path: str = "data/uploads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, object_key: str) -> Path:
        return self.base_path / object_key

    def save_file(
        self,
        file: BinaryIO,
        object_key: str,
        content_type: str | None = None,
    ) -> str:
        destination = self._resolve_path(object_key)
        destination.parent.mkdir(parents=True, exist_ok=True)

        with destination.open("wb") as buffer:
            shutil.copyfileobj(file, buffer)

        return object_key

    def delete_file(self, object_key: str) -> None:
        path = self._resolve_path(object_key)

        if path.exists():
            path.unlink()

    def file_exists(self, object_key: str) -> bool:
        return self._resolve_path(object_key).exists()

    def get_public_url(self, object_key: str) -> str:
        return f"/media/{object_key}"

    def get_signed_url(
        self,
        object_key: str,
        expires_in_seconds: int = 3600,
    ) -> str:
        return self.get_public_url(object_key)