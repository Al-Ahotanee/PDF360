import io
import uuid
from pathlib import Path
from typing import BinaryIO

from app.core.config import settings
from app.services.storage.base import StorageProvider


class S3StorageProvider(StorageProvider):
    """
    S3-compatible storage provider (AWS S3, Cloudflare R2, MinIO, Supabase Storage).
    """

    def __init__(self):
        import boto3
        from botocore.config import Config

        session = boto3.session.Session()
        self.bucket = settings.S3_BUCKET_NAME
        s3_config = Config(signature_version="s3v4")

        kwargs = {
            "service_name": "s3",
            "aws_access_key_id": settings.S3_ACCESS_KEY,
            "aws_secret_access_key": settings.S3_SECRET_KEY,
            "config": s3_config,
        }
        if settings.S3_REGION:
            kwargs["region_name"] = settings.S3_REGION
        if settings.S3_ENDPOINT_URL:
            kwargs["endpoint_url"] = settings.S3_ENDPOINT_URL

        self.client = session.client(**kwargs)

    def save(self, key: str, file_obj: BinaryIO) -> int:
        file_obj.seek(0, io.SEEK_END)
        size = file_obj.tell()
        file_obj.seek(0)
        self.client.upload_fileobj(file_obj, self.bucket, key)
        return size

    def read(self, key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()

    def open_stream(self, key: str) -> BinaryIO:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"]

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def exists(self, key: str) -> bool:
        from botocore.exceptions import ClientError
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False

    def build_key(self, owner_id: str, filename: str) -> str:
        safe_name = Path(filename).name
        return f"{owner_id}/{uuid.uuid4().hex}_{safe_name}"
