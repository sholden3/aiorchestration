"""
@fileoverview Database connection and session management
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Backend - Database Layer
@business_logic Database connection pooling and session lifecycle
"""

import os
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy.engine import Engine

from .models import Base

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:root@localhost:5432/ai_assistant"
)

# For testing, use SQLite
TEST_DATABASE_URL = "sqlite:///./test.db"

# Determine which database to use
IS_TESTING = os.getenv("TESTING", "false").lower() == "true"
CURRENT_DATABASE_URL = TEST_DATABASE_URL if IS_TESTING else DATABASE_URL

# Create engine with appropriate pooling
if IS_TESTING:
    # SQLite for testing
    engine = create_engine(
        CURRENT_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=NullPool  # No pooling for SQLite
    )
else:
    # PostgreSQL for production
    engine = create_engine(
        CURRENT_DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,   # Recycle connections after 1 hour
        echo=os.getenv("SQL_ECHO", "false").lower() == "true"
    )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Enable foreign key constraints for SQLite
if IS_TESTING:
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized: {CURRENT_DATABASE_URL}")

def drop_db():
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped")

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database session
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database session
    
    Usage:
        with get_db_session() as db:
            db.query(Model).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    def health_check() -> dict:
        """Check database health"""
        try:
            with get_db_session() as db:
                # Simple query to verify connection
                db.execute("SELECT 1")
                return {
                    "status": "healthy",
                    "database": "connected",
                    "url": CURRENT_DATABASE_URL.split("@")[-1] if "@" in CURRENT_DATABASE_URL else "local"
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
    
    @staticmethod
    def get_table_counts() -> dict:
        """Get row counts for all tables"""
        counts = {}
        with get_db_session() as db:
            for table in Base.metadata.tables.keys():
                try:
                    count = db.execute(f"SELECT COUNT(*) FROM {table}").scalar()
                    counts[table] = count
                except:
                    counts[table] = 0
        return counts
    
    @staticmethod
    def seed_initial_data():
        """Seed database with initial data"""
        from .seeds import seed_rules, seed_practices, seed_templates
        
        with get_db_session() as db:
            # Check if already seeded
            from .models import Rule
            if db.query(Rule).count() > 0:
                print("Database already seeded")
                return
            
            # Seed data
            seed_rules(db)
            seed_practices(db)
            seed_templates(db)
            print("Database seeded successfully")

# Export commonly used items
__all__ = [
    'engine',
    'SessionLocal',
    'get_db',
    'get_db_session',
    'init_db',
    'drop_db',
    'DatabaseManager'
]