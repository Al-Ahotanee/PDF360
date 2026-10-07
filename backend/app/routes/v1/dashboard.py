from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import ActivityLogOut, DashboardStats
from app.schemas.pdf import FileOut, JobOut
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return DashboardService(db).get_stats(user.id)


@router.get("/recent-files", response_model=list[FileOut])
def recent_files(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return DashboardService(db).get_recent_files(user.id)


@router.get("/favorite-files", response_model=list[FileOut])
def favorite_files(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return DashboardService(db).get_favorite_files(user.id)


@router.get("/recent-jobs", response_model=list[JobOut])
def recent_jobs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return DashboardService(db).get_recent_jobs(user.id)


@router.get("/activity", response_model=list[ActivityLogOut])
def recent_activity(limit: int = 20, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return DashboardService(db).get_recent_activity(user.id, limit=limit)

