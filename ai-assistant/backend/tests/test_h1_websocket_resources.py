"""
Test suite for H1: WebSocket Resource Management
Validates connection limits, cleanup, and resource exhaustion prevention
Architecture: Dr. Sarah Chen
"""
import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, MagicMock
from fastapi import WebSocket
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from websocket_resource_manager import (
    WebSocketResourceManager,
    WebSocketConnection,
    WebSocketMetrics
)


class TestWebSocketResourceManagement:
    """Test H1: WebSocket resource management and limits"""
    
    @pytest.fixture
    async def manager(self):
        """Create resource manager instance"""
        manager = WebSocketResourceManager(
            max_connections=10,
            max_connections_per_user=3,
            connection_timeout=5,
            cleanup_interval=2
        )
        await manager.start_background_tasks()
        yield manager
        await manager.stop_background_tasks()
    
    @pytest.fixture
    def mock_websocket(self):
        """Create mock WebSocket"""
        ws = MagicMock(spec=WebSocket)
        ws.send_json = AsyncMock()
        ws.close = AsyncMock()
        return ws
    
    @pytest.mark.asyncio
    async def test_connection_limit_enforcement(self, manager, mock_websocket):
        """Test that connection limits are enforced"""
        connections = []
        
        # Fill up to max connections
        for i in range(10):
            async with manager.managed_connection(mock_websocket, f"user_{i}") as conn:
                connections.append(conn)
                assert conn is not None
        
        # Try to exceed limit
        can_accept, reason = manager.can_accept_connection("user_11")
        assert not can_accept
        assert "Maximum connections reached" in reason
    
    @pytest.mark.asyncio
    async def test_per_user_connection_limit(self, manager, mock_websocket):
        """Test per-user connection limits"""
        user_id = "test_user"
        
        # Create max connections for one user
        for i in range(3):
            async with manager.managed_connection(mock_websocket, user_id) as conn:
                assert conn is not None
        
        # Try to exceed per-user limit
        can_accept, reason = manager.can_accept_connection(user_id)
        assert not can_accept
        assert "User connection limit reached" in reason
    
    @pytest.mark.asyncio
    async def test_connection_cleanup_on_timeout(self, manager, mock_websocket):
        """Test automatic cleanup of stale connections"""
        # Create connection with short timeout
        manager.connection_timeout = 1
        manager.cleanup_interval = 0.5
        
        # Create connection
        connection_id = f"test_user_{int(time.time() * 1000)}"
        connection = WebSocketConnection(
            connection_id=connection_id,
            user_id="test_user",
            websocket=mock_websocket,
            created_at=time.time() - 10,  # Old connection
            last_activity=time.time() - 10  # Stale
        )
        
        manager._connections[connection_id] = connection
        manager._user_connections["test_user"].add(connection_id)
        
        # Wait for cleanup cycle
        await asyncio.sleep(1)
        
        # Connection should be cleaned up
        assert connection_id not in manager._connections
        assert connection_id not in manager._user_connections.get("test_user", set())
    
    @pytest.mark.asyncio
    async def test_connection_activity_tracking(self, manager, mock_websocket):
        """Test that connection activity is properly tracked"""
        async with manager.managed_connection(mock_websocket, "test_user") as conn:
            connection = manager.get_connection(conn.connection_id)
            initial_activity = connection.last_activity
            
            # Simulate activity
            await asyncio.sleep(0.1)
            connection.update_activity()
            
            assert connection.last_activity > initial_activity
    
    @pytest.mark.asyncio
    async def test_metrics_tracking(self, manager, mock_websocket):
        """Test that metrics are properly tracked"""
        initial_metrics = manager._metrics.get_metrics()
        
        # Create and close connections
        async with manager.managed_connection(mock_websocket, "user1") as conn1:
            pass
        
        async with manager.managed_connection(mock_websocket, "user2") as conn2:
            pass
        
        final_metrics = manager._metrics.get_metrics()
        
        assert final_metrics['total_connections'] > initial_metrics['total_connections']
        assert final_metrics['peak_connections'] >= 1
    
    @pytest.mark.asyncio
    async def test_broadcast_to_user(self, manager, mock_websocket):
        """Test broadcasting to all user connections"""
        user_id = "broadcast_user"
        message = {"type": "test", "data": "broadcast"}
        
        # Create multiple connections for user
        connections = []
        for i in range(2):
            ws = MagicMock(spec=WebSocket)
            ws.send_json = AsyncMock()
            async with manager.managed_connection(ws, user_id) as conn:
                connections.append(conn)
        
        # Broadcast to user
        await manager.broadcast_to_user(user_id, message)
        
        # Verify all connections received message
        for conn in connections:
            connection = manager.get_connection(conn.connection_id)
            if connection:
                connection.websocket.send_json.assert_called()
    
    @pytest.mark.asyncio
    async def test_memory_estimation(self, manager, mock_websocket):
        """Test memory usage estimation"""
        initial_estimate = manager._estimate_memory_usage()
        
        # Add connections
        async with manager.managed_connection(mock_websocket, "user1") as conn1:
            with_one = manager._estimate_memory_usage()
            
            async with manager.managed_connection(mock_websocket, "user2") as conn2:
                with_two = manager._estimate_memory_usage()
        
        assert with_two > with_one > initial_estimate
    
    @pytest.mark.asyncio
    async def test_heartbeat_dead_connection_cleanup(self, manager):
        """Test that dead connections are detected and cleaned up"""
        # Create connection with failing websocket
        ws = MagicMock(spec=WebSocket)
        ws.send_json = AsyncMock(side_effect=Exception("Connection dead"))
        ws.close = AsyncMock()
        
        connection_id = "dead_conn"
        connection = WebSocketConnection(
            connection_id=connection_id,
            user_id="test_user",
            websocket=ws,
            created_at=time.time(),
            last_activity=time.time()
        )
        
        manager._connections[connection_id] = connection
        manager._user_connections["test_user"].add(connection_id)
        
        # Trigger heartbeat
        manager.heartbeat_interval = 0.1
        await asyncio.sleep(0.3)
        
        # Dead connection should be cleaned up
        assert connection_id not in manager._connections
    
    @pytest.mark.asyncio
    async def test_status_reporting(self, manager, mock_websocket):
        """Test status reporting functionality"""
        # Create some connections
        async with manager.managed_connection(mock_websocket, "user1") as conn1:
            async with manager.managed_connection(mock_websocket, "user2") as conn2:
                status = manager.get_status()
                
                assert status['active_connections'] == 2
                assert status['unique_users'] == 2
                assert 0 < status['usage_percent'] <= 100
                assert 'metrics' in status
                assert 'limits' in status


class TestWebSocketMetrics:
    """Test WebSocket metrics tracking"""
    
    def test_connection_metrics(self):
        """Test connection tracking metrics"""
        metrics = WebSocketMetrics()
        
        # Record connections
        metrics.record_connection_established("user1")
        metrics.record_connection_established("user2")
        metrics.record_connection_closed("user1")
        
        assert metrics.total_connections == 2
        assert metrics.active_connections == 1
        assert metrics.peak_connections == 2
    
    def test_error_tracking(self):
        """Test error tracking"""
        metrics = WebSocketMetrics()
        
        # Record errors
        metrics.record_connection_error("user1", "timeout")
        metrics.record_connection_error("user2", "timeout")
        metrics.record_connection_error("user3", "refused")
        
        assert metrics.failed_connections == 3
        assert metrics.connection_errors["timeout"] == 2
        assert metrics.connection_errors["refused"] == 1
    
    def test_cleanup_metrics(self):
        """Test cleanup cycle metrics"""
        metrics = WebSocketMetrics()
        
        # Record cleanup cycles
        metrics.record_cleanup_cycle(5)
        metrics.record_cleanup_cycle(3)
        
        assert metrics.cleanup_cycles == 2
        assert metrics.connections_cleaned == 8
    
    def test_data_transfer_metrics(self):
        """Test data transfer tracking"""
        metrics = WebSocketMetrics()
        
        # Record data transfers
        metrics.record_data_transfer(1024, 512)
        metrics.record_data_transfer(2048, 1024)
        
        assert metrics.bytes_sent_total == 3072
        assert metrics.bytes_received_total == 1536


if __name__ == "__main__":
    pytest.main([__file__, "-v"])