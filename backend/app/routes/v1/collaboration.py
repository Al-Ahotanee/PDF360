from datetime import datetime, timedelta, timezone
import secrets
import uuid

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.collaboration import (
    CommentCreate,
    CommentOut,
    NotificationOut,
    ShareCreateRequest,
    ShareOut,
    SharedWithMeOut,
)
from app.services.collaboration_service import CommentService, NotificationService
from app.services.share_service import ShareService

router = APIRouter(prefix="/collaboration", tags=["Collaboration"])


@router.get("/notifications", response_model=list[NotificationOut])
def list_notifications(unread_only: bool = False, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return NotificationService(db).list_for_user(user.id, unread_only)


@router.patch("/notifications/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(notification_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return NotificationService(db).mark_read(user_id=user.id, notification_id=notification_id)


@router.get("/files/{file_id}/comments", response_model=list[CommentOut])
def list_comments(file_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return CommentService(db).list_for_file(user_id=user.id, file_id=file_id)


@router.post("/files/{file_id}/comments", response_model=CommentOut, status_code=201)
def add_comment(file_id: uuid.UUID, data: CommentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return CommentService(db).add_comment(
        author_id=user.id, file_id=file_id, body=data.body, page_number=data.page_number, position=data.position
    )


@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment(comment_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    CommentService(db).delete_comment(user_id=user.id, comment_id=comment_id)


# --- Document Sharing Endpoints ---

@router.post("/files/{file_id}/share", response_model=ShareOut, status_code=201)
def share_file(
    file_id: uuid.UUID,
    data: ShareCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    share = ShareService(db).share_file(
        owner_id=user.id,
        file_id=file_id,
        with_email=data.with_email,
        permission=data.permission,
    )
    return ShareOut(
        id=share.id,
        file_id=share.file_id,
        owner_id=share.owner_id,
        shared_with_id=share.shared_with_id,
        permission=share.permission,
        created_at=share.created_at,
        shared_with_email=share.shared_with.email if share.shared_with else data.with_email,
    )


@router.get("/files/{file_id}/shares", response_model=list[ShareOut])
def list_file_shares(
    file_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    shares = ShareService(db).list_shares_for_file(owner_id=user.id, file_id=file_id)
    return [
        ShareOut(
            id=s.id,
            file_id=s.file_id,
            owner_id=s.owner_id,
            shared_with_id=s.shared_with_id,
            permission=s.permission,
            created_at=s.created_at,
            shared_with_email=s.shared_with.email if s.shared_with else None,
        )
        for s in shares
    ]


@router.delete("/shares/{share_id}", status_code=204)
def revoke_share(
    share_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ShareService(db).revoke_share(owner_id=user.id, share_id=share_id)


@router.get("/shared-with-me", response_model=list[SharedWithMeOut])
def list_shared_with_me(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    shares = ShareService(db).list_shared_with_me(user_id=user.id)
    return [
        SharedWithMeOut(
            id=s.id,
            file_id=s.file_id,
            original_filename=s.file.original_filename,
            mime_type=s.file.mime_type,
            size_bytes=s.file.size_bytes,
            permission=s.permission,
            owner_email=s.owner.email if s.owner else None,
            created_at=s.created_at,
        )
        for s in shares
        if s.file and not s.file.is_trashed
    ]


# --- Public Share Links (Password Protected & Expiring) ---

class PublicLinkCreate(BaseModel):
    expires_in_hours: int | None = Field(None, ge=1, le=8760)
    password: str | None = None
    allow_download: bool = True


class PublicLinkOut(BaseModel):
    id: uuid.UUID
    share_token: str
    share_url: str
    expires_at: datetime | None
    has_password: bool
    allow_download: bool
    view_count: int


class PublicDocumentOut(BaseModel):
    file_id: uuid.UUID
    original_filename: str
    size_bytes: int
    mime_type: str | None
    allow_download: bool
    has_password: bool
    created_at: datetime


@router.post("/files/{file_id}/public-link", response_model=PublicLinkOut, status_code=201)
def create_public_share_link(
    file_id: uuid.UUID,
    data: PublicLinkCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.services.file_service import FileService
    from app.repositories.public_share_repository import PublicShareRepository
    from app.core.security import hash_password

    file = FileService(db).get_accessible_file(file_id=file_id, user_id=user.id)
    share_token = secrets.token_urlsafe(32)
    pw_hash = hash_password(data.password) if data.password else None
    expires_at = datetime.now(timezone.utc) + timedelta(hours=data.expires_in_hours) if data.expires_in_hours else None

    repo = PublicShareRepository(db)
    share = repo.create(
        file_id=file.id,
        created_by_id=user.id,
        share_token=share_token,
        password_hash=pw_hash,
        expires_at=expires_at,
        allow_download=data.allow_download,
    )
    return PublicLinkOut(
        id=share.id,
        share_token=share.share_token,
        share_url=f"/share/{share.share_token}",
        expires_at=share.expires_at,
        has_password=bool(share.password_hash),
        allow_download=share.allow_download,
        view_count=share.view_count,
    )


@router.get("/public/{share_token}", response_model=PublicDocumentOut)
def get_public_document(
    share_token: str,
    password: str | None = None,
    db: Session = Depends(get_db),
):
    from app.repositories.public_share_repository import PublicShareRepository
    from app.core.security import verify_password
    from fastapi import HTTPException, status

    repo = PublicShareRepository(db)
    share = repo.get_by_token(share_token)
    if not share or (share.file and share.file.is_trashed):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared document not found.")

    if share.expires_at and share.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="This share link has expired.")

    if share.password_hash:
        if not password or not verify_password(password, share.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password required or incorrect.")

    repo.increment_view_count(share)
    return PublicDocumentOut(
        file_id=share.file.id,
        original_filename=share.file.original_filename,
        size_bytes=share.file.size_bytes,
        mime_type=share.file.mime_type,
        allow_download=share.allow_download,
        has_password=bool(share.password_hash),
        created_at=share.file.created_at,
    )


@router.get("/public/{share_token}/download")
def download_public_document(
    share_token: str,
    password: str | None = None,
    db: Session = Depends(get_db),
):
    import io
    from fastapi.responses import StreamingResponse
    from app.repositories.public_share_repository import PublicShareRepository
    from app.core.security import verify_password
    from app.services.file_service import FileService
    from fastapi import HTTPException, status

    repo = PublicShareRepository(db)
    share = repo.get_by_token(share_token)
    if not share or (share.file and share.file.is_trashed):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared document not found.")

    if share.expires_at and share.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="This share link has expired.")

    if share.password_hash:
        if not password or not verify_password(password, share.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password required or incorrect.")

    if not share.allow_download:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Downloading is disabled for this link.")

    service = FileService(db)
    content = service.read_bytes(share.file)
    return StreamingResponse(
        io.BytesIO(content),
        media_type=share.file.mime_type or "application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{share.file.original_filename}"',
            "Content-Length": str(len(content)),
        },
    )
