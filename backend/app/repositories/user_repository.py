import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.role import Role
from app.models.user import User


class UserRepository:
    """
    All direct DB access for User lives here. Services call this instead of
    touching `db.query(...)` themselves — if we ever swap ORMs or add
    caching, only this file changes.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = select(User).options(joinedload(User.role)).where(User.id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).options(joinedload(User.role)).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_role_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, *, email: str, hashed_password: str, full_name: str | None, role_id: uuid.UUID) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role_id=role_id,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
