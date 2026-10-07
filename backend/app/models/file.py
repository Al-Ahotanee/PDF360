import uuid

from sqlalchemy import BigInteger, Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Folder(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "folders"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("folders.id", ondelete="CASCADE"), nullable=True
    )
    is_trashed: Mapped[bool] = mapped_column(Boolean, default=False)

    parent: Mapped["Folder | None"] = relationship(remote_side="Folder.id", back_populates="children")
    children: Mapped[list["Folder"]] = relationship(back_populates="parent")
    files: Mapped[list["File"]] = relationship(back_populates="folder")


class File(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Represents a stored object (usually a PDF, but also source files used for
    "convert to PDF" — Word/Excel/PPT/images before conversion).

    `storage_key` is the path/key inside whichever StorageProvider is active
    (local disk path today, S3 object key later) — never expose it directly
    to clients; always resolve it through the storage service so swapping
    providers doesn't break download links.
    """
    __tablename__ = "files"

    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    folder_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("folders.id", ondelete="SET NULL"), nullable=True
    )

    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(1000), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)

    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    is_trashed: Mapped[bool] = mapped_column(Boolean, default=False)

    folder: Mapped["Folder | None"] = relationship(back_populates="files")
    tags: Mapped[list["Tag"]] = relationship(secondary="file_tags", back_populates="files")
    versions: Mapped[list["DocumentVersion"]] = relationship(back_populates="file", order_by="DocumentVersion.version_number")
