"""
File: ai-assistant/backend/tests/governance/test_session_manager.py
Purpose: Unit tests for session management with singleton pattern
Architecture: Test suite validating session lifecycle and timeout handling
Dependencies: pytest, asyncio, unittest.mock, freezegun
Owner: Maya Patel

@fileoverview Comprehensive unit tests for session management
@author Maya Patel v1.0 - QA & Testing Lead
@architecture Testing - Unit test suite for session manager
@business_logic Validates session creation, timeout, cleanup, singleton pattern
@testing_strategy Lifecycle testing, concurrency validation, memory management
@coverage_target 100% for SessionManager class
"""

import pytest
import asyncio
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import time

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from governance.core.session_manager import (
    Session,
    SessionManager
)


class TestSession:
    """
    Test suite for Session dataclass.
    
    Validates session properties and behavior.
    """
    
    def test_session_creation(self):
        """Test session creation with defaults."""
        session = Session(id="test_session")
        
        assert session.id == "test_session"
        assert session.user_id is None
        assert session.is_active == True
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.last_accessed, datetime)
        assert session.metadata == {}
    
    def test_session_with_user(self):
        """Test session creation with user ID."""
        session = Session(
            id="test_session",
            user_id="user123",
            metadata={"ip": "192.168.1.1"}
        )
        
        assert session.user_id == "user123"
        assert session.metadata["ip"] == "192.168.1.1"
    
    def test_session_touch(self):
        """Test updating last accessed time."""
        session = Session(id="test_session")
        original_time = session.last_accessed
        
        # Small delay to ensure time difference
        time.sleep(0.01)
        session.touch()
        
        assert session.last_accessed > original_time
    
    def test_session_expiry_check(self):
        """Test session expiry validation."""
        session = Session(id="test_session")
        
        # Not expired with large timeout
        assert not session.is_expired(3600)
        
        # Manually set old last_accessed time
        session.last_accessed = datetime.utcnow() - timedelta(hours=2)
        
        # Should be expired with 1 hour timeout
        assert session.is_expired(3600)
        
        # Not expired with 3 hour timeout
        assert not session.is_expired(10800)
    
    def test_inactive_session_expiry(self):
        """Test inactive sessions are always expired."""
        session = Session(id="test_session")
        session.is_active = False
        
        # Inactive sessions are always expired
        assert session.is_expired(999999)


class TestSessionManager:
    """
    Test suite for SessionManager singleton functionality.
    
    Tests session management, cleanup, and singleton pattern.
    """
    
    @pytest.fixture
    def manager(self):
        """Create a session manager instance."""
        # Reset singleton for testing
        SessionManager._instance = None
        config = {
            'session_timeout': 60,
            'max_sessions': 100
        }
        return SessionManager(config)
    
    def test_singleton_pattern(self):
        """Test SessionManager follows singleton pattern."""
        # Reset singleton
        SessionManager._instance = None
        
        manager1 = SessionManager()
        manager2 = SessionManager()
        
        assert manager1 is manager2
        
        # Even with different config, should return same instance
        manager3 = SessionManager({'session_timeout': 120})
        assert manager1 is manager3
    
    @pytest.mark.asyncio
    async def test_create_session(self, manager):
        """Test session creation."""
        session = await manager.create_session(
            user_id="user123",
            metadata={"source": "web"}
        )
        
        assert session is not None
        assert session.id.startswith("sess_")
        assert session.user_id == "user123"
        assert session.metadata["source"] == "web"
        assert session.is_active == True
        
        # Session should be stored
        assert session.id in manager.sessions
    
    @pytest.mark.asyncio
    async def test_create_session_without_user(self, manager):
        """Test anonymous session creation."""
        session = await manager.create_session()
        
        assert session is not None
        assert session.user_id is None
        assert session.id.startswith("sess_")
    
    @pytest.mark.asyncio
    async def test_session_limit(self, manager):
        """Test maximum session limit enforcement."""
        manager.max_sessions = 5
        
        # Create maximum sessions
        sessions = []
        for i in range(5):
            session = await manager.create_session(user_id=f"user_{i}")
            sessions.append(session)
        
        assert len(manager.sessions) == 5
        
        # Next session should raise error
        with pytest.raises(Exception, match="Maximum session limit.*reached"):
            await manager.create_session(user_id="overflow")
    
    @pytest.mark.asyncio
    async def test_get_session(self, manager):
        """Test retrieving sessions."""
        session = await manager.create_session(user_id="user123")
        
        # Retrieve existing session
        retrieved = await manager.get_session(session.id)
        assert retrieved is not None
        assert retrieved.id == session.id
        assert retrieved.user_id == "user123"
        
        # Non-existent session
        none_session = await manager.get_session("nonexistent")
        assert none_session is None
    
    @pytest.mark.asyncio
    async def test_get_session_updates_access_time(self, manager):
        """Test that getting a session updates last accessed time."""
        session = await manager.create_session()
        original_time = session.last_accessed
        
        # Small delay
        time.sleep(0.01)
        
        retrieved = await manager.get_session(session.id)
        assert retrieved.last_accessed > original_time
    
    @pytest.mark.asyncio
    async def test_get_expired_session(self, manager):
        """Test that expired sessions are not returned."""
        manager.timeout_seconds = 1  # 1 second timeout
        
        session = await manager.create_session()
        
        # Manually expire the session
        session.last_accessed = datetime.utcnow() - timedelta(seconds=2)
        
        retrieved = await manager.get_session(session.id)
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_validate_session(self, manager):
        """Test session validation."""
        session = await manager.create_session()
        
        # Valid session
        is_valid = await manager.validate_session(session.id)
        assert is_valid == True
        
        # Non-existent session
        is_valid = await manager.validate_session("nonexistent")
        assert is_valid == False
        
        # Inactive session
        session.is_active = False
        is_valid = await manager.validate_session(session.id)
        assert is_valid == False
    
    @pytest.mark.asyncio
    async def test_destroy_session(self, manager):
        """Test session destruction."""
        session = await manager.create_session(user_id="user123")
        session_id = session.id
        
        # Destroy session
        destroyed = await manager.destroy_session(session_id)
        assert destroyed == True
        assert session_id not in manager.sessions
        assert session.is_active == False
        
        # Try to destroy again
        destroyed_again = await manager.destroy_session(session_id)
        assert destroyed_again == False
    
    @pytest.mark.asyncio
    async def test_update_session_metadata(self, manager):
        """Test updating session metadata."""
        session = await manager.create_session(
            metadata={"initial": "value"}
        )
        
        # Update metadata
        updated = await manager.update_session_metadata(
            session.id,
            {"new": "data", "count": 5}
        )
        assert updated == True
        
        # Check metadata was merged
        retrieved = await manager.get_session(session.id)
        assert retrieved.metadata["initial"] == "value"
        assert retrieved.metadata["new"] == "data"
        assert retrieved.metadata["count"] == 5
        
        # Update non-existent session
        updated = await manager.update_session_metadata(
            "nonexistent",
            {"data": "value"}
        )
        assert updated == False
    
    def test_get_active_sessions(self, manager):
        """Test retrieving active sessions."""
        asyncio.run(self._create_mixed_sessions(manager))
        
        active = manager.get_active_sessions()
        
        # Should only return non-expired, active sessions
        assert len(active) == 2
        assert all(s.is_active for s in active)
        assert all(not s.is_expired(manager.timeout_seconds) for s in active)
    
    async def _create_mixed_sessions(self, manager):
        """Helper to create mix of active/inactive/expired sessions."""
        # Active sessions
        active1 = await manager.create_session(user_id="active1")
        active2 = await manager.create_session(user_id="active2")
        
        # Inactive session
        inactive = await manager.create_session(user_id="inactive")
        inactive.is_active = False
        
        # Expired session
        expired = await manager.create_session(user_id="expired")
        expired.last_accessed = datetime.utcnow() - timedelta(hours=2)
    
    def test_get_statistics(self, manager):
        """Test session statistics generation."""
        asyncio.run(self._create_mixed_sessions(manager))
        
        stats = manager.get_statistics()
        
        assert stats['total_sessions'] == 4
        assert stats['active_sessions'] == 2
        assert stats['expired_sessions'] == 2
        assert stats['oldest_session'] is not None
        assert stats['newest_session'] is not None
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self, manager):
        """Test automatic cleanup of expired sessions."""
        manager.timeout_seconds = 1
        
        # Create sessions
        session1 = await manager.create_session(user_id="user1")
        session2 = await manager.create_session(user_id="user2")
        
        # Expire one session
        session1.last_accessed = datetime.utcnow() - timedelta(seconds=2)
        
        # Run cleanup
        await manager._cleanup_expired_sessions()
        
        # Only non-expired session should remain
        assert len(manager.sessions) == 1
        assert session2.id in manager.sessions
        assert session1.id not in manager.sessions


class TestSessionManagerConcurrency:
    """
    Test suite for SessionManager concurrency handling.
    
    Tests thread safety and concurrent operations.
    """
    
    @pytest.fixture
    def manager(self):
        """Create a session manager for concurrency tests."""
        SessionManager._instance = None
        return SessionManager({'max_sessions': 1000})
    
    @pytest.mark.asyncio
    async def test_concurrent_session_creation(self, manager):
        """Test concurrent session creation."""
        async def create_session(user_id):
            return await manager.create_session(user_id=user_id)
        
        # Create many sessions concurrently
        tasks = [
            create_session(f"user_{i}")
            for i in range(100)
        ]
        
        sessions = await asyncio.gather(*tasks)
        
        # All sessions should be created successfully
        assert len(sessions) == 100
        assert len(set(s.id for s in sessions)) == 100  # All unique
        assert len(manager.sessions) == 100
    
    @pytest.mark.asyncio
    async def test_concurrent_session_operations(self, manager):
        """Test concurrent mixed operations."""
        # Create some initial sessions
        session_ids = []
        for i in range(10):
            session = await manager.create_session(user_id=f"user_{i}")
            session_ids.append(session.id)
        
        async def random_operation():
            import random
            op = random.choice(['get', 'validate', 'update', 'destroy'])
            session_id = random.choice(session_ids)
            
            if op == 'get':
                return await manager.get_session(session_id)
            elif op == 'validate':
                return await manager.validate_session(session_id)
            elif op == 'update':
                return await manager.update_session_metadata(
                    session_id,
                    {"timestamp": datetime.utcnow().isoformat()}
                )
            else:  # destroy
                return await manager.destroy_session(session_id)
        
        # Run many concurrent operations
        tasks = [random_operation() for _ in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Should complete without deadlocks or errors
        assert len(results) == 100
        
        # Some sessions might be destroyed
        assert len(manager.sessions) <= 10


class TestSessionManagerIntegration:
    """
    Integration tests for SessionManager with real scenarios.
    
    Tests realistic usage patterns and edge cases.
    """
    
    @pytest.mark.asyncio
    async def test_session_lifecycle(self):
        """Test complete session lifecycle."""
        SessionManager._instance = None
        manager = SessionManager({
            'session_timeout': 2,  # 2 seconds
            'max_sessions': 10
        })
        
        # Create session
        session = await manager.create_session(
            user_id="testuser",
            metadata={"login_time": datetime.utcnow().isoformat()}
        )
        
        # Validate session
        assert await manager.validate_session(session.id) == True
        
        # Update metadata
        await manager.update_session_metadata(
            session.id,
            {"last_action": "viewed_dashboard"}
        )
        
        # Keep session alive
        await asyncio.sleep(1)
        await manager.get_session(session.id)  # Touch session
        
        # Wait for near expiry
        await asyncio.sleep(1.5)
        
        # Session should still be valid (touched recently)
        assert await manager.validate_session(session.id) == True
        
        # Wait for expiry
        await asyncio.sleep(2.5)
        
        # Session should be expired
        assert await manager.validate_session(session.id) == False
        
        # Cleanup should remove it
        await manager._cleanup_expired_sessions()
        assert session.id not in manager.sessions
    
    @pytest.mark.asyncio
    async def test_session_manager_with_background_cleanup(self):
        """Test session manager with background cleanup task."""
        SessionManager._instance = None
        manager = SessionManager({
            'session_timeout': 1,
            'max_sessions': 10
        })
        
        # Mock the cleanup task
        with patch.object(manager, '_cleanup_expired_sessions') as mock_cleanup:
            mock_cleanup.return_value = asyncio.Future()
            mock_cleanup.return_value.set_result(None)
            
            # Start cleanup task
            manager._start_cleanup_task()
            
            # Create sessions
            await manager.create_session(user_id="user1")
            await manager.create_session(user_id="user2")
            
            # Cleanup task should be created
            assert manager._cleanup_task is not None
    
    @pytest.mark.asyncio
    async def test_session_security_patterns(self):
        """Test security-related session patterns."""
        SessionManager._instance = None
        manager = SessionManager()
        
        # Create session with security metadata
        session = await manager.create_session(
            user_id="secure_user",
            metadata={
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0",
                "csrf_token": str(uuid.uuid4())
            }
        )
        
        # Validate CSRF token
        retrieved = await manager.get_session(session.id)
        assert "csrf_token" in retrieved.metadata
        
        # Simulate IP change detection
        new_ip = "10.0.0.1"
        if retrieved.metadata.get("ip_address") != new_ip:
            # Security check - could destroy session on IP change
            await manager.destroy_session(session.id)
        
        # Session should be destroyed
        assert await manager.validate_session(session.id) == False