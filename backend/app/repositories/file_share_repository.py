import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.file import File
from app.models.file_share import FileShare, SharePermission


class FileShareRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, share_id: uuid.UUID) -> FileShare | None:
        stmt = (
            select(FileShare)
            .options(joinedload(FileShare.file), joinedload(FileShare.shared_with), joinedload(FileShare.owner))
            .where(FileShare.id == share_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_for_file_and_user(self, file_id: uuid.UUID, user_id: uuid.UUID) -> FileShare | None:
        stmt = select(FileShare).where(FileShare.file_id == file_id, FileShare.shared_with_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_for_file(self, file_id: uuid.UUID) -> list[FileShare]:
        stmt = (
            select(FileShare)
            .options(joinedload(FileShare.shared_with), joinedload(FileShare.owner))
            .where(FileShare.file_id == file_id)
            .order_by(FileShare.created_at.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def list_shared_with_user(self, user_id: uuid.UUID) -> list[FileShare]:
        stmt = (
            select(FileShare)
            .options(joinedload(FileShare.file), joinedload(FileShare.owner))
            .join(File, FileShare.file_id == File.id)
            .where(FileShare.shared_with_id == user_id, File.is_trashed.is_(False))
            .order_by(FileShare.created_at.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def upsert(
        self,
        *,
        file_id: uuid.UUID,
        owner_id: uuid.UUID,
        shared_with_id: uuid.UUID,
        permission: SharePermission,
    ) -> FileShare:
        existing = self.get_for_file_and_user(file_id, shared_with_id)
        if existing:
            existing.permission = permission
            self.db.commit()
            self.db.refresh(existing)
            return existing

        share = FileShare(
            file_id=file_id,
            owner_id=owner_id,
            shared_with_id=shared_with_id,
            permission=permission,
        )
        self.db.add(share)
        self.db.commit()
        self.db.refresh(share)
        return share

    def delete(self, share: FileShare) -> None:
        self.db.delete(share)
        self.db.commit()
