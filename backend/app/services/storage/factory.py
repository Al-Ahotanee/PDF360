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
    # If explicitly set to s3 OR if AWS/Neon credentials are provided in the environment
    has_s3_creds = bool(settings.effective_s3_access_key and settings.effective_s3_secret_key)
    use_s3 = settings.STORAGE_PROVIDER == "s3" or (has_s3_creds and settings.S3_BUCKET_NAME)

    if use_s3:
        if settings.S3_BUCKET_NAME and has_s3_creds:
            from app.services.storage.s3 import S3StorageProvider
            return S3StorageProvider()
        else:
            logger.warning(
                "S3 storage credentials detected or requested, but S3_BUCKET_NAME is missing. "
                "Falling back to local storage temporarily."
            )
            return LocalStorageProvider(settings.LOCAL_STORAGE_PATH)

    if settings.STORAGE_PROVIDER == "local":
        return LocalStorageProvider(settings.LOCAL_STORAGE_PATH)

    raise ValueError(f"Unknown STORAGE_PROVIDER: {settings.STORAGE_PROVIDER}")
