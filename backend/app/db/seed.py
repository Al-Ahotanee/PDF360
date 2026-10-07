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


# Predefined demo & default users for seeding
# Safe default password for seed users: "Password123!"
DEFAULT_USERS = [
    {
        "email": "superadmin@pdf360.internal",
        "full_name": "PDF360 Super Administrator",
        "role_name": "super_admin",
        "is_active": True,
        "is_verified": True,
    },
    {
        "email": "admin@pdf360.internal",
        "full_name": "PDF360 Organization Admin",
        "role_name": "admin",
        "is_active": True,
        "is_verified": True,
    },
    {
        "email": "pro@pdf360.internal",
        "full_name": "Alex Mercer (Pro Plan)",
        "role_name": "premium_user",
        "is_active": True,
        "is_verified": True,
    },
    {
        "email": "demo@pdf360.internal",
        "full_name": "Demo User (Free Plan)",
        "role_name": "registered_user",
        "is_active": True,
        "is_verified": True,
    },
]


def seed() -> None:
    from app.core.security import hash_password
    from app.models.user import User

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

        roles_by_name = {}
        for role_name in DEFAULT_ROLES:
            role = db.query(Role).filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
                db.add(role)
                db.flush()
            role.permissions = [permissions_by_code[c] for c in ROLE_PERMISSION_MAP[role_name]]
            roles_by_name[role_name] = role

        # Seed default users idempotently
        default_hashed_pw = hash_password("Password123!")
        users_created = 0
        for u_data in DEFAULT_USERS:
            existing = db.query(User).filter_by(email=u_data["email"]).first()
            if existing is None:
                role = roles_by_name[u_data["role_name"]]
                user_obj = User(
                    email=u_data["email"],
                    hashed_password=default_hashed_pw,
                    full_name=u_data["full_name"],
                    role_id=role.id,
                    is_active=u_data["is_active"],
                    is_verified=u_data["is_verified"],
                )
                db.add(user_obj)
                users_created += 1

        db.commit()
        print(f"Seeded {len(DEFAULT_ROLES)} roles and {len(DEFAULT_PERMISSIONS)} permissions.")
        print(f"Seeded {users_created} new users ({len(DEFAULT_USERS)} total configured).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
