import uuid
from datetime import datetime

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: uuid.UUID
    title: str
    body: str | None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    body: str
    page_number: int | None = None
    position: dict | None = None


class CommentOut(BaseModel):
    id: uuid.UUID
    file_id: uuid.UUID
    author_id: uuid.UUID
    body: str
    page_number: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
