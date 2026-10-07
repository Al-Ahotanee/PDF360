import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Comment, Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: uuid.UUID, unread_only: bool = False) -> list[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.is_read.is_(False))
        stmt = stmt.order_by(Notification.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, notification_id: uuid.UUID) -> Notification | None:
        return self.db.execute(select(Notification).where(Notification.id == notification_id)).scalar_one_or_none()

    def create(self, *, user_id: uuid.UUID, title: str, body: str | None, metadata: dict) -> Notification:
        n = Notification(user_id=user_id, title=title, body=body, metadata_json=metadata)
        self.db.add(n)
        self.db.commit()
        self.db.refresh(n)
        return n

    def mark_read(self, notification: Notification) -> Notification:
        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        return notification


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_file(self, file_id: uuid.UUID) -> list[Comment]:
        stmt = select(Comment).where(Comment.file_id == file_id).order_by(Comment.created_at.asc())
        return list(self.db.execute(stmt).scalars().all())

    def create(self, *, file_id: uuid.UUID, author_id: uuid.UUID, body: str,
               page_number: int | None, position: dict | None) -> Comment:
        c = Comment(file_id=file_id, author_id=author_id, body=body, page_number=page_number, position=position)
        self.db.add(c)
        self.db.commit()
        self.db.refresh(c)
        return c

    def get_by_id(self, comment_id: uuid.UUID) -> Comment | None:
        return self.db.execute(select(Comment).where(Comment.id == comment_id)).scalar_one_or_none()

    def delete(self, comment: Comment) -> None:
        self.db.delete(comment)
        self.db.commit()
