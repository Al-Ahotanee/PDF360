import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.file import File
from app.models.job import Job


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_stats(self, owner_id: uuid.UUID) -> dict:
        storage_used = self.db.execute(
            select(func.coalesce(func.sum(File.size_bytes), 0)).where(
                File.owner_id == owner_id, File.is_trashed.is_(False)
            )
        ).scalar_one()

        file_count = self.db.execute(
            select(func.count(File.id)).where(File.owner_id == owner_id, File.is_trashed.is_(False))
        ).scalar_one()

        since = datetime.now(timezone.utc) - timedelta(days=30)
        jobs_last_30_days = self.db.execute(
            select(func.count(Job.id)).where(Job.owner_id == owner_id, Job.created_at >= since)
        ).scalar_one()

        return {
            "storage_used_bytes": storage_used,
            "file_count": file_count,
            "jobs_last_30_days": jobs_last_30_days,
        }

    def get_recent_files(self, owner_id: uuid.UUID, limit: int = 10) -> list[File]:
        stmt = (
            select(File)
            .where(File.owner_id == owner_id, File.is_trashed.is_(False))
            .order_by(File.created_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_favorite_files(self, owner_id: uuid.UUID) -> list[File]:
        stmt = select(File).where(File.owner_id == owner_id, File.is_favorite.is_(True), File.is_trashed.is_(False))
        return list(self.db.execute(stmt).scalars().all())

    def get_recent_jobs(self, owner_id: uuid.UUID, limit: int = 20) -> list[Job]:
        stmt = select(Job).where(Job.owner_id == owner_id).order_by(Job.created_at.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())
