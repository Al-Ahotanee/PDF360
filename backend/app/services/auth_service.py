from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPair, UserLogin, UserRegister

DEFAULT_ROLE_NAME = "registered_user"


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def register(self, data: UserRegister) -> User:
        if self.users.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email is already registered."
            )

        role = self.users.get_role_by_name(DEFAULT_ROLE_NAME)
        if role is None:
            # Should never happen once seed data has run — fail loudly rather
            # than silently assigning no role.
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default role is not configured. Run database seed script.",
            )

        return self.users.create(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            role_id=role.id,
        )

    def authenticate(self, data: UserLogin) -> User:
        user = self.users.get_by_email(data.email)
        if user is None or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated."
            )
        return user

    def issue_tokens(self, user: User) -> TokenPair:
        return TokenPair(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    def refresh_access_token(self, refresh_token: str) -> TokenPair:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token."
            )
        user_id = payload["sub"]
        user = self.users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
        return self.issue_tokens(user)
