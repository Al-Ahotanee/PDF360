import uuid

from pydantic import BaseModel


class FolderCreate(BaseModel):
    name: str
    parent_id: uuid.UUID | None = None


class FolderOut(BaseModel):
    id: uuid.UUID
    name: str
    parent_id: uuid.UUID | None

    model_config = {"from_attributes": True}


class TagCreate(BaseModel):
    name: str
    color: str | None = None


class TagOut(BaseModel):
    id: uuid.UUID
    name: str
    color: str | None

    model_config = {"from_attributes": True}


class FavoriteRequest(BaseModel):
    is_favorite: bool


class AddTagRequest(BaseModel):
    tag_id: uuid.UUID
