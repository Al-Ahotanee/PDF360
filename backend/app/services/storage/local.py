import shutil
import uuid
from pathlib import Path
from typing import BinaryIO

from app.services.storage.base import StorageProvider


class LocalStorageProvider(StorageProvider):
    def __init__(self, root_path: str):
        self.root = Path(root_path)
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, key: str) -> Path:
        # Prevent path traversal — key must resolve inside root.
        path = (self.root / key).resolve()
        if not str(path).startswith(str(self.root.resolve())):
            raise ValueError(f"Invalid storage key: {key}")
        return path

    def save(self, key: str, file_obj: BinaryIO) -> int:
        path = self._resolve(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as dest:
            shutil.copyfileobj(file_obj, dest)
        return path.stat().st_size

    def read(self, key: str) -> bytes:
        return self._resolve(key).read_bytes()

    def open_stream(self, key: str) -> BinaryIO:
        return open(self._resolve(key), "rb")

    def delete(self, key: str) -> None:
        path = self._resolve(key)
        if path.exists():
            path.unlink()

    def exists(self, key: str) -> bool:
        return self._resolve(key).exists()

    def build_key(self, owner_id: str, filename: str) -> str:
        safe_name = Path(filename).name  # strip any directory components
        return f"{owner_id}/{uuid.uuid4().hex}_{safe_name}"
