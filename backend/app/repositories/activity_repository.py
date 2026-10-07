import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import ActivityLog


class ActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: uuid.UUID, limit: int = 50) -> list[ActivityLog]:
        stmt = (
            select(ActivityLog)
            .where(ActivityLog.user_id == user_id)
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def create(
        self,
        *,
        user_id: uuid.UUID,
        action: str,
        resource_type: str | None = None,
        resource_id: uuid.UUID | None = None,
        metadata_json: dict | None = None,
    ) -> ActivityLog:
        log = ActivityLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata_json=metadata_json or {},
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
