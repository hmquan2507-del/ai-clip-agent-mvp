import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile


class LocalStorageProvider:
    def __init__(self, base_path: str = "data/uploads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_upload(self, file: UploadFile, production_id: str) -> tuple[str, int]:
        safe_name = f"{uuid.uuid4()}_{file.filename}"
        production_dir = self.base_path / production_id
        production_dir.mkdir(parents=True, exist_ok=True)

        destination = production_dir / safe_name

        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        size_bytes = destination.stat().st_size

        return str(destination), size_bytes