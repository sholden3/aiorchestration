"""
WebSocket Manager Unit Tests
============================

@author Sam Martinez v3.2.0 - Testing Lead & Quality Assurance
@architecture Test coverage for WebSocket real-time communication system
@business_logic Validates connection limits, broadcasting, and resource management

File Type: Test Implementation
Documentation Standard: v2.0 (CLAUDE.md § Standards)
Orchestrated Implementation: Phase 2 Test Coverage

Core Architects:
- Alex Novak v3.0: Frontend Integration & Real-time Communication
- Dr. Sarah Chen v1.2: Backend Systems & Resource Management
- Sam Martinez v3.2.0: Testing Lead & Quality Assurance

Business Context:
- Real-time WebSocket broadcasting for live updates
- Connection management with resource limits
- User-specific message routing
- Metrics tracking and performance monitoring

Architecture Pattern:
- Connection pooling with per-user limits
- Message broadcasting with backpressure handling
- Automatic cleanup of dead connections
- Resource tracking and metrics collection

Test Strategy (Sam Martinez):
- Unit tests for connection management
- Broadcasting behavior validation
- Resource limit enforcement
- Metrics tracking verification
- Error handling and recovery

Performance Requirements:
- <100ms message broadcast latency
- Support for 100+ concurrent connections
- Memory usage <10KB per connection
- Automatic cleanup within 60s of disconnect

Dependencies:
- pytest: Test framework
- pytest-asyncio: Async test support
- unittest.mock: Mocking WebSocket connections
- asyncio: Async testing utilities
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from websocket_manager import WebSocketResourceManager, ConnectionMetrics, WebSocketManager
from fastapi import WebSocket


class MockWebSocket:
    """Mock WebSocket for testing"""
    
    def __init__(self, client_id=None):
        self.state = "connected"
        self.messages_sent = []
        self.closed = False
        self.accept = AsyncMock()
        self.send_text = AsyncMock(side_effect=self._record_message)
        self.send_json = AsyncMock(side_effect=self._record_json)
        self.receive_text = AsyncMock(return_value='{"type": "ping"}')
        self.close = AsyncMock(side_effect=self._close)
        self.client = {"host": "127.0.0.1", "port": 12345}
        self.client_id = client_id or f"client_{id(self)}"
        
    def _record_message(self, message):
        self.messages_sent.append(message)
        
    def _record_json(self, data):
        self.messages_sent.append(json.dumps(data))
        
    def _close(self):
        self.closed = True
        self.state = "disconnected"
        

class TestConnectionMetrics:
    """Test ConnectionMetrics class functionality"""
    
    def test_metrics_initialization(self):
        """Test ConnectionMetrics initialization"""
        now = datetime.now()
        metrics = ConnectionMetrics(
            client_id="test_client",
            connected_at=now,
            last_activity=now
        )
        
        assert metrics.client_id == "test_client"
        assert metrics.connected_at == now
        assert metrics.last_activity == now
        assert metrics.messages_sent == 0
        assert metrics.messages_received == 0
        assert metrics.memory_usage_mb == 0.0
        assert metrics.is_alive == True
        assert len(metrics.subscriptions) == 0
        assert metrics.idle_warnings_sent == 0
        
    def test_metrics_update(self):
        """Test updating metrics"""
        now = datetime.now()
        metrics = ConnectionMetrics(
            client_id="test_client",
            connected_at=now,
            last_activity=now
        )
        
        # Update message counts
        metrics.messages_sent += 1
        metrics.messages_received += 2
        metrics.memory_usage_mb = 1.5
        metrics.idle_warnings_sent += 1
        
        assert metrics.messages_sent == 1
        assert metrics.messages_received == 2
        assert metrics.memory_usage_mb == 1.5
        assert metrics.idle_warnings_sent == 1


class TestWebSocketResourceManager:
    """Test WebSocketResourceManager functionality"""
    
    @pytest.fixture
    def manager(self):
        """Create WebSocketResourceManager instance"""
        with patch('websocket_manager.config') as mock_config:
            # Mock config values
            mock_config.systems.websocket_max_connections = 10
            mock_config.systems.websocket_idle_timeout_seconds = 60
            mock_config.systems.websocket_memory_limit_per_connection_mb = 10
            mock_config.systems.websocket_backpressure_threshold = 0.8
            mock_config.systems.websocket_cleanup_interval_seconds = 30
            mock_config.systems.websocket_heartbeat_interval_seconds = 30
            mock_config.systems.websocket_max_connections_per_user = 3
            
            manager = WebSocketResourceManager()
            return manager
    
    def test_manager_initialization(self, manager):
        """Test manager initialization with proper defaults"""
        assert manager.max_connections == 10
        assert manager.idle_timeout == 60
        assert manager.memory_limit_per_connection == 10
        assert manager.backpressure_threshold == 0.8
        assert len(manager.connections) == 0
        assert manager.connection_count == 0
        
    @pytest.mark.asyncio
    async def test_accept_connection(self, manager):
        """Test accepting a new connection"""
        mock_ws = MockWebSocket()
        
        # Accept connection
        success = await manager.accept_connection(mock_ws, "user1")
        
        assert success == True
        assert mock_ws in manager.connections
        assert manager.connections[mock_ws].user_id == "user1"
        assert manager.connection_count == 1
        
    @pytest.mark.asyncio
    async def test_reject_connection_at_limit(self, manager):
        """Test rejecting connections when at limit"""
        # Fill up to max connections
        for i in range(10):
            mock_ws = MockWebSocket(client_id=f"client_{i}")
            success = await manager.accept_connection(mock_ws, f"user_{i}")
            assert success == True
            
        # Try to add one more
        mock_ws = MockWebSocket()
        success = await manager.accept_connection(mock_ws, "user_overflow")
        
        assert success == False
        assert manager.connections_rejected == 1
        assert manager.connection_count == 10
        
    @pytest.mark.asyncio
    async def test_remove_connection(self, manager):
        """Test removing a connection"""
        mock_ws = MockWebSocket()
        
        # Add connection
        await manager.accept_connection(mock_ws, "user1")
        assert manager.connection_count == 1
        
        # Remove connection
        await manager.remove_connection(mock_ws)
        
        assert mock_ws not in manager.connections
        assert manager.connection_count == 0
        
    @pytest.mark.asyncio
    async def test_check_idle_connections(self, manager):
        """Test checking and removing idle connections"""
        mock_ws = MockWebSocket()
        
        # Add connection
        await manager.accept_connection(mock_ws, "user1")
        
        # Make it idle by setting last_activity to old time
        manager.connections[mock_ws].last_activity = time.time() - 120  # 2 minutes ago
        
        # Check idle connections
        removed = await manager.check_idle_connections()
        
        assert removed == 1
        assert mock_ws not in manager.connections
        assert manager.idle_timeouts == 1
        
    @pytest.mark.asyncio
    async def test_estimate_memory_usage(self, manager):
        """Test memory usage estimation"""
        mock_ws = MockWebSocket()
        
        # Add connection
        await manager.accept_connection(mock_ws, "user1")
        
        # Estimate memory
        memory_mb = manager.estimate_memory_usage()
        
        # Should have some memory usage
        assert memory_mb >= 0
        
    @pytest.mark.asyncio
    async def test_get_connection_stats(self, manager):
        """Test getting connection statistics"""
        # Add some connections
        for i in range(3):
            mock_ws = MockWebSocket(client_id=f"client_{i}")
            await manager.accept_connection(mock_ws, f"user_{i}")
            
        # Get stats
        stats = manager.get_connection_stats()
        
        assert stats["active_connections"] == 3
        assert stats["total_connections_ever"] == 3
        assert stats["connections_rejected"] == 0
        assert stats["idle_timeouts"] == 0
        assert "memory_usage_mb" in stats
        assert "uptime_seconds" in stats
        
    @pytest.mark.asyncio
    async def test_broadcast_message(self, manager):
        """Test broadcasting message to all connections"""
        # Add connections
        mock_connections = []
        for i in range(3):
            mock_ws = MockWebSocket(client_id=f"client_{i}")
            mock_connections.append(mock_ws)
            await manager.accept_connection(mock_ws, f"user_{i}")
            
        # Broadcast message
        message = {"type": "update", "data": "test"}
        success_count = await manager.broadcast(json.dumps(message))
        
        # Verify all connections received message
        assert success_count == 3
        for mock_ws in mock_connections:
            assert len(mock_ws.messages_sent) == 1
            
    @pytest.mark.asyncio
    async def test_send_to_user(self, manager):
        """Test sending message to specific user"""
        # Add connections for same user
        user_connections = []
        for i in range(2):
            mock_ws = MockWebSocket(client_id=f"user1_conn_{i}")
            user_connections.append(mock_ws)
            await manager.accept_connection(mock_ws, "user1")
            
        # Add connection for different user
        other_ws = MockWebSocket(client_id="user2_conn")
        await manager.accept_connection(other_ws, "user2")
        
        # Send to user1
        message = {"type": "user_update"}
        success_count = await manager.send_to_user("user1", json.dumps(message))
        
        # Verify only user1 connections received message
        assert success_count == 2
        for mock_ws in user_connections:
            assert len(mock_ws.messages_sent) == 1
        assert len(other_ws.messages_sent) == 0
        
    @pytest.mark.asyncio
    async def test_connection_error_handling(self, manager):
        """Test error handling during message send"""
        mock_ws = MockWebSocket()
        mock_ws.send_text = AsyncMock(side_effect=Exception("Send failed"))
        
        # Add connection
        await manager.accept_connection(mock_ws, "user1")
        
        # Try to broadcast (should handle error gracefully)
        success_count = await manager.broadcast("test message")
        
        # Should have recorded error
        assert success_count == 0
        assert manager.connections[mock_ws].errors == 1
        assert manager.connections[mock_ws].last_error is not None


class TestWebSocketManager:
    """Test WebSocketManager functionality"""
    
    @pytest.fixture
    def ws_manager(self):
        """Create WebSocketManager instance"""
        with patch('websocket_manager.config') as mock_config:
            # Mock config values
            mock_config.systems.websocket_max_connections = 100
            mock_config.systems.websocket_idle_timeout_seconds = 60
            mock_config.systems.websocket_memory_limit_per_connection_mb = 10
            mock_config.systems.websocket_backpressure_threshold = 0.8
            mock_config.systems.websocket_cleanup_interval_seconds = 30
            mock_config.systems.websocket_heartbeat_interval_seconds = 30
            mock_config.systems.websocket_max_connections_per_user = 5
            
            manager = WebSocketManager()
            return manager
    
    def test_manager_singleton(self):
        """Test WebSocketManager is singleton"""
        with patch('websocket_manager.config') as mock_config:
            # Mock config values
            mock_config.systems.websocket_max_connections = 100
            
            manager1 = WebSocketManager()
            manager2 = WebSocketManager()
            
            # Should be same instance
            assert manager1 is manager2
            
    @pytest.mark.asyncio
    async def test_connect_websocket(self, ws_manager):
        """Test connecting a WebSocket through manager"""
        mock_ws = MockWebSocket()
        
        # Connect
        await ws_manager.connect(mock_ws)
        
        # Verify connection added
        assert mock_ws in ws_manager.connections
        assert ws_manager.resource_manager.connection_count == 1
        
    @pytest.mark.asyncio
    async def test_disconnect_websocket(self, ws_manager):
        """Test disconnecting a WebSocket"""
        mock_ws = MockWebSocket()
        
        # Connect and disconnect
        await ws_manager.connect(mock_ws)
        await ws_manager.disconnect(mock_ws)
        
        # Verify connection removed
        assert mock_ws not in ws_manager.connections
        assert ws_manager.resource_manager.connection_count == 0
        
    @pytest.mark.asyncio
    async def test_handle_message(self, ws_manager):
        """Test handling incoming WebSocket message"""
        mock_ws = MockWebSocket()
        
        # Connect
        await ws_manager.connect(mock_ws)
        
        # Handle message
        message = json.dumps({"type": "test", "data": "hello"})
        await ws_manager.handle_message(mock_ws, message)
        
        # Should update metrics
        metrics = ws_manager.resource_manager.connections[mock_ws]
        assert metrics.messages_received == 1
        assert metrics.data_received_bytes > 0
        
    @pytest.mark.asyncio
    async def test_broadcast_to_all(self, ws_manager):
        """Test broadcasting to all connections"""
        # Connect multiple WebSockets
        mock_connections = []
        for i in range(3):
            mock_ws = MockWebSocket(client_id=f"client_{i}")
            mock_connections.append(mock_ws)
            await ws_manager.connect(mock_ws)
            
        # Broadcast message
        await ws_manager.broadcast({"type": "announcement", "message": "test"})
        
        # Verify all received
        for mock_ws in mock_connections:
            assert len(mock_ws.messages_sent) == 1
            
    @pytest.mark.asyncio
    async def test_get_status(self, ws_manager):
        """Test getting WebSocket manager status"""
        # Connect some WebSockets
        for i in range(5):
            mock_ws = MockWebSocket(client_id=f"client_{i}")
            await ws_manager.connect(mock_ws)
            
        # Get status
        status = ws_manager.get_status()
        
        assert status["active_connections"] == 5
        assert status["resource_manager"]["active_connections"] == 5
        assert "memory_usage_mb" in status["resource_manager"]


class TestWebSocketIntegration:
    """Test WebSocket integration scenarios"""
    
    @pytest.fixture
    def manager(self):
        """Create WebSocketResourceManager instance"""
        with patch('websocket_manager.config') as mock_config:
            # Mock config values
            mock_config.systems.websocket_max_connections = 100
            mock_config.systems.websocket_idle_timeout_seconds = 60
            mock_config.systems.websocket_memory_limit_per_connection_mb = 10
            mock_config.systems.websocket_backpressure_threshold = 0.8
            mock_config.systems.websocket_cleanup_interval_seconds = 30
            mock_config.systems.websocket_heartbeat_interval_seconds = 30
            mock_config.systems.websocket_max_connections_per_user = 5
            
            return WebSocketResourceManager()
    
    @pytest.mark.asyncio
    async def test_connection_lifecycle(self, manager):
        """Test complete connection lifecycle"""
        mock_ws = MockWebSocket()
        
        # Connect
        success = await manager.accept_connection(mock_ws, "test_user")
        assert success == True
        
        # Send messages
        await manager.broadcast("test message")
        assert len(mock_ws.messages_sent) == 1
        
        # Disconnect
        await manager.remove_connection(mock_ws)
        
        # Verify cleanup
        assert mock_ws not in manager.connections
        
    @pytest.mark.asyncio
    async def test_concurrent_connections(self, manager):
        """Test handling concurrent connections"""
        # Create tasks for concurrent connections
        tasks = []
        mock_connections = []
        for i in range(10):
            mock_ws = MockWebSocket(client_id=f"client_{i}")
            mock_connections.append(mock_ws)
            task = asyncio.create_task(
                manager.accept_connection(mock_ws, f"user_{i}")
            )
            tasks.append(task)
            
        # Wait for all connections
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(results)
        assert manager.connection_count == 10
        
    @pytest.mark.asyncio
    async def test_performance_under_load(self, manager):
        """Test performance with many connections"""
        # Connect many WebSockets
        for i in range(50):
            mock_ws = MockWebSocket(client_id=f"client_{i}")
            await manager.accept_connection(mock_ws, f"user_{i}")
            
        # Measure broadcast time
        start_time = time.time()
        await manager.broadcast("performance test message")
        elapsed = time.time() - start_time
        
        # Should complete quickly
        assert elapsed < 0.1  # Less than 100ms
        
        # Verify all connections are healthy
        assert manager.connection_count == 50


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])