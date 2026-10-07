import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.collaboration import CommentCreate, CommentOut, NotificationOut
from app.services.collaboration_service import CommentService, NotificationService

router = APIRouter(prefix="/collaboration", tags=["Collaboration"])


@router.get("/notifications", response_model=list[NotificationOut])
def list_notifications(unread_only: bool = False, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return NotificationService(db).list_for_user(user.id, unread_only)


@router.patch("/notifications/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(notification_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return NotificationService(db).mark_read(user_id=user.id, notification_id=notification_id)


@router.get("/files/{file_id}/comments", response_model=list[CommentOut])
def list_comments(file_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return CommentService(db).list_for_file(owner_id=user.id, file_id=file_id)


@router.post("/files/{file_id}/comments", response_model=CommentOut, status_code=201)
def add_comment(file_id: uuid.UUID, data: CommentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return CommentService(db).add_comment(
        owner_id=user.id, file_id=file_id, body=data.body, page_number=data.page_number, position=data.position
    )


@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment(comment_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    CommentService(db).delete_comment(owner_id=user.id, comment_id=comment_id)
