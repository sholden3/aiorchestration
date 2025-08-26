"""
Test fixtures for database and system testing
Provides mock PostgreSQL connection for tests
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
import asyncpg
from typing import Dict, Any

@pytest.fixture
async def mock_db_connection():
    """Mock database connection for testing"""
    conn = AsyncMock(spec=asyncpg.Connection)
    
    # Mock execute method
    async def mock_execute(query, *args):
        if "CREATE TABLE" in query:
            return "CREATE TABLE"
        elif "INSERT" in query:
            return "INSERT 0 1"
        elif "SELECT" in query:
            return []
        return None
    
    conn.execute = mock_execute
    conn.fetchrow = AsyncMock(return_value=None)
    conn.fetch = AsyncMock(return_value=[])
    
    return conn

@pytest.fixture
async def mock_db_pool():
    """Mock database connection pool"""
    pool = AsyncMock(spec=asyncpg.Pool)
    
    # Create mock connection directly (not via fixture)
    conn = AsyncMock(spec=asyncpg.Connection)
    
    # Mock execute method
    async def mock_execute(query, *args):
        if "CREATE TABLE" in query:
            return "CREATE TABLE"
        elif "INSERT" in query:
            return "INSERT 0 1"
        elif "SELECT" in query:
            return []
        return None
    
    conn.execute = mock_execute
    conn.fetchrow = AsyncMock(return_value=None)
    conn.fetch = AsyncMock(return_value=[])
    
    # Mock acquire context manager
    class MockAcquire:
        async def __aenter__(self):
            return conn
        async def __aexit__(self, *args):
            pass
    
    pool.acquire = lambda: MockAcquire()
    pool.close = AsyncMock()
    
    return pool

@pytest.fixture
def mock_database_manager(mock_db_pool):
    """Mock DatabaseManager with pool"""
    from database_manager import DatabaseManager
    from config import Config
    
    config = Config()
    manager = DatabaseManager(config)
    manager.pool = mock_db_pool
    
    return manager

@pytest.fixture
def test_config():
    """Test configuration with safe defaults"""
    from config import Config
    import os
    
    # Set test environment variables
    os.environ['DB_HOST'] = 'test_host'
    os.environ['DB_NAME'] = 'test_db'
    os.environ['BACKEND_HOST'] = '127.0.0.1'
    
    config = Config()
    
    # Override with test values
    config.systems.db_host = 'test_host'
    config.systems.db_name = 'test_db'
    config.systems.cache_hot_size_mb = 10  # Small for testing
    config.systems.cache_warm_size_mb = 20
    
    return config

@pytest.fixture
async def test_cache():
    """Test cache with small memory limits"""
    from cache_manager import IntelligentCache
    
    cache = IntelligentCache(
        hot_size_mb=1,  # 1MB for testing
        warm_size_mb=2   # 2MB for testing
    )
    
    # Clear any existing cache
    await cache.clear()
    
    yield cache
    
    # Cleanup
    await cache.clear()

@pytest.fixture
def mock_claude_integration():
    """Mock Claude integration for testing"""
    from claude_integration import ClaudeIntegration
    
    mock_claude = MagicMock(spec=ClaudeIntegration)
    
    # Mock methods
    async def mock_call_claude(prompt, **kwargs):
        return {
            'response': f'Mock response to: {prompt[:50]}...',
            'tokens_used': len(prompt) // 4,
            'success': True
        }
    
    mock_claude.call_claude = mock_call_claude
    mock_claude.estimate_tokens = lambda x: len(x) // 4
    
    return mock_claude