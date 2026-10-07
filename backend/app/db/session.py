"""
Database engine + session management.

`get_db` is a FastAPI dependency — routes never import SessionLocal directly,
they take `db: Session = Depends(get_db)`. This keeps session lifecycle
(open/close/rollback-on-error) in one place.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # avoids stale-connection errors against Neon's pooler
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
