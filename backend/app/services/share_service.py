import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.file_share import FileShare, SharePermission
from app.repositories.file_repository import FileRepository
from app.repositories.file_share_repository import FileShareRepository
from app.repositories.user_repository import UserRepository
from app.services.collaboration_service import NotificationService


class ShareService:
    def __init__(self, db: Session):
        self.db = db
        self.files = FileRepository(db)
        self.shares = FileShareRepository(db)
        self.users = UserRepository(db)
        self.notifications = NotificationService(db)

    def _assert_owns_file(self, owner_id: uuid.UUID, file_id: uuid.UUID):
        file = self.files.get_by_id(file_id)
        if file is None or file.owner_id != owner_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
        return file

    def share_file(
        self,
        *,
        owner_id: uuid.UUID,
        file_id: uuid.UUID,
        with_email: str,
        permission: SharePermission,
    ) -> FileShare:
        file = self._assert_owns_file(owner_id, file_id)

        target_user = self.users.get_by_email(with_email)
        if target_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{with_email}' not found.",
            )

        if target_user.id == owner_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="You cannot share a file with yourself.",
            )

        share = self.shares.upsert(
            file_id=file_id,
            owner_id=owner_id,
            shared_with_id=target_user.id,
            permission=permission,
        )

        owner_user = self.users.get_by_id(owner_id)
        owner_name = (owner_user.full_name or owner_user.email) if owner_user else "Someone"

        self.notifications.create_for_user(
            user_id=target_user.id,
            title="File shared with you",
            body=f"{owner_name} shared '{file.original_filename}' with you ({permission.value} access).",
            metadata={"type": "file_share", "file_id": str(file_id), "permission": permission.value},
        )

        return share

    def list_shares_for_file(self, *, owner_id: uuid.UUID, file_id: uuid.UUID) -> list[FileShare]:
        self._assert_owns_file(owner_id, file_id)
        return self.shares.list_for_file(file_id)

    def revoke_share(self, *, owner_id: uuid.UUID, share_id: uuid.UUID) -> None:
        share = self.shares.get_by_id(share_id)
        if share is None or share.owner_id != owner_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share grant not found.")
        self.shares.delete(share)

    def list_shared_with_me(self, *, user_id: uuid.UUID) -> list[FileShare]:
        return self.shares.list_shared_with_user(user_id)
