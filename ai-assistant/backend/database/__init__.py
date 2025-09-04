"""
Database Module

Database models, migrations, and connection management.
Supports PostgreSQL with SQLite fallback.

Recovery Note: Created 2025-09-03 during dependency recovery (DEC-2025-010)
"""

# Database configuration constants
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 40
DATABASE_POOL_TIMEOUT = 30