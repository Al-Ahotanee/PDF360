"""
Seeds the five default roles and a starter permission set.

Run after migrations:
    python -m app.db.seed

Idempotent — safe to run multiple times; existing rows are left untouched.
"""
from app.db.session import SessionLocal

# Every model that participates in a relationship() elsewhere must be
# imported before mappers configure — SQLAlchemy resolves string-based
# relationship targets (e.g. Role.users -> "User") against whatever's been
# imported into this process, not just this module's own imports.
# Confirmed necessary by testing: running this script with only `role`
# imported raised InvalidRequestError trying to resolve "User".
from app.models import activity, billing, document_version, file, job, system, tag, user  # noqa: F401
from app.models.role import Permission, Role

DEFAULT_ROLES = ["guest", "registered_user", "premium_user", "admin", "super_admin"]

DEFAULT_PERMISSIONS = [
    "files:read", "files:create", "files:update", "files:delete",
    "files:merge", "files:split", "files:convert", "files:compress", "files:ocr",
    "ai:use",
    "admin:users:manage", "admin:system:manage", "admin:audit:read",
]

# Which roles get which permissions, by role name -> list of permission codes.
ROLE_PERMISSION_MAP = {
    "guest": ["files:read"],
    "registered_user": ["files:read", "files:create", "files:update", "files:delete",
                         "files:merge", "files:split", "files:convert", "files:compress"],
    "premium_user": ["files:read", "files:create", "files:update", "files:delete",
                      "files:merge", "files:split", "files:convert", "files:compress",
                      "files:ocr", "ai:use"],
    "admin": DEFAULT_PERMISSIONS,
    "super_admin": DEFAULT_PERMISSIONS,
}


def seed() -> None:
    db = SessionLocal()
    try:
        permissions_by_code = {}
        for code in DEFAULT_PERMISSIONS:
            perm = db.query(Permission).filter_by(code=code).first()
            if perm is None:
                perm = Permission(code=code)
                db.add(perm)
                db.flush()
            permissions_by_code[code] = perm

        for role_name in DEFAULT_ROLES:
            role = db.query(Role).filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
                db.add(role)
                db.flush()
            role.permissions = [permissions_by_code[c] for c in ROLE_PERMISSION_MAP[role_name]]

        db.commit()
        print(f"Seeded {len(DEFAULT_ROLES)} roles and {len(DEFAULT_PERMISSIONS)} permissions.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
