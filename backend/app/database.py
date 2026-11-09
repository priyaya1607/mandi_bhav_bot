import logging
from typing import Any
from .config import settings

logger = logging.getLogger(__name__)

engine = None
SessionLocal = None
Base = None

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import declarative_base, sessionmaker, Session

    database_url = settings.DATABASE_URL
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    try:
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as e:
        logger.warning(f"PostgreSQL engine initialization deferred: {e}")

    Base = declarative_base()
except ImportError:
    logger.warning("SQLAlchemy not installed. Backend running in memory-cache mode.")
    class DummyBase:
        metadata = None
    Base = DummyBase
    Session = Any


def get_db():
    """FastAPI Dependency for database session."""
    if SessionLocal is None:
        yield None
        return
        
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> dict:
    """Verifies PostgreSQL connectivity."""
    if engine is None:
        return {"connected": False, "error": "PostgreSQL engine not initialized or database offline"}
    try:
        with engine.connect() as connection:
            return {"connected": True, "database": "PostgreSQL"}
    except Exception as e:
        return {"connected": False, "error": str(e), "database": "PostgreSQL"}
