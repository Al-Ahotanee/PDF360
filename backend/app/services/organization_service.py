import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.file_repository import FileRepository
from app.repositories.organization_repository import FolderRepository, TagRepository


class OrganizationService:
    def __init__(self, db: Session):
        self.db = db
        self.folders = FolderRepository(db)
        self.tags = TagRepository(db)
        self.files = FileRepository(db)

    def create_folder(self, *, owner_id: uuid.UUID, name: str, parent_id: uuid.UUID | None):
        if parent_id is not None:
            parent = self.folders.get_by_id(parent_id)
            if parent is None or parent.owner_id != owner_id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent folder not found.")
        return self.folders.create(owner_id=owner_id, name=name, parent_id=parent_id)

    def list_folders(self, owner_id: uuid.UUID):
        return self.folders.list_for_owner(owner_id)

    def create_tag(self, *, owner_id: uuid.UUID, name: str, color: str | None):
        return self.tags.create(owner_id=owner_id, name=name, color=color)

    def list_tags(self, owner_id: uuid.UUID):
        return self.tags.list_for_owner(owner_id)

    def _get_owned_file(self, owner_id: uuid.UUID, file_id: uuid.UUID):
        file = self.files.get_by_id(file_id)
        if file is None or file.owner_id != owner_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
        return file

    def toggle_favorite(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, is_favorite: bool):
        file = self._get_owned_file(owner_id, file_id)
        file.is_favorite = is_favorite
        self.db.commit()
        self.db.refresh(file)
        return file

    def move_to_trash(self, *, owner_id: uuid.UUID, file_id: uuid.UUID):
        file = self._get_owned_file(owner_id, file_id)
        file.is_trashed = True
        self.db.commit()
        self.db.refresh(file)
        return file

    def restore_from_trash(self, *, owner_id: uuid.UUID, file_id: uuid.UUID):
        file = self._get_owned_file(owner_id, file_id)
        file.is_trashed = False
        self.db.commit()
        self.db.refresh(file)
        return file

    def add_tag_to_file(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, tag_id: uuid.UUID):
        file = self._get_owned_file(owner_id, file_id)
        tag = self.tags.get_by_id(tag_id)
        if tag is None or tag.owner_id != owner_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found.")
        if tag not in file.tags:
            file.tags.append(tag)
            self.db.commit()
            self.db.refresh(file)
        return file
