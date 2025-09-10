"""
Database connection management for Supabase PostgreSQL.
"""

import os
from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from config import config

def get_database_url() -> Optional[str]:
    """Get database URL from configuration."""
    return config.get("database_url")

def create_engine() -> Engine:
    """Create SQLAlchemy engine with connection pooling."""
    database_url = get_database_url()

    if not database_url:
        raise ValueError("DATABASE_URL is not configured. Please set it in your .env file.")

    # Create engine for Supabase
    from sqlalchemy import create_engine
    engine = create_engine(database_url, echo=False)

    return engine

def get_session(engine: Optional[Engine] = None) -> Session:
    """Get database session."""
    if engine is None:
        engine = create_engine()

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def test_connection() -> bool:
    """Test database connection."""
    try:
        engine = create_engine()
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            row = result.fetchone()
            return row is not None
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False