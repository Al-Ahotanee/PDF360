"""
Returns the active StorageProvider based on settings.STORAGE_PROVIDER.
Callers use `get_storage_provider()` — never instantiate a concrete
provider class directly.
"""
from functools import lru_cache

from app.core.config import settings
from app.services.storage.base import StorageProvider
from app.services.storage.local import LocalStorageProvider


@lru_cache
def get_storage_provider() -> StorageProvider:
    if settings.STORAGE_PROVIDER == "local":
        return LocalStorageProvider(settings.LOCAL_STORAGE_PATH)
    if settings.STORAGE_PROVIDER == "s3":
        from app.services.storage.s3 import S3StorageProvider
        return S3StorageProvider()
    raise ValueError(f"Unknown STORAGE_PROVIDER: {settings.STORAGE_PROVIDER}")
