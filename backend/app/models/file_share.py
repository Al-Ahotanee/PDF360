from datetime import datetime
import enum
import uuid

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SharePermission(str, enum.Enum):
    VIEW = "view"
    COMMENT = "comment"
    EDIT = "edit"


class FileShare(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Grants shared_with_id access to file_id at `permission`.
    - VIEW: download, preview, page-count, read bookmarks
    - COMMENT: additionally allows reading and posting comments
    - EDIT: additionally allows running PDF operations against the file
    Direct user-to-user grants only.
    """
    __tablename__ = "file_shares"
    __table_args__ = (
        UniqueConstraint("file_id", "shared_with_id", name="uq_file_shares_file_user"),
    )

    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), index=True, nullable=False
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    shared_with_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    permission: Mapped[SharePermission] = mapped_column(
        Enum(
            SharePermission,
            name="share_permission",
            values_callable=lambda x: [e.value for e in x],
            create_type=False,
        ),
        nullable=False,
    )

    file: Mapped["File"] = relationship()
    shared_with: Mapped["User"] = relationship(foreign_keys=[shared_with_id])
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id])


class PublicShare(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Public share links allowing anyone with the URL (and optional password)
    to view and download a file, with an optional expiration timestamp.
    """
    __tablename__ = "public_shares"

    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), index=True, nullable=False
    )
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    share_token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    allow_download: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    file: Mapped["File"] = relationship()
    created_by: Mapped["User"] = relationship()
