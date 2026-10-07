import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.collaboration_repository import CommentRepository, NotificationRepository
from app.repositories.file_repository import FileRepository


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationRepository(db)

    def list_for_user(self, user_id: uuid.UUID, unread_only: bool = False):
        return self.notifications.list_for_user(user_id, unread_only)

    def mark_read(self, *, user_id: uuid.UUID, notification_id: uuid.UUID):
        n = self.notifications.get_by_id(notification_id)
        if n is None or n.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
        return self.notifications.mark_read(n)

    def create_for_user(self, *, user_id: uuid.UUID, title: str, body: str | None = None, metadata: dict | None = None):
        """Called internally (e.g. by job completion hooks) rather than exposed as a public write endpoint."""
        return self.notifications.create(user_id=user_id, title=title, body=body, metadata=metadata or {})


class CommentService:
    def __init__(self, db: Session):
        self.db = db
        self.comments = CommentRepository(db)
        self.files = FileRepository(db)

    def _assert_owns_file(self, owner_id: uuid.UUID, file_id: uuid.UUID):
        file = self.files.get_by_id(file_id)
        if file is None or file.owner_id != owner_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")

    def list_for_file(self, *, owner_id: uuid.UUID, file_id: uuid.UUID):
        self._assert_owns_file(owner_id, file_id)
        return self.comments.list_for_file(file_id)

    def add_comment(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, body: str,
                     page_number: int | None, position: dict | None):
        self._assert_owns_file(owner_id, file_id)
        return self.comments.create(file_id=file_id, author_id=owner_id, body=body, page_number=page_number, position=position)

    def delete_comment(self, *, owner_id: uuid.UUID, comment_id: uuid.UUID):
        comment = self.comments.get_by_id(comment_id)
        if comment is None or comment.author_id != owner_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")
        self.comments.delete(comment)
