import re
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.file_share import SharePermission
from app.repositories.collaboration_repository import CommentRepository, NotificationRepository
from app.repositories.file_repository import FileRepository
from app.repositories.user_repository import UserRepository
from app.services.file_access import has_at_least


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
        """Called internally rather than exposed as a public write endpoint."""
        return self.notifications.create(user_id=user_id, title=title, body=body, metadata=metadata or {})


class CommentService:
    def __init__(self, db: Session):
        self.db = db
        self.comments = CommentRepository(db)
        self.files = FileRepository(db)
        self.users = UserRepository(db)
        self.notifications = NotificationService(db)

    def _get_accessible_file(self, user_id: uuid.UUID, file_id: uuid.UUID, required: SharePermission):
        file = self.files.get_by_id(file_id)
        if file is None or not has_at_least(self.db, file=file, user_id=user_id, required=required):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found or access denied.")
        return file

    def list_for_file(self, *, user_id: uuid.UUID, file_id: uuid.UUID):
        self._get_accessible_file(user_id, file_id, required=SharePermission.VIEW)
        return self.comments.list_for_file(file_id)

    def add_comment(
        self,
        *,
        author_id: uuid.UUID,
        file_id: uuid.UUID,
        body: str,
        page_number: int | None,
        position: dict | None,
    ):
        file = self._get_accessible_file(author_id, file_id, required=SharePermission.COMMENT)

        # Parse mentions (@username or @email)
        mentioned_user_ids: list[str] = []
        author = self.users.get_by_id(author_id)
        author_name = (author.full_name or author.email) if author else "Someone"

        # Regex for @email or @handle
        matches = re.findall(r"@([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+|[a-zA-Z0-9_.-]+)", body)
        for match in set(matches):
            target_user = self.users.get_by_email(match)
            if not target_user and "@" not in match:
                # Try finding by full_name or email prefix
                target_user = self.db.query(self.users.model if hasattr(self.users, "model") else author.__class__).filter(
                    author.__class__.email.ilike(f"{match}@%")
                ).first()
            if target_user and target_user.id != author_id:
                uid_str = str(target_user.id)
                if uid_str not in mentioned_user_ids:
                    mentioned_user_ids.append(uid_str)
                    self.notifications.create_for_user(
                        user_id=target_user.id,
                        title="Mentioned in a comment",
                        body=f"{author_name} mentioned you in a comment on '{file.original_filename}'.",
                        metadata={"type": "comment_mention", "file_id": str(file_id)},
                    )

        comment = self.comments.create(
            file_id=file_id,
            author_id=author_id,
            body=body,
            page_number=page_number,
            position=position,
        )
        if mentioned_user_ids:
            comment.mentioned_user_ids = [uuid.UUID(u) for u in mentioned_user_ids]
            self.db.commit()
            self.db.refresh(comment)

        # If author is not the file owner, notify the file owner
        if file.owner_id != author_id and str(file.owner_id) not in mentioned_user_ids:
            self.notifications.create_for_user(
                user_id=file.owner_id,
                title="New comment on your file",
                body=f"{author_name} commented on '{file.original_filename}'.",
                metadata={"type": "file_comment", "file_id": str(file_id)},
            )

        return comment

    def delete_comment(self, *, user_id: uuid.UUID, comment_id: uuid.UUID):
        comment = self.comments.get_by_id(comment_id)
        if comment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")
        file = self.files.get_by_id(comment.file_id)
        # Allowed if user authored the comment or owns the file
        if comment.author_id != user_id and (file is None or file.owner_id != user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete this comment.")
        self.comments.delete(comment)
