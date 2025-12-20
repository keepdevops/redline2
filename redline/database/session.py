"""
SQLAlchemy Session Management for VarioSync
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from .models import Base

logger = logging.getLogger(__name__)

# Get Supabase connection string from environment
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD', '')

# Extract project ref from SUPABASE_URL (https://xxxxx.supabase.co)
project_ref = SUPABASE_URL.split('//')[1].split('.')[0] if SUPABASE_URL and '//' in SUPABASE_URL else ''

# Build PostgreSQL connection string (using Supabase connection pooler)
# Format: postgresql://postgres.PROJECT_REF:PASSWORD@aws-1-us-west-1.pooler.supabase.com:5432/postgres
if project_ref and SUPABASE_DB_PASSWORD:
    DATABASE_URL = f'postgresql://postgres.{project_ref}:{SUPABASE_DB_PASSWORD}@aws-1-us-west-1.pooler.supabase.com:5432/postgres'
else:
    DATABASE_URL = None
    logger.warning("SUPABASE_URL or SUPABASE_DB_PASSWORD not set - database connection unavailable")

# Create SQLAlchemy engine (only if DATABASE_URL is configured)
if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before using
        echo=False  # Set to True for SQL debugging
    )

    # Create session factory
    SessionLocal = scoped_session(sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    ))
else:
    engine = None
    SessionLocal = None


@contextmanager
def get_db_session():
    """
    Context manager for database sessions

    Usage:
        with get_db_session() as session:
            user = session.query(UserHours).filter_by(user_id=user_id).first()
    """
    if SessionLocal is None:
        raise RuntimeError("Database not configured - set SUPABASE_URL and SUPABASE_DB_PASSWORD in .env")

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """Initialize database (create all tables)"""
    if engine is None:
        raise RuntimeError("Database not configured - set SUPABASE_URL and SUPABASE_DB_PASSWORD in .env")

    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def drop_db():
    """Drop all tables (use with caution!)"""
    if engine is None:
        raise RuntimeError("Database not configured - set SUPABASE_URL and SUPABASE_DB_PASSWORD in .env")

    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("All tables dropped")
