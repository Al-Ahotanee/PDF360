"""
Returns the active StorageProvider based on settings.STORAGE_PROVIDER.
Callers use `get_storage_provider()` — never instantiate a concrete
provider class directly.
"""
from functools import lru_cache
import logging

from app.core.config import settings
from app.services.storage.base import StorageProvider
from app.services.storage.local import LocalStorageProvider

logger = logging.getLogger(__name__)


@lru_cache
def get_storage_provider() -> StorageProvider:
    if settings.STORAGE_PROVIDER == "s3":
        if settings.S3_BUCKET_NAME and settings.S3_ACCESS_KEY:
            from app.services.storage.s3 import S3StorageProvider
            return S3StorageProvider()
        else:
            logger.warning(
                "STORAGE_PROVIDER=s3 is set but S3_BUCKET_NAME or S3_ACCESS_KEY is missing. "
                "Falling back to local storage temporarily."
            )
            return LocalStorageProvider(settings.LOCAL_STORAGE_PATH)

    if settings.STORAGE_PROVIDER == "local":
        return LocalStorageProvider(settings.LOCAL_STORAGE_PATH)

    raise ValueError(f"Unknown STORAGE_PROVIDER: {settings.STORAGE_PROVIDER}")
