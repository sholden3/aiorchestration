"""
Unit Tests for WebSocket Resource Manager (H1 Fix)

Tests the WebSocketResourceManager class in isolation to verify:
- Connection limits enforcement
- Resource tracking accuracy
- Idle timeout detection
- Memory usage estimation
- Backpressure logic
- Cleanup mechanisms

Dr. Sarah Chen's Testing Philosophy:
- Test failure modes explicitly
- Verify defensive patterns work
- Ensure circuit breakers activate correctly
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from fastapi import WebSocket

# Mock config for testing
class MockConfig:
    class systems:
        websocket_max_connections = 5
        websocket_idle_timeout_seconds = 10  # Short for testing
        websocket_memory_limit_per_connection_mb = 5
        websocket_backpressure_threshold = 0.8
        websocket_cleanup_interval_seconds = 5  # Short for testing
        websocket_heartbeat_interval_seconds = 3  # Short for testing

# Import the module under test with mocked config
with patch('websocket_manager.config', MockConfig):
    from websocket_manager import WebSocketResourceManager, ConnectionMetrics

class TestWebSocketResourceManager:
    """Test suite for WebSocket resource management"""
    
    @pytest.fixture
    def resource_manager(self):
        """Create a fresh resource manager for each test"""
        return WebSocketResourceManager()
    
    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket for testing"""
        return MagicMock(spec=WebSocket)
    
    def test_initialization(self, resource_manager):
        """Test resource manager initializes correctly"""
        assert resource_manager.max_connections == 5
        assert resource_manager.idle_timeout == 10
        assert resource_manager.connection_count == 0
        assert resource_manager.total_connections_ever == 0
        assert resource_manager.connections_rejected == 0
        assert len(resource_manager.connections) == 0
    
    def test_connection_acceptance_limits(self, resource_manager):
        """Test connection acceptance respects limits"""
        # Initially should accept connections
        can_accept, message = resource_manager.can_accept_connection()
        assert can_accept is True
        assert message == "OK"
        
        # Add connections up to backpressure threshold
        resource_manager.connection_count = 4  # 80% of 5
        can_accept, message = resource_manager.can_accept_connection()
        assert can_accept is True
        assert "Backpressure warning" in message
        
        # At limit should reject
        resource_manager.connection_count = 5
        can_accept, message = resource_manager.can_accept_connection()
        assert can_accept is False
        assert "Connection limit exceeded" in message
    
    def test_connection_registration(self, resource_manager, mock_websocket):
        """Test connection registration and tracking"""
        client_id = "test_client_1"
        
        # Register connection
        metrics = resource_manager.register_connection(mock_websocket, client_id)
        
        assert resource_manager.connection_count == 1
        assert resource_manager.total_connections_ever == 1
        assert mock_websocket in resource_manager.connections
        assert resource_manager.connections[mock_websocket] == metrics
        assert metrics.client_id == client_id
        assert metrics.memory_usage_mb == 2.0  # Default estimation
    
    def test_connection_unregistration(self, resource_manager, mock_websocket):
        """Test connection unregistration and cleanup"""
        # Register first
        metrics = resource_manager.register_connection(mock_websocket, "test_client")
        assert resource_manager.connection_count == 1
        
        # Unregister
        returned_metrics = resource_manager.unregister_connection(mock_websocket)
        
        assert resource_manager.connection_count == 0
        assert mock_websocket not in resource_manager.connections
        assert returned_metrics == metrics
        
        # Unregistering again should return None
        returned_metrics = resource_manager.unregister_connection(mock_websocket)
        assert returned_metrics is None
    
    def test_activity_tracking(self, resource_manager, mock_websocket):
        """Test activity tracking updates"""
        # Register connection
        metrics = resource_manager.register_connection(mock_websocket, "test_client")
        initial_activity = metrics.last_activity
        
        # Small delay to ensure timestamp difference
        time.sleep(0.1)
        
        # Update activity
        resource_manager.update_activity(mock_websocket, "sent")
        
        assert metrics.messages_sent == 1
        assert metrics.messages_received == 0
        assert metrics.last_activity > initial_activity
        
        # Test received message
        resource_manager.update_activity(mock_websocket, "received")
        
        assert metrics.messages_sent == 1
        assert metrics.messages_received == 1
    
    def test_idle_connection_detection(self, resource_manager, mock_websocket):
        """Test idle connection detection"""
        # Register connection
        metrics = resource_manager.register_connection(mock_websocket, "test_client")
        
        # Artificially age the connection
        old_time = datetime.now() - timedelta(seconds=15)  # Older than 10s timeout
        metrics.last_activity = old_time
        
        # Check for idle connections
        idle_connections = resource_manager.get_idle_connections()
        
        assert len(idle_connections) == 1
        assert idle_connections[0][0] == mock_websocket
        assert idle_connections[0][1] == metrics
    
    def test_resource_metrics_calculation(self, resource_manager):
        """Test resource metrics calculation"""
        # Create multiple mock connections
        mock_websockets = [MagicMock(spec=WebSocket) for _ in range(3)]
        
        for i, ws in enumerate(mock_websockets):
            metrics = resource_manager.register_connection(ws, f"client_{i}")
            metrics.messages_sent = i * 10
            metrics.messages_received = i * 5
            metrics.memory_usage_mb = 2.5  # Slightly higher than default
        
        # Get resource metrics
        metrics = resource_manager.get_resource_metrics()
        
        assert metrics["connection_count"] == 3
        assert metrics["max_connections"] == 5
        assert metrics["connection_utilization"] == 0.6  # 3/5
        assert metrics["total_connections_ever"] == 3
        assert metrics["total_memory_usage_mb"] == 7.5  # 3 * 2.5
        assert metrics["average_memory_per_connection_mb"] == 2.5
        assert metrics["backpressure_active"] is False  # Below threshold
    
    def test_backpressure_activation(self, resource_manager):
        """Test backpressure detection"""
        # Create connections to trigger backpressure
        mock_websockets = [MagicMock(spec=WebSocket) for _ in range(4)]  # 80% of 5
        
        for i, ws in enumerate(mock_websockets):
            resource_manager.register_connection(ws, f"client_{i}")
        
        metrics = resource_manager.get_resource_metrics()
        assert metrics["backpressure_active"] is True
        assert metrics["connection_utilization"] == 0.8
    
    def test_memory_estimation(self, resource_manager, mock_websocket):
        """Test memory usage estimation"""
        estimate = resource_manager._estimate_connection_memory(mock_websocket)
        
        # Should return default 2.0MB
        assert estimate == 2.0
    
    @pytest.mark.asyncio
    async def test_cleanup_idle_connections(self, resource_manager):
        """Test idle connection cleanup process"""
        # Create mock websockets
        mock_websockets = [AsyncMock(spec=WebSocket) for _ in range(3)]
        
        # Register connections
        for i, ws in enumerate(mock_websockets):
            metrics = resource_manager.register_connection(ws, f"client_{i}")
            # Make first two idle
            if i < 2:
                metrics.last_activity = datetime.now() - timedelta(seconds=15)
        
        assert resource_manager.connection_count == 3
        
        # Run cleanup
        await resource_manager._cleanup_idle_connections()
        
        # Should have sent warnings to idle connections
        for ws in mock_websockets[:2]:
            ws.send_json.assert_called_once()
            call_args = ws.send_json.call_args[0][0]
            assert call_args["type"] == "idle_timeout_warning"
        
        # Third connection should not receive warning
        mock_websockets[2].send_json.assert_not_called()
        
        # Run cleanup again (after warning period)
        await resource_manager._cleanup_idle_connections()
        
        # Idle connections should be closed
        for ws in mock_websockets[:2]:
            ws.close.assert_called_once_with(code=1000, reason="Idle timeout")
        
        # Should have fewer registered connections
        assert resource_manager.connection_count == 1
    
    @pytest.mark.asyncio
    async def test_heartbeat_sending(self, resource_manager):
        """Test heartbeat sending to active connections"""
        # Create mock websockets
        mock_websockets = [AsyncMock(spec=WebSocket) for _ in range(2)]
        
        # Register connections
        for i, ws in enumerate(mock_websockets):
            resource_manager.register_connection(ws, f"client_{i}")
        
        # Send heartbeats
        await resource_manager._send_heartbeats()
        
        # Verify heartbeats were sent
        for ws in mock_websockets:
            ws.send_json.assert_called_once()
            call_args = ws.send_json.call_args[0][0]
            assert call_args["type"] == "heartbeat"
            assert "timestamp" in call_args
            assert "connection_id" in call_args
    
    @pytest.mark.asyncio
    async def test_heartbeat_failure_cleanup(self, resource_manager):
        """Test cleanup of connections that fail heartbeat"""
        # Create mock websockets - one that fails heartbeat
        working_ws = AsyncMock(spec=WebSocket)
        failing_ws = AsyncMock(spec=WebSocket)
        failing_ws.send_json.side_effect = Exception("Connection failed")
        
        # Register both connections
        resource_manager.register_connection(working_ws, "working_client")
        resource_manager.register_connection(failing_ws, "failing_client")
        
        assert resource_manager.connection_count == 2
        
        # Send heartbeats
        await resource_manager._send_heartbeats()
        
        # Working connection should get heartbeat
        working_ws.send_json.assert_called_once()
        
        # Failing connection should be cleaned up
        assert resource_manager.connection_count == 1
        assert failing_ws not in resource_manager.connections
        assert working_ws in resource_manager.connections
    
    @pytest.mark.asyncio
    async def test_background_task_lifecycle(self, resource_manager):
        """Test starting and stopping background tasks"""
        # Start tasks
        resource_manager.start_background_tasks()
        
        assert resource_manager._cleanup_task is not None
        assert resource_manager._heartbeat_task is not None
        assert not resource_manager._cleanup_task.done()
        assert not resource_manager._heartbeat_task.done()
        
        # Stop tasks
        await resource_manager.stop_background_tasks()
        
        # Tasks should be cancelled
        assert resource_manager._cleanup_task.cancelled()
        assert resource_manager._heartbeat_task.cancelled()

class TestConnectionMetrics:
    """Test suite for ConnectionMetrics dataclass"""
    
    def test_connection_metrics_creation(self):
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
        assert metrics.is_alive is True
        assert len(metrics.subscriptions) == 0
        assert metrics.idle_warnings_sent == 0

# Performance benchmarks
@pytest.mark.benchmark
class TestWebSocketResourceManagerPerformance:
    """Performance tests for resource manager operations"""
    
    def test_connection_registration_performance(self, benchmark, resource_manager):
        """Benchmark connection registration performance"""
        mock_websockets = [MagicMock(spec=WebSocket) for _ in range(100)]
        
        def register_connections():
            for i, ws in enumerate(mock_websockets):
                resource_manager.register_connection(ws, f"client_{i}")
        
        benchmark(register_connections)
    
    def test_metrics_calculation_performance(self, benchmark, resource_manager):
        """Benchmark resource metrics calculation performance"""
        # Setup connections
        mock_websockets = [MagicMock(spec=WebSocket) for _ in range(100)]
        for i, ws in enumerate(mock_websockets):
            resource_manager.register_connection(ws, f"client_{i}")
        
        benchmark(resource_manager.get_resource_metrics)
    
    def test_idle_detection_performance(self, benchmark, resource_manager):
        """Benchmark idle connection detection performance"""
        # Setup connections with mixed activity times
        mock_websockets = [MagicMock(spec=WebSocket) for _ in range(100)]
        for i, ws in enumerate(mock_websockets):
            metrics = resource_manager.register_connection(ws, f"client_{i}")
            # Make half of them idle
            if i % 2 == 0:
                metrics.last_activity = datetime.now() - timedelta(seconds=15)
        
        benchmark(resource_manager.get_idle_connections)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])