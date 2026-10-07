import uuid

from sqlalchemy.orm import Session

from app.models.file import File
from app.models.file_share import SharePermission
from app.repositories.file_share_repository import FileShareRepository

_LEVEL = {
    SharePermission.VIEW: 1,
    SharePermission.COMMENT: 2,
    SharePermission.EDIT: 3,
}


def permission_for(db: Session, *, file: File, user_id: uuid.UUID) -> SharePermission | None:
    """EDIT if caller owns the file, otherwise whatever was granted via share, else None."""
    if file.owner_id == user_id:
        return SharePermission.EDIT
    share = FileShareRepository(db).get_for_file_and_user(file.id, user_id)
    return share.permission if share else None


def has_at_least(db: Session, *, file: File, user_id: uuid.UUID, required: SharePermission) -> bool:
    """Returns True if user has at least the required permission on the file."""
    perm = permission_for(db, file=file, user_id=user_id)
    return perm is not None and _LEVEL[perm] >= _LEVEL[required]
