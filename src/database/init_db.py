"""
Database initialization script for Supabase PostgreSQL.
"""

from .connection import create_engine
from .models import Base
from config import config
import logging

logger = logging.getLogger(__name__)

def init_database():
    """Initialize database by creating all tables."""
    try:
        logger.info("Initializing database...")

        # Create engine
        engine = create_engine()

        # Create all tables
        Base.metadata.create_all(bind=engine)

        logger.info("Database initialized successfully!")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

def drop_database():
    """Drop all tables (use with caution!)."""
    try:
        logger.warning("Dropping all database tables...")

        engine = create_engine()
        Base.metadata.drop_all(bind=engine)

        logger.info("All tables dropped successfully!")
        return True

    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        return False

if __name__ == "__main__":
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)

    # Initialize database
    success = init_database()
    if success:
        print("✅ Database initialization completed!")
    else:
        print("❌ Database initialization failed!")
        exit(1)