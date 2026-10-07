import uuid

from fastapi import APIRouter, Depends
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
