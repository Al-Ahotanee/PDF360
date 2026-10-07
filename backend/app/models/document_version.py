import uuid

from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class DocumentVersion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Every edit/operation that produces a new file body (not just metadata)
    creates a new version row instead of overwriting storage_key on File.
    File.storage_key always mirrors the *latest* version for fast reads;
    older versions stay addressable for restore/diff.
    """
    __tablename__ = "document_versions"

    file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"))
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_key: Mapped[str] = mapped_column(String(1000), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    change_note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    file: Mapped["File"] = relationship(back_populates="versions")
