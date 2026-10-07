import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Notification(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    # e.g. {"type": "job_complete", "job_id": "..."} — lets the frontend
    # deep-link a notification without new columns per notification type.
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)


class Comment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "comments"

    file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"))
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    # Page/position anchor for annotation-style comments on the PDF viewer.
    page_number: Mapped[int | None] = mapped_column(nullable=True)
    position: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    mentioned_user_ids: Mapped[list] = mapped_column(JSONB, default=list)


class ActivityLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """User-facing activity feed — 'you merged report.pdf', 'you shared X with Y'."""
    __tablename__ = "activity_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "file.merge"
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)


class AuditLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Admin/security-sensitive audit trail — distinct from ActivityLog:
    covers permission changes, admin actions, login attempts, etc., and is
    never shown in a normal user's activity feed.
    """
    __tablename__ = "audit_logs"

    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "admin.user.role_changed"
    target_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)
