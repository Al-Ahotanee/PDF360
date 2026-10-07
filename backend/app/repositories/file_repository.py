import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.file import File


class FileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, file_id: uuid.UUID) -> File | None:
        return self.db.execute(select(File).where(File.id == file_id)).scalar_one_or_none()

    def get_many_by_ids(self, file_ids: list[uuid.UUID]) -> list[File]:
        rows = self.db.execute(select(File).where(File.id.in_(file_ids))).scalars().all()
        return list(rows)

    def create(self, *, owner_id: uuid.UUID, original_filename: str, storage_key: str,
               mime_type: str, size_bytes: int, folder_id: uuid.UUID | None = None) -> File:
        file = File(
            owner_id=owner_id,
            original_filename=original_filename,
            storage_key=storage_key,
            mime_type=mime_type,
            size_bytes=size_bytes,
            folder_id=folder_id,
        )
        self.db.add(file)
        self.db.commit()
        self.db.refresh(file)
        return file

    def list_for_owner(self, owner_id: uuid.UUID, include_trashed: bool = False) -> list[File]:
        stmt = select(File).where(File.owner_id == owner_id)
        if not include_trashed:
            stmt = stmt.where(File.is_trashed.is_(False))
        return list(self.db.execute(stmt).scalars().all())
