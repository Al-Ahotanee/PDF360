"""
StorageProvider interface — the single abstraction every service/route uses
to read/write file bytes. Nothing outside this package should call
`open()`/`os.path` or an S3 SDK directly.

Swapping STORAGE_PROVIDER=local -> s3 in .env, plus implementing
S3StorageProvider, should require zero changes anywhere else in the app.
"""
from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageProvider(ABC):
    @abstractmethod
    def save(self, key: str, file_obj: BinaryIO) -> int:
        """Writes file_obj to `key`, returns size in bytes."""
        raise NotImplementedError

    @abstractmethod
    def read(self, key: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def open_stream(self, key: str) -> BinaryIO:
        """Returns a file-like object for streaming reads (large downloads)."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists(self, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def build_key(self, owner_id: str, filename: str) -> str:
        """Builds a namespaced, collision-resistant storage key for a new file."""
        raise NotImplementedError
