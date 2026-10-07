import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.file import Folder
from app.models.tag import Tag


class FolderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, owner_id: uuid.UUID, name: str, parent_id: uuid.UUID | None) -> Folder:
        folder = Folder(owner_id=owner_id, name=name, parent_id=parent_id)
        self.db.add(folder)
        self.db.commit()
        self.db.refresh(folder)
        return folder

    def get_by_id(self, folder_id: uuid.UUID) -> Folder | None:
        return self.db.execute(select(Folder).where(Folder.id == folder_id)).scalar_one_or_none()

    def list_for_owner(self, owner_id: uuid.UUID) -> list[Folder]:
        stmt = select(Folder).where(Folder.owner_id == owner_id, Folder.is_trashed.is_(False))
        return list(self.db.execute(stmt).scalars().all())


class TagRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, owner_id: uuid.UUID, name: str, color: str | None) -> Tag:
        tag = Tag(owner_id=owner_id, name=name, color=color)
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag

    def get_by_id(self, tag_id: uuid.UUID) -> Tag | None:
        return self.db.execute(select(Tag).where(Tag.id == tag_id)).scalar_one_or_none()

    def list_for_owner(self, owner_id: uuid.UUID) -> list[Tag]:
        return list(self.db.execute(select(Tag).where(Tag.owner_id == owner_id)).scalars().all())
