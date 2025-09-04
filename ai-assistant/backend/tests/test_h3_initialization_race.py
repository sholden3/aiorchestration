"""
Test suite for H3: Database Initialization Race Condition Fix

@fileoverview Tests for preventing API access before initialization
@author Sam Martinez v3.2.0 - Test Architecture
@testing_strategy Integration tests for initialization sequence
@references docs/fixes/H3-database-race-condition.md

FIX H3: Database Initialization Race Condition Tests
Tests the thread-safe initialization including:
- Initialization state tracking
- 503 responses during startup
- Health endpoint status reporting
- Concurrent request handling
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from main import AIBackendService, AITask, TaskResponse
from fastapi import HTTPException
from fastapi.testclient import TestClient


class TestH3InitializationRace:
    """Test suite for database initialization race condition fix"""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration"""
        config = Mock()
        config.systems.backend_port = 8000
        config.systems.cache_hot_size_mb = 100
        return config
    
    @pytest.fixture
    def backend_service(self, mock_config):
        """Create backend service instance"""
        with patch('main.IntelligentCache') as mock_cache:
            # Mock cache to avoid async task creation
            mock_cache_instance = Mock()
            mock_cache_instance.get_metrics = Mock(return_value={
                'hit_rate': 0.0,
                'tokens_saved': 0,
                'hot_cache_size_mb': 0.0,
                'warm_cache_files': 0
            })
            mock_cache.return_value = mock_cache_instance
            
            service = AIBackendService(config=mock_config)
            service.cache = mock_cache_instance
            return service
    
    @pytest.fixture
    def test_client(self, backend_service):
        """Create test client for API testing"""
        return TestClient(backend_service.app)
    
    def test_initialization_state_tracking(self, backend_service):
        """Test that initialization state is properly tracked"""
        # Initially should not be initialized
        assert backend_service._initialization_complete == False
        assert backend_service._initialization_error == None
        assert backend_service._startup_lock is not None
    
    @pytest.mark.asyncio
    async def test_ensure_initialized_blocks_before_ready(self, backend_service):
        """Test that _ensure_initialized blocks requests before initialization"""
        # Should raise 503 when not initialized
        with pytest.raises(HTTPException) as exc_info:
            await backend_service._ensure_initialized()
        
        assert exc_info.value.status_code == 503
        assert "still initializing" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_ensure_initialized_passes_after_ready(self, backend_service):
        """Test that _ensure_initialized allows requests after initialization"""
        # Mark as initialized
        backend_service._initialization_complete = True
        
        # Should not raise
        result = await backend_service._ensure_initialized()
        assert result == True
    
    @pytest.mark.asyncio
    async def test_ensure_initialized_reports_errors(self, backend_service):
        """Test that initialization errors are properly reported"""
        # Set an initialization error
        backend_service._initialization_error = "Database connection failed"
        
        with pytest.raises(HTTPException) as exc_info:
            await backend_service._ensure_initialized()
        
        assert exc_info.value.status_code == 503
        assert "Database connection failed" in exc_info.value.detail
    
    def test_health_endpoint_during_initialization(self, test_client):
        """Test health endpoint returns proper status during initialization"""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "initializing"
        assert data["initialized"] == False
    
    def test_health_endpoint_after_initialization(self, backend_service, test_client):
        """Test health endpoint returns healthy after initialization"""
        backend_service._initialization_complete = True
        
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["initialized"] == True
    
    def test_health_endpoint_with_error(self, backend_service, test_client):
        """Test health endpoint reports degraded status on error"""
        backend_service._initialization_error = "Failed to connect to database"
        
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["initialized"] == False
        assert "Failed to connect" in data["error"]
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_during_initialization(self, backend_service):
        """Test that concurrent requests are properly serialized during initialization"""
        # Track call order
        call_order = []
        
        async def mock_init():
            """Simulate slow initialization"""
            call_order.append("init_start")
            await asyncio.sleep(0.1)
            backend_service._initialization_complete = True
            call_order.append("init_complete")
        
        # Start initialization
        init_task = asyncio.create_task(mock_init())
        
        # Try concurrent requests
        async def try_request(request_id):
            try:
                call_order.append(f"request_{request_id}_start")
                await backend_service._ensure_initialized()
                call_order.append(f"request_{request_id}_success")
            except HTTPException:
                call_order.append(f"request_{request_id}_blocked")
        
        # Launch multiple concurrent requests
        request_tasks = [
            asyncio.create_task(try_request(1)),
            asyncio.create_task(try_request(2)),
            asyncio.create_task(try_request(3))
        ]
        
        # Wait a bit for requests to be blocked
        await asyncio.sleep(0.05)
        
        # Complete initialization
        await init_task
        
        # Now requests should succeed
        await asyncio.gather(*request_tasks)
        
        # Verify requests were blocked then succeeded
        assert "init_start" in call_order
        assert any("blocked" in item for item in call_order)
    
    def test_ai_execute_endpoint_blocked_before_init(self, test_client):
        """Test that /ai/execute endpoint is blocked before initialization"""
        task_data = {
            "prompt": "Test prompt",
            "use_cache": False
        }
        
        response = test_client.post("/ai/execute", json=task_data)
        
        assert response.status_code == 503
        assert "initializing" in response.json()["detail"]
    
    @patch('main.IntelligentCache')
    @patch('main.PersonaManager')
    @patch('main.ClaudeOptimizer')
    def test_ai_execute_endpoint_works_after_init(
        self, mock_claude, mock_persona, mock_cache, backend_service, test_client
    ):
        """Test that /ai/execute endpoint works after initialization"""
        # Mark as initialized
        backend_service._initialization_complete = True
        
        # Mock the execute method
        mock_claude_instance = Mock()
        mock_claude_instance.execute_with_persona = AsyncMock(return_value={
            'success': True,
            'response': 'Test response'
        })
        mock_claude.return_value = mock_claude_instance
        backend_service.claude = mock_claude_instance
        
        # Mock cache
        mock_cache_instance = Mock()
        mock_cache_instance.generate_key = Mock(return_value="test_key")
        mock_cache_instance.get = AsyncMock(return_value=None)
        mock_cache.return_value = mock_cache_instance
        backend_service.cache = mock_cache_instance
        
        task_data = {
            "prompt": "Test prompt",
            "use_cache": False
        }
        
        response = test_client.post("/ai/execute", json=task_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
    
    def test_orchestration_status_blocked_before_init(self, test_client):
        """Test that /orchestration/status is blocked before initialization"""
        response = test_client.get("/orchestration/status")
        
        assert response.status_code == 503
    
    def test_agents_spawn_blocked_before_init(self, test_client):
        """Test that /agents/spawn is blocked before initialization"""
        response = test_client.post("/agents/spawn", json={"type": "claude_assistant"})
        
        assert response.status_code == 503
    
    def test_metrics_cache_returns_empty_during_init(self, test_client):
        """Test that /metrics/cache returns zeros during initialization"""
        response = test_client.get("/metrics/cache")
        
        assert response.status_code == 200
        data = response.json()
        assert data["hit_rate"] == 0.0
        assert data["tokens_saved"] == 0
        assert data["total_requests"] == 0
    
    def test_metrics_performance_returns_initializing(self, test_client):
        """Test that /metrics/performance indicates initialization status"""
        response = test_client.get("/metrics/performance")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "initializing"
        assert "System is still initializing" in data["message"]
    
    @pytest.mark.asyncio
    async def test_startup_lock_prevents_race_condition(self, backend_service):
        """Test that startup lock prevents race conditions"""
        # Track whether initialization is in progress
        initialization_count = 0
        
        async def mock_startup():
            nonlocal initialization_count
            async with backend_service._startup_lock:
                initialization_count += 1
                await asyncio.sleep(0.1)
                backend_service._initialization_complete = True
        
        # Try to start multiple initializations
        tasks = [
            asyncio.create_task(mock_startup()),
            asyncio.create_task(mock_startup()),
            asyncio.create_task(mock_startup())
        ]
        
        await asyncio.gather(*tasks)
        
        # Only one initialization should have occurred
        assert initialization_count == 1
        assert backend_service._initialization_complete == True
    
    @pytest.mark.asyncio
    async def test_error_recovery_scenario(self, backend_service):
        """Test error recovery during initialization"""
        # Simulate initialization error
        backend_service._initialization_error = "Database unavailable"
        
        # Requests should get error status
        with pytest.raises(HTTPException) as exc_info:
            await backend_service._ensure_initialized()
        assert "Database unavailable" in exc_info.value.detail
        
        # Simulate recovery
        backend_service._initialization_error = None
        backend_service._initialization_complete = True
        
        # Now requests should succeed
        result = await backend_service._ensure_initialized()
        assert result == True


class TestH3Integration:
    """Integration tests for the full initialization sequence"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_startup_sequence(self):
        """Test the complete startup sequence with mocked dependencies"""
        with patch('main.DatabaseManager') as mock_db, \
             patch('main.AIOrchestrationEngine') as mock_orchestrator, \
             patch('main.db_service') as mock_db_service:
            
            # Mock async methods
            mock_db_instance = Mock()
            mock_db_instance.initialize = AsyncMock()
            mock_db_instance.close = AsyncMock()
            mock_db.return_value = mock_db_instance
            
            mock_orchestrator_instance = Mock()
            mock_orchestrator_instance.start_orchestration = AsyncMock()
            mock_orchestrator_instance.stop_orchestration = AsyncMock()
            mock_orchestrator.return_value = mock_orchestrator_instance
            
            mock_db_service.connect = AsyncMock()
            mock_db_service.initialize_schema = AsyncMock()
            mock_db_service.is_connected = True
            
            # Create service
            service = AIBackendService()
            
            # Simulate startup event
            startup_handler = None
            for call in service.app.router.on_startup:
                startup_handler = call
                break
            
            assert startup_handler is not None
            
            # Run startup
            await startup_handler()
            
            # Verify initialization completed
            assert service._initialization_complete == True
            assert service._initialization_error == None
            
            # Verify all services initialized
            mock_db_service.connect.assert_called_once()
            mock_db_service.initialize_schema.assert_called_once()
            mock_db_instance.initialize.assert_called_once()
            mock_orchestrator_instance.start_orchestration.assert_called_once()
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_startup_failure_handling(self):
        """Test proper error handling when startup fails"""
        with patch('main.DatabaseManager') as mock_db:
            # Make database initialization fail
            mock_db_instance = Mock()
            mock_db_instance.initialize = AsyncMock(
                side_effect=Exception("Database connection failed")
            )
            mock_db.return_value = mock_db_instance
            
            # Create service
            service = AIBackendService()
            
            # Get startup handler
            startup_handler = None
            for call in service.app.router.on_startup:
                startup_handler = call
                break
            
            # Run startup (should handle error gracefully)
            await startup_handler()
            
            # Verify error was captured
            assert service._initialization_complete == False
            assert service._initialization_error is not None
            assert "Database connection failed" in service._initialization_error


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--color=yes"])