import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.file_share import SharePermission


class NotificationOut(BaseModel):
    id: uuid.UUID
    title: str
    body: str | None
    is_read: bool
    metadata_json: dict = {}
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
    mentioned_user_ids: list = []
    created_at: datetime

    model_config = {"from_attributes": True}


class ShareCreateRequest(BaseModel):
    with_email: EmailStr
    permission: SharePermission = SharePermission.VIEW


class ShareOut(BaseModel):
    id: uuid.UUID
    file_id: uuid.UUID
    owner_id: uuid.UUID
    shared_with_id: uuid.UUID
    permission: SharePermission
    created_at: datetime
    shared_with_email: str | None = None

    model_config = {"from_attributes": True}


class SharedWithMeOut(BaseModel):
    id: uuid.UUID  # share id
    file_id: uuid.UUID
    original_filename: str
    mime_type: str
    size_bytes: int
    permission: SharePermission
    owner_email: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
