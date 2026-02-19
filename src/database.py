"""
Database configuration and session management.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Use SQLite for development, can be changed to PostgreSQL for production
DB_PATH = Path(__file__).parent.parent / "activities.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for FastAPI that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize the database with tables."""
    from models import Base
    Base.metadata.create_all(bind=engine)
