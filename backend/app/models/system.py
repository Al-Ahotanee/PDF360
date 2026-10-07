import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ApiKey(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Developer API keys for programmatic access (Phase 16 — user dashboard
    exposes these). We store only a hash of the key, never the raw value —
    same pattern as password hashing.
    """
    __tablename__ = "api_keys"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(12), nullable=False)  # shown in UI, e.g. "pdf360_ab12"
    hashed_key: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_used_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Setting(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Per-user settings (theme, default export format, notification prefs, etc.)."""
    __tablename__ = "settings"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict)


class SystemConfiguration(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Global, admin-editable key/value config (feature flags, storage quotas,
    maintenance mode, etc.) — read through a cached service, not directly,
    so a config change doesn't require a redeploy.
    """
    __tablename__ = "system_configuration"

    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
