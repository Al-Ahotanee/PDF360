import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.activity import AuditLog
from app.models.billing import Payment, PaymentStatus, Subscription, SubscriptionPlan
from app.models.file import File
from app.models.job import Job, JobStatus
from app.models.role import Role
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def list_users(self, limit: int = 100) -> list[User]:
        stmt = select(User).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def set_user_role(self, *, user_id: uuid.UUID, role_name: str, actor_id: uuid.UUID | None = None) -> User:
        user = self.users.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        role = self.users.get_role_by_name(role_name)
        if role is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Unknown role: {role_name}")
        previous_role = user.role.name if user.role else None
        user.role_id = role.id
        self.db.commit()
        self.db.refresh(user)
        self._write_audit(actor_id, "admin.user.role_changed", "user", user.id, {"from": previous_role, "to": role_name})
        return user

    def set_user_active(self, *, user_id: uuid.UUID, is_active: bool, actor_id: uuid.UUID | None = None) -> User:
        user = self.users.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        user.is_active = is_active
        self.db.commit()
        self.db.refresh(user)
        self._write_audit(actor_id, "admin.user.active_changed", "user", user.id, {"is_active": is_active})
        return user

    def list_roles(self) -> list[Role]:
        return list(self.db.execute(select(Role)).scalars().all())

    def _write_audit(self, actor_id: uuid.UUID | None, action: str, target_type: str,
                      target_id: uuid.UUID | None, metadata: dict) -> None:
        self.db.add(AuditLog(actor_id=actor_id, action=action, target_type=target_type,
                              target_id=target_id, metadata_json=metadata))
        self.db.commit()

    def list_audit_logs(self, limit: int = 100) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def system_health(self) -> dict:
        return {
            "status": "ok",
            "queued_jobs": self.db.execute(select(func.count()).select_from(Job).where(Job.status == JobStatus.QUEUED)).scalar_one(),
            "processing_jobs": self.db.execute(select(func.count()).select_from(Job).where(Job.status == JobStatus.PROCESSING)).scalar_one(),
            "failed_jobs_last_100": sum(
                1 for j in self.db.execute(select(Job.status).order_by(Job.created_at.desc()).limit(100)).scalars()
                if j == JobStatus.FAILED
            ),
        }

    def analytics(self) -> dict:
        total_users = self.db.execute(select(func.count()).select_from(User)).scalar_one()
        active_users = self.db.execute(select(func.count()).select_from(User).where(User.is_active.is_(True))).scalar_one()
        total_files = self.db.execute(select(func.count()).select_from(File)).scalar_one()
        total_jobs = self.db.execute(select(func.count()).select_from(Job)).scalar_one()
        premium_subs = self.db.execute(
            select(func.count()).select_from(Subscription).where(
                Subscription.plan.in_([SubscriptionPlan.PREMIUM_MONTHLY, SubscriptionPlan.PREMIUM_YEARLY])
            )
        ).scalar_one()
        revenue = self.db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.status == PaymentStatus.SUCCEEDED)
        ).scalar_one()
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_files": total_files,
            "total_jobs": total_jobs,
            "premium_subscribers": premium_subs,
            "total_revenue": float(revenue),
        }

    def list_feature_flags(self):
        from app.repositories.system_config_repository import SystemConfigRepository
        return SystemConfigRepository(self.db).list_all()

    def set_feature_flag(self, *, key: str, value: dict, description: str | None = None, actor_id: uuid.UUID | None = None):
        from app.repositories.system_config_repository import SystemConfigRepository
        cfg = SystemConfigRepository(self.db).set_key(key=key, value=value, description=description)
        self._write_audit(actor_id, "admin.feature_flag.set", "system_configuration", cfg.id, {"key": key, "value": value})
        return cfg

    def delete_feature_flag(self, *, key: str, actor_id: uuid.UUID | None = None) -> bool:
        from app.repositories.system_config_repository import SystemConfigRepository
        deleted = SystemConfigRepository(self.db).delete_key(key)
        if deleted:
            self._write_audit(actor_id, "admin.feature_flag.deleted", "system_configuration", None, {"key": key})
        return deleted

