import uuid
from typing import BinaryIO

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.file import File
from app.repositories.file_repository import FileRepository
from app.services.storage.factory import get_storage_provider

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "image/png",
    "image/jpeg",
}
MAX_UPLOAD_BYTES = 200 * 1024 * 1024  # 200MB — chunked upload for larger files is Phase 9 follow-up


class FileService:
    def __init__(self, db: Session):
        self.db = db
        self.files = FileRepository(db)
        self._storage = None

    @property
    def storage(self):
        if self._storage is None:
            try:
                self._storage = get_storage_provider()
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Failed to initialize storage provider: {e}. Falling back to configured local path.")
                from app.services.storage.local import LocalStorageProvider
                self._storage = LocalStorageProvider(settings.LOCAL_STORAGE_PATH)
        return self._storage

    def upload(self, *, owner_id: uuid.UUID, filename: str, mime_type: str, file_obj: BinaryIO) -> File:
        if mime_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type '{mime_type}' is not supported.",
            )

        key = self.storage.build_key(str(owner_id), filename)
        size_bytes = self.storage.save(key, file_obj)

        if size_bytes > MAX_UPLOAD_BYTES:
            self.storage.delete(key)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds max upload size of {MAX_UPLOAD_BYTES // (1024*1024)}MB.",
            )

        return self.files.create(
            owner_id=owner_id,
            original_filename=filename,
            storage_key=key,
            mime_type=mime_type,
            size_bytes=size_bytes,
        )

    def get_owned_file(self, *, file_id: uuid.UUID, owner_id: uuid.UUID) -> File:
        file = self.files.get_by_id(file_id)
        if file is None or file.owner_id != owner_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
        return file

    def get_accessible_file(
        self,
        *,
        file_id: uuid.UUID,
        user_id: uuid.UUID,
        required_permission=None,
    ) -> File:
        from app.models.file_share import SharePermission
        from app.services.file_access import has_at_least

        perm = required_permission or SharePermission.VIEW
        file = self.files.get_by_id(file_id)
        if file is None or not has_at_least(self.db, file=file, user_id=user_id, required=perm):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found or access denied.")
        return file

    def read_bytes(self, file: File) -> bytes:
        return self.storage.read(file.storage_key)

    def list_for_owner(self, owner_id: uuid.UUID) -> list[File]:
        return self.files.list_for_owner(owner_id)
