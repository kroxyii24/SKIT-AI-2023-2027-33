"""
Database session management.

Note: this file is imported by nearly every route module (`from app.db.session
import get_db`) but was never actually produced as its own artifact in the
milestone files — it's added here to make the codebase importable/runnable.
Mirrors the pattern already used in tests/integration/conftest.py, but wired
to the real Postgres URL from settings instead of an in-memory SQLite DB.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """FastAPI dependency — yields a DB session and guarantees it closes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
