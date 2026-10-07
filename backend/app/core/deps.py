"""
Reusable FastAPI dependencies: current-user resolution and permission checks.

Usage in a route:
    @router.delete("/files/{file_id}")
    def delete_file(user: User = Depends(require_permission("files:delete"))):
        ...

`require_permission` is a dependency *factory* — it returns a dependency
closed over the required permission string, so RBAC checks read declaratively
at the route signature instead of as if-statements inside handler bodies.
"""
import uuid
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    token_header: str | None = Depends(oauth2_scheme),
    token_query: str | None = Query(None, alias="token"),
    db: Session = Depends(get_db),
) -> User:
    token = token_header or token_query
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_uuid = uuid.UUID(payload["sub"]) if isinstance(payload["sub"], str) else payload["sub"]
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload structure.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = UserRepository(db).get_by_id(user_uuid)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")
    return user


def require_permission(permission_code: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        user_permission_codes = {p.code for p in user.role.permissions}
        if permission_code not in user_permission_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission_code}",
            )
        return user

    return dependency
