import io
import logging
import uuid
from pathlib import Path
from typing import BinaryIO

from app.core.config import settings
from app.services.storage.base import StorageProvider
from app.services.storage.local import LocalStorageProvider

logger = logging.getLogger(__name__)


class S3StorageProvider(StorageProvider):
    """
    S3-compatible storage provider (AWS S3, Cloudflare R2, MinIO, Neon Object Storage, Supabase Storage).
    Falls back gracefully to local storage if S3 operations fail due to network/permissions.
    """

    def __init__(self):
        import boto3
        from botocore.config import Config

        self._local_fallback = LocalStorageProvider(settings.LOCAL_STORAGE_PATH)
        session = boto3.session.Session()
        self.bucket = settings.S3_BUCKET_NAME or "pdf360-default"
        s3_config = Config(signature_version="s3v4", connect_timeout=5, read_timeout=5)

        kwargs = {
            "service_name": "s3",
            "aws_access_key_id": settings.effective_s3_access_key,
            "aws_secret_access_key": settings.effective_s3_secret_key,
            "config": s3_config,
        }
        if settings.effective_s3_region:
            kwargs["region_name"] = settings.effective_s3_region
        if settings.effective_s3_endpoint_url:
            kwargs["endpoint_url"] = settings.effective_s3_endpoint_url

        self.client = session.client(**kwargs)

    def save(self, key: str, file_obj: BinaryIO) -> int:
        file_obj.seek(0, io.SEEK_END)
        size = file_obj.tell()
        file_obj.seek(0)
        try:
            self.client.upload_fileobj(file_obj, self.bucket, key)
            return size
        except Exception as exc:
            logger.warning(f"S3 upload failed for key {key} ({exc}); falling back to local storage.", exc_info=True)
            file_obj.seek(0)
            return self._local_fallback.save(key, file_obj)

    def read(self, key: str) -> bytes:
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except Exception as exc:
            logger.warning(f"S3 read failed for key {key} ({exc}); checking local fallback storage.")
            if self._local_fallback.exists(key):
                return self._local_fallback.read(key)
            raise

    def open_stream(self, key: str) -> BinaryIO:
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return response["Body"]
        except Exception as exc:
            logger.warning(f"S3 open_stream failed for key {key} ({exc}); checking local fallback storage.")
            if self._local_fallback.exists(key):
                return self._local_fallback.open_stream(key)
            raise

    def delete(self, key: str) -> None:
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
        except Exception as exc:
            logger.warning(f"S3 delete failed for key {key}: {exc}")
        if self._local_fallback.exists(key):
            self._local_fallback.delete(key)

    def exists(self, key: str) -> bool:
        from botocore.exceptions import ClientError
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return self._local_fallback.exists(key)

    def build_key(self, owner_id: str, filename: str) -> str:
        safe_name = Path(filename).name
        return f"{owner_id}/{uuid.uuid4().hex}_{safe_name}"

