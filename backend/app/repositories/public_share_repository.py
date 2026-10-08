from datetime import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.file_share import PublicShare


class PublicShareRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_token(self, share_token: str) -> PublicShare | None:
        stmt = (
            select(PublicShare)
            .options(joinedload(PublicShare.file), joinedload(PublicShare.created_by))
            .where(PublicShare.share_token == share_token)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_for_file(self, file_id: uuid.UUID) -> PublicShare | None:
        stmt = (
            select(PublicShare)
            .options(joinedload(PublicShare.file))
            .where(PublicShare.file_id == file_id)
            .order_by(PublicShare.created_at.desc())
        )
        return self.db.execute(stmt).scalars().first()

    def create(
        self,
        *,
        file_id: uuid.UUID,
        created_by_id: uuid.UUID,
        share_token: str,
        password_hash: str | None = None,
        expires_at: datetime | None = None,
        allow_download: bool = True,
    ) -> PublicShare:
        share = PublicShare(
            file_id=file_id,
            created_by_id=created_by_id,
            share_token=share_token,
            password_hash=password_hash,
            expires_at=expires_at,
            allow_download=allow_download,
        )
        self.db.add(share)
        self.db.commit()
        self.db.refresh(share)
        return share

    def increment_view_count(self, share: PublicShare) -> None:
        share.view_count += 1
        self.db.commit()

    def delete(self, share: PublicShare) -> None:
        self.db.delete(share)
        self.db.commit()
