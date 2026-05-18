"""SQLAlchemy base for all models."""
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Get database URL from environment. Dev scripts set both names; supporting
# BACKEND_DATABASE_URL keeps this module aligned with the pydantic settings
# prefix used by the rest of the backend.
DATABASE_URL = (
    os.getenv("DATABASE_URL")
    or os.getenv("BACKEND_DATABASE_URL")
    or "postgresql+psycopg://postgres:postgres@localhost:5432/medisign"
)

# Create engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# Dependency for getting DB session
def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
