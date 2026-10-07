from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import RefreshRequest, TokenPair, UserLogin, UserOut, UserRegister
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register(data)
    return UserOut(
        id=user.id, email=user.email, full_name=user.full_name,
        role=user.role.name, is_active=user.is_active, is_verified=user.is_verified,
    )


@router.post("/login", response_model=TokenPair)
def login(data: UserLogin, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.authenticate(data)
    return service.issue_tokens(user)


@router.post("/refresh", response_model=TokenPair)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.refresh_access_token(data.refresh_token)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut(
        id=user.id, email=user.email, full_name=user.full_name,
        role=user.role.name, is_active=user.is_active, is_verified=user.is_verified,
    )
