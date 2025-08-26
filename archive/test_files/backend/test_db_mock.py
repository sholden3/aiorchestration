"""
Mock Database for Testing Without PostgreSQL
Evidence-Based Implementation: Allows test execution without external dependencies
"""

import asyncio
from unittest.mock import MagicMock, AsyncMock
from contextlib import asynccontextmanager

class MockConnection:
    """Mock database connection for testing"""
    
    async def fetchval(self, query):
        """Mock fetchval - returns 1 for SELECT 1"""
        if "SELECT 1" in query:
            return 1
        return None
    
    async def fetch(self, query):
        """Mock fetch - returns empty list"""
        return []
    
    async def execute(self, query, *args):
        """Mock execute - always succeeds with variable args"""
        return "EXECUTE 1"
    
    async def fetchrow(self, query, *args):
        """Mock fetchrow - returns None for cache queries"""
        return None
    
    async def close(self):
        """Mock close"""
        pass

class MockPool:
    """Mock connection pool for testing"""
    
    def __init__(self):
        self._size = 2
        self._connections = []
    
    @asynccontextmanager
    async def acquire(self):
        """Mock connection acquisition"""
        conn = MockConnection()
        self._connections.append(conn)
        try:
            yield conn
        finally:
            self._connections.remove(conn)
    
    def get_size(self):
        """Return pool size"""
        return self._size
    
    async def close(self):
        """Mock pool close"""
        pass

async def create_mock_pool(*args, **kwargs):
    """Create mock pool for testing"""
    return MockPool()

# Monkey patch for tests when PostgreSQL is not available
def patch_asyncpg():
    """Patch asyncpg for testing without PostgreSQL"""
    import sys
    from unittest.mock import Mock
    
    mock_asyncpg = Mock()
    mock_asyncpg.create_pool = create_mock_pool
    mock_asyncpg.Connection = MockConnection
    mock_asyncpg.Pool = MockPool
    
    sys.modules['asyncpg'] = mock_asyncpg
    return mock_asyncpg