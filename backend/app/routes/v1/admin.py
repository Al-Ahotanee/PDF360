import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin import AnalyticsOut, AuditLogOut, RoleOut, SetActiveRequest, SetRoleRequest, SystemHealthOut
from app.schemas.auth import UserOut
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


def _to_user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id, email=user.email, full_name=user.full_name,
        role=user.role.name, is_active=user.is_active, is_verified=user.is_verified,
    )


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_permission("admin:users:manage"))):
    return [_to_user_out(u) for u in AdminService(db).list_users()]


@router.patch("/users/{user_id}/role", response_model=UserOut)
def set_user_role(user_id: uuid.UUID, data: SetRoleRequest, db: Session = Depends(get_db),
                   actor: User = Depends(require_permission("admin:users:manage"))):
    return _to_user_out(AdminService(db).set_user_role(user_id=user_id, role_name=data.role_name, actor_id=actor.id))


@router.patch("/users/{user_id}/active", response_model=UserOut)
def set_user_active(user_id: uuid.UUID, data: SetActiveRequest, db: Session = Depends(get_db),
                     actor: User = Depends(require_permission("admin:users:manage"))):
    return _to_user_out(AdminService(db).set_user_active(user_id=user_id, is_active=data.is_active, actor_id=actor.id))


@router.get("/roles", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db), _: User = Depends(require_permission("admin:users:manage"))):
    return AdminService(db).list_roles()


@router.get("/audit-logs", response_model=list[AuditLogOut])
def list_audit_logs(db: Session = Depends(get_db), _: User = Depends(require_permission("admin:audit:read"))):
    return AdminService(db).list_audit_logs()


@router.get("/system-health", response_model=SystemHealthOut)
def system_health(db: Session = Depends(get_db), _: User = Depends(require_permission("admin:system:manage"))):
    return AdminService(db).system_health()


@router.get("/analytics", response_model=AnalyticsOut)
def analytics(db: Session = Depends(get_db), _: User = Depends(require_permission("admin:system:manage"))):
    return AdminService(db).analytics()
