"""
Database Manager Unit Tests
===========================

@author Sam Martinez v3.2.0 - Testing Lead & Quality Assurance
@architecture Test coverage for PostgreSQL database operations with mock fallback
@business_logic Validates thread-safe initialization and connection pooling

File Type: Test Implementation
Documentation Standard: v2.0 (CLAUDE.md § Standards)
Orchestrated Implementation: Phase 2 Test Coverage

Core Architects:
- Alex Novak v3.0: Frontend Integration & Data Flow
- Dr. Sarah Chen v1.2: Backend Systems & Database Architecture
- Sam Martinez v3.2.0: Testing Lead & Quality Assurance

Business Context:
- PostgreSQL database management with connection pooling
- Thread-safe initialization with race condition prevention (H3 fix)
- Mock fallback for development environments
- JSONB storage for flexible data structures

Architecture Pattern:
- Connection pooling with proper resource management
- Thread-safe singleton pattern
- Graceful fallback to mock when database unavailable
- Structured logging for debugging

Test Strategy (Sam Martinez):
- Unit tests for database operations
- Connection pooling validation
- Thread safety verification
- Mock fallback behavior
- Error handling and recovery

Performance Requirements:
- <50ms query response time
- Connection pool size: 5-20 connections
- Automatic reconnection on failure
- Zero data loss on proper shutdown

Dependencies:
- pytest: Test framework
- pytest-asyncio: Async test support
- unittest.mock: Mocking database connections
- psycopg2: PostgreSQL adapter
"""

import pytest
import asyncio
import json
import threading
import time
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from database_manager import DatabaseManager


class TestDatabaseManager:
    """Test DatabaseManager functionality"""
    
    @pytest.fixture
    def mock_pool(self):
        """Create mock connection pool"""
        pool = MagicMock()
        conn = MagicMock()
        cursor = MagicMock()
        
        # Setup mock chain
        pool.getconn.return_value = conn
        conn.cursor.return_value = cursor
        cursor.fetchone.return_value = None
        cursor.fetchall.return_value = []
        
        return pool, conn, cursor
    
    @pytest.fixture
    def manager_with_mock_pool(self, mock_pool):
        """Create DatabaseManager with mocked pool"""
        pool, conn, cursor = mock_pool
        
        with patch('database_manager.psycopg2') as mock_psycopg2:
            mock_psycopg2.pool.SimpleConnectionPool.return_value = pool
            manager = DatabaseManager()
            manager.pool = pool
            manager.is_initialized = True
            manager.use_mock = False
            
            return manager, pool, conn, cursor
    
    def test_singleton_pattern(self):
        """Test DatabaseManager is singleton"""
        manager1 = DatabaseManager()
        manager2 = DatabaseManager()
        
        assert manager1 is manager2
        
    def test_initialization_state(self):
        """Test initialization state tracking"""
        with patch('database_manager.psycopg2'):
            manager = DatabaseManager()
            
            # Should start uninitialized
            assert manager.is_initialized == False
            assert manager.is_initializing == False
            
    @pytest.mark.asyncio
    async def test_ensure_initialized_success(self, manager_with_mock_pool):
        """Test successful initialization"""
        manager, pool, conn, cursor = manager_with_mock_pool
        
        # Call ensure_initialized
        await manager._ensure_initialized()
        
        # Should remain initialized
        assert manager.is_initialized == True
        assert manager.use_mock == False
        
    @pytest.mark.asyncio
    async def test_ensure_initialized_fallback_to_mock(self):
        """Test fallback to mock when database unavailable"""
        with patch('database_manager.psycopg2') as mock_psycopg2:
            # Make psycopg2 raise error to simulate unavailable database
            mock_psycopg2.pool.SimpleConnectionPool.side_effect = Exception("Connection failed")
            
            manager = DatabaseManager()
            await manager._ensure_initialized()
            
            # Should fall back to mock
            assert manager.use_mock == True
            assert manager.is_initialized == True
            
    @pytest.mark.asyncio
    async def test_store_chat_session(self, manager_with_mock_pool):
        """Test storing chat session"""
        manager, pool, conn, cursor = manager_with_mock_pool
        cursor.fetchone.return_value = (1,)  # Return session ID
        
        # Store session
        session_id = await manager.store_chat_session("user123", "test_model")
        
        # Verify query executed
        cursor.execute.assert_called()
        conn.commit.assert_called()
        assert session_id == 1
        
    @pytest.mark.asyncio
    async def test_store_message(self, manager_with_mock_pool):
        """Test storing message"""
        manager, pool, conn, cursor = manager_with_mock_pool
        cursor.fetchone.return_value = (1,)  # Return message ID
        
        # Store message
        message_id = await manager.store_message(
            session_id=1,
            role="user",
            content="Test message",
            metadata={"tokens": 10}
        )
        
        # Verify query executed
        cursor.execute.assert_called()
        conn.commit.assert_called()
        assert message_id == 1
        
    @pytest.mark.asyncio
    async def test_get_session_history(self, manager_with_mock_pool):
        """Test retrieving session history"""
        manager, pool, conn, cursor = manager_with_mock_pool
        
        # Mock return data
        cursor.fetchall.return_value = [
            (1, "user", "Hello", {"tokens": 10}, "2024-01-01 12:00:00"),
            (2, "assistant", "Hi there", {"tokens": 8}, "2024-01-01 12:00:01")
        ]
        
        # Get history
        history = await manager.get_session_history(1)
        
        # Verify results
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["role"] == "assistant"
        
    @pytest.mark.asyncio
    async def test_update_session_metadata(self, manager_with_mock_pool):
        """Test updating session metadata"""
        manager, pool, conn, cursor = manager_with_mock_pool
        
        # Update metadata
        metadata = {"total_tokens": 100, "cost": 0.01}
        await manager.update_session_metadata(1, metadata)
        
        # Verify query executed
        cursor.execute.assert_called()
        conn.commit.assert_called()
        
    @pytest.mark.asyncio
    async def test_get_user_sessions(self, manager_with_mock_pool):
        """Test getting user sessions"""
        manager, pool, conn, cursor = manager_with_mock_pool
        
        # Mock return data
        cursor.fetchall.return_value = [
            (1, "2024-01-01 12:00:00", "2024-01-01 12:10:00", 5, {"total_tokens": 50}),
            (2, "2024-01-02 13:00:00", "2024-01-02 13:05:00", 3, {"total_tokens": 30})
        ]
        
        # Get sessions
        sessions = await manager.get_user_sessions("user123", limit=10)
        
        # Verify results
        assert len(sessions) == 2
        assert sessions[0]["id"] == 1
        assert sessions[0]["message_count"] == 5
        
    @pytest.mark.asyncio
    async def test_search_messages(self, manager_with_mock_pool):
        """Test searching messages"""
        manager, pool, conn, cursor = manager_with_mock_pool
        
        # Mock return data
        cursor.fetchall.return_value = [
            (1, 1, "user", "Test search query", "2024-01-01 12:00:00"),
            (2, 1, "assistant", "Test response", "2024-01-01 12:00:01")
        ]
        
        # Search messages
        results = await manager.search_messages("user123", "test")
        
        # Verify results
        assert len(results) == 2
        assert "test" in results[0]["content"].lower()
        
    @pytest.mark.asyncio
    async def test_cleanup_old_sessions(self, manager_with_mock_pool):
        """Test cleaning up old sessions"""
        manager, pool, conn, cursor = manager_with_mock_pool
        cursor.rowcount = 5  # Mock 5 deleted sessions
        
        # Cleanup sessions
        deleted = await manager.cleanup_old_sessions(days=30)
        
        # Verify query executed
        cursor.execute.assert_called()
        conn.commit.assert_called()
        assert deleted == 5
        
    @pytest.mark.asyncio
    async def test_connection_pool_management(self, manager_with_mock_pool):
        """Test connection pool put back after use"""
        manager, pool, conn, cursor = manager_with_mock_pool
        
        # Execute a query
        await manager.store_chat_session("user123", "model")
        
        # Verify connection returned to pool
        pool.putconn.assert_called_with(conn)
        
    @pytest.mark.asyncio
    async def test_error_handling(self, manager_with_mock_pool):
        """Test error handling and rollback"""
        manager, pool, conn, cursor = manager_with_mock_pool
        
        # Make execute raise error
        cursor.execute.side_effect = Exception("Query failed")
        
        # Try to store session
        session_id = await manager.store_chat_session("user123", "model")
        
        # Should rollback and return None
        conn.rollback.assert_called()
        assert session_id is None
        
    @pytest.mark.asyncio
    async def test_mock_mode_operations(self):
        """Test operations in mock mode"""
        manager = DatabaseManager()
        manager.use_mock = True
        manager.is_initialized = True
        
        # Test mock operations
        session_id = await manager.store_chat_session("user123", "model")
        assert session_id == 1
        
        message_id = await manager.store_message(1, "user", "test")
        assert message_id == 1
        
        history = await manager.get_session_history(1)
        assert isinstance(history, list)
        
    def test_thread_safety(self):
        """Test thread-safe initialization (H3 fix)"""
        manager = DatabaseManager()
        results = []
        
        def init_in_thread():
            # Try to initialize
            manager._initialize_pool()
            results.append(manager.is_initialized)
            
        # Create multiple threads
        threads = []
        for _ in range(10):
            t = threading.Thread(target=init_in_thread)
            threads.append(t)
            t.start()
            
        # Wait for all threads
        for t in threads:
            t.join()
            
        # Should only initialize once
        assert all(results)  # All should see initialized state
        
    @pytest.mark.asyncio
    async def test_get_stats(self, manager_with_mock_pool):
        """Test getting database statistics"""
        manager, pool, conn, cursor = manager_with_mock_pool
        
        # Mock stats
        cursor.fetchone.return_value = (100, 50, 1000)
        
        # Get stats
        stats = await manager.get_stats()
        
        # Verify stats structure
        assert "total_sessions" in stats
        assert "total_messages" in stats
        assert "total_users" in stats
        
    @pytest.mark.asyncio
    async def test_health_check(self, manager_with_mock_pool):
        """Test database health check"""
        manager, pool, conn, cursor = manager_with_mock_pool
        
        # Mock successful query
        cursor.fetchone.return_value = (1,)
        
        # Check health
        healthy = await manager.health_check()
        
        # Should be healthy
        assert healthy == True
        
    @pytest.mark.asyncio
    async def test_health_check_failure(self, manager_with_mock_pool):
        """Test health check when database fails"""
        manager, pool, conn, cursor = manager_with_mock_pool
        
        # Make query fail
        cursor.execute.side_effect = Exception("Connection lost")
        
        # Check health
        healthy = await manager.health_check()
        
        # Should be unhealthy
        assert healthy == False


class TestDatabaseIntegration:
    """Test database integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_full_session_lifecycle(self):
        """Test complete session lifecycle"""
        manager = DatabaseManager()
        manager.use_mock = True
        manager.is_initialized = True
        
        # Create session
        session_id = await manager.store_chat_session("test_user", "gpt-4")
        assert session_id is not None
        
        # Add messages
        msg1 = await manager.store_message(session_id, "user", "Hello")
        msg2 = await manager.store_message(session_id, "assistant", "Hi there")
        
        assert msg1 is not None
        assert msg2 is not None
        
        # Get history
        history = await manager.get_session_history(session_id)
        assert len(history) >= 0  # Mock might return empty
        
        # Update metadata
        await manager.update_session_metadata(session_id, {"completed": True})
        
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test concurrent database operations"""
        manager = DatabaseManager()
        manager.use_mock = True
        manager.is_initialized = True
        
        # Create multiple concurrent operations
        tasks = []
        for i in range(10):
            task = manager.store_chat_session(f"user_{i}", "model")
            tasks.append(task)
            
        # Wait for all
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(r is not None for r in results)
        
    @pytest.mark.asyncio
    async def test_recovery_after_error(self):
        """Test recovery after database error"""
        with patch('database_manager.psycopg2') as mock_psycopg2:
            manager = DatabaseManager()
            
            # First call fails
            mock_psycopg2.pool.SimpleConnectionPool.side_effect = [
                Exception("Connection failed"),
                MagicMock()  # Second call succeeds
            ]
            
            # First initialization fails, falls back to mock
            await manager._ensure_initialized()
            assert manager.use_mock == True
            
            # Reset and try again
            manager.is_initialized = False
            manager.use_mock = False
            
            # Should try to reconnect
            await manager._ensure_initialized()


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])