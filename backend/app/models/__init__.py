"""
Importing app.models (this package) guarantees every SQLAlchemy model
class is registered before any mapper is configured. Without this,
whichever route/script runs first only pulls in the model modules it
directly imports, and any relationship() with a string-based target class
that isn't among those fails with "failed to locate a name" — confirmed by
two real occurrences during testing (db/seed.py, and the live /auth/login
endpoint failing via File.versions -> "DocumentVersion").

Every entrypoint (main.py, db/seed.py, alembic/env.py) imports this
package (or the individual modules) before touching the DB.
"""
from app.models import (  # noqa: F401
    activity,
    billing,
    document_version,
    file,
    file_share,
    job,
    role,
    system,
    tag,
    user,
)
