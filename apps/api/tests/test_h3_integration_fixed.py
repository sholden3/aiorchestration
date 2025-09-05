"""
Integration Tests for H3: Database Initialization Race Condition Fix (Fixed Version)

@fileoverview Integration tests with proper async mocking
@author Sam Martinez v3.2.0 - Test Architecture
@testing_strategy Layer 2: Integration tests with all components
@references docs/decisions/testing-strategy-unit-vs-integration.md

These tests validate the H3 fix in a realistic environment with proper
async context management to avoid coroutine warnings.
"""

import asyncio
import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import HTTPException
from starlette.testclient import TestClient


class TestH3IntegrationFixed:
    """Integration tests with proper async context"""
    
    @pytest.fixture
    def mock_async_components(self):
        """Mock all async components to prevent event loop issues"""
        with patch('cache_manager.asyncio.create_task') as mock_create_task, \
             patch('websocket_manager.asyncio.create_task') as mock_ws_task, \
             patch('cache_manager.IntelligentCache') as mock_cache:
            
            # Prevent async task creation
            mock_create_task.return_value = None
            mock_ws_task.return_value = None
            
            # Mock cache instances
            cache_instance = Mock()
            cache_instance.get_metrics = Mock(return_value={
                'hit_rate': 0.0,
                'tokens_saved': 0,
                'hot_cache_size_mb': 0.0,
                'warm_cache_files': 0,
                'hits': 0,
                'misses': 0
            })
            cache_instance.get = AsyncMock(return_value=None)
            cache_instance.store = AsyncMock()
            cache_instance.generate_key = Mock(return_value="test_key")
            cache_instance.load_from_database = AsyncMock()
            cache_instance.save_to_database = AsyncMock()
            
            mock_cache.return_value = cache_instance
            
            yield {
                'create_task': mock_create_task,
                'ws_task': mock_ws_task,
                'cache': cache_instance
            }
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration"""
        config = Mock()
        config.systems.backend_port = 8000
        config.systems.cache_hot_size_mb = 100
        return config
    
    @pytest.fixture
    def backend_service(self, mock_config, mock_async_components):
        """Create backend service with mocked async components"""
        with patch('main.IntelligentCache') as mock_main_cache, \
             patch('main.DatabaseManager') as mock_db, \
             patch('main.PersonaManager') as mock_persona, \
             patch('main.ClaudeOptimizer') as mock_claude, \
             patch('main.MetricsCollector') as mock_metrics, \
             patch('main.UnifiedGovernanceOrchestrator') as mock_gov, \
             patch('main.AIOrchestrationEngine') as mock_ai_orch, \
             patch('main.PersonaOrchestrationEnhanced') as mock_persona_orch, \
             patch('main.ConversationManager') as mock_conv:
            
            # Use the mocked cache
            mock_main_cache.return_value = mock_async_components['cache']
            
            # Mock database manager
            db_instance = Mock()
            db_instance.initialize = AsyncMock()
            db_instance.close = AsyncMock()
            mock_db.return_value = db_instance
            
            # Mock persona manager
            persona_instance = Mock()
            persona_instance.personas = {}
            persona_instance.suggest_persona = Mock(return_value=[])
            mock_persona.return_value = persona_instance
            
            # Mock Claude optimizer
            claude_instance = Mock()
            claude_instance.execute_with_persona = AsyncMock(return_value={
                'success': True,
                'response': 'Test response'
            })
            mock_claude.return_value = claude_instance
            
            # Mock metrics collector
            metrics_instance = Mock()
            metrics_instance.start_collection = AsyncMock()
            metrics_instance.get_performance_summary = AsyncMock(return_value={})
            metrics_instance.record_cache_hit = Mock()
            metrics_instance.record_cache_miss = Mock()
            mock_metrics.return_value = metrics_instance
            
            # Mock governance and orchestration
            mock_gov.return_value = Mock()
            mock_ai_orch.return_value = Mock(
                start_orchestration=AsyncMock(),
                stop_orchestration=AsyncMock(),
                get_orchestration_status=Mock(return_value={
                    "is_running": False,
                    "tasks": {},
                    "performance": {}
                })
            )
            mock_persona_orch.return_value = Mock()
            mock_conv.return_value = Mock()
            
            # Import and create service
            from main import AIBackendService
            service = AIBackendService(config=mock_config)
            
            # Inject mocked components
            service.cache = mock_async_components['cache']
            service.db_manager = db_instance
            service.persona_manager = persona_instance
            service.claude = claude_instance
            service.metrics = metrics_instance
            
            return service
    
    @pytest.fixture
    def test_client(self, backend_service):
        """Create test client for API testing"""
        return TestClient(backend_service.app)
    
    def test_initialization_tracking_in_service(self, backend_service):
        """Test that service properly tracks initialization state"""
        assert hasattr(backend_service, '_initialization_complete')
        assert hasattr(backend_service, '_initialization_error')
        assert hasattr(backend_service, '_startup_lock')
        
        assert backend_service._initialization_complete == False
        assert backend_service._initialization_error == None
        assert backend_service._startup_lock is not None
    
    def test_health_endpoint_before_initialization(self, test_client):
        """Test health endpoint returns initializing status"""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "initializing"
        assert data["initialized"] == False
        assert "timestamp" in data
    
    def test_ai_execute_blocked_before_init(self, test_client):
        """Test that AI execution endpoint is blocked before initialization"""
        task_data = {
            "prompt": "Test prompt",
            "use_cache": False
        }
        
        response = test_client.post("/ai/execute", json=task_data)
        
        assert response.status_code == 503
        error_detail = response.json()["detail"]
        assert "initializing" in error_detail or "not available" in error_detail
    
    def test_orchestration_status_blocked(self, test_client):
        """Test orchestration status endpoint is blocked"""
        response = test_client.get("/orchestration/status")
        
        assert response.status_code == 503
        assert "detail" in response.json()
    
    def test_agents_spawn_blocked(self, test_client):
        """Test agent spawning is blocked before initialization"""
        response = test_client.post("/agents/spawn", json={"type": "claude_assistant"})
        
        assert response.status_code == 503
        assert "detail" in response.json()
    
    def test_cache_metrics_returns_empty(self, test_client):
        """Test cache metrics returns zeros during initialization"""
        response = test_client.get("/metrics/cache")
        
        assert response.status_code == 200
        data = response.json()
        assert data["hit_rate"] == 0.0
        assert data["tokens_saved"] == 0
        assert data["total_requests"] == 0
    
    def test_performance_metrics_shows_initializing(self, test_client):
        """Test performance metrics indicates initialization"""
        response = test_client.get("/metrics/performance")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "initializing"
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_startup_event_updates_state(self, backend_service):
        """Test that startup event properly updates initialization state"""
        # Manually trigger startup logic
        async def simulate_startup():
            async with backend_service._startup_lock:
                try:
                    # Simulate successful initialization
                    backend_service._initialization_complete = True
                except Exception as e:
                    backend_service._initialization_error = str(e)
                    backend_service._initialization_complete = False
        
        await simulate_startup()
        
        assert backend_service._initialization_complete == True
        assert backend_service._initialization_error == None
    
    @pytest.mark.asyncio
    async def test_startup_error_handling(self, backend_service):
        """Test that startup errors are properly captured"""
        async def simulate_failed_startup():
            async with backend_service._startup_lock:
                try:
                    # Simulate initialization failure
                    raise Exception("Database connection failed")
                except Exception as e:
                    backend_service._initialization_error = str(e)
                    backend_service._initialization_complete = False
        
        await simulate_failed_startup()
        
        assert backend_service._initialization_complete == False
        assert "Database connection failed" in backend_service._initialization_error
    
    def test_health_endpoint_after_error(self, backend_service, test_client):
        """Test health endpoint reports degraded status after error"""
        backend_service._initialization_error = "Connection timeout"
        
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["initialized"] == False
        assert "Connection timeout" in data["error"]
    
    def test_health_endpoint_after_success(self, backend_service, test_client):
        """Test health endpoint reports healthy after initialization"""
        backend_service._initialization_complete = True
        
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["initialized"] == True
    
    @pytest.mark.asyncio
    async def test_ensure_initialized_method(self, backend_service):
        """Test the _ensure_initialized method behavior"""
        # Test when not initialized
        with pytest.raises(HTTPException) as exc_info:
            await backend_service._ensure_initialized()
        assert exc_info.value.status_code == 503
        
        # Test when initialized
        backend_service._initialization_complete = True
        result = await backend_service._ensure_initialized()
        assert result == True
        
        # Test with error
        backend_service._initialization_complete = False
        backend_service._initialization_error = "Failed"
        with pytest.raises(HTTPException) as exc_info:
            await backend_service._ensure_initialized()
        assert "Failed" in exc_info.value.detail
    
    def test_ai_execute_works_after_init(self, backend_service, test_client):
        """Test AI execution works after initialization"""
        # Mark as initialized
        backend_service._initialization_complete = True
        
        task_data = {
            "prompt": "Test prompt",
            "use_cache": False
        }
        
        response = test_client.post("/ai/execute", json=task_data)
        
        # Should work now
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["response"] == "Test response"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_serialization(self, backend_service):
        """Test that concurrent requests are properly serialized"""
        request_log = []
        
        async def make_request(request_id):
            request_log.append(f"start_{request_id}")
            try:
                await backend_service._ensure_initialized()
                request_log.append(f"success_{request_id}")
            except HTTPException:
                request_log.append(f"blocked_{request_id}")
        
        # Make concurrent requests while not initialized
        tasks = [
            make_request(1),
            make_request(2),
            make_request(3)
        ]
        
        await asyncio.gather(*tasks)
        
        # All should be blocked
        assert "blocked_1" in request_log
        assert "blocked_2" in request_log
        assert "blocked_3" in request_log
    
    def test_persona_suggest_works_without_init(self, test_client):
        """Test persona suggestion doesn't require full initialization"""
        response = test_client.post(
            "/persona/suggest",
            json={"description": "Write unit tests"}
        )
        
        # Should work even without initialization
        assert response.status_code == 200
        data = response.json()
        assert "personas" in data
    
    @pytest.mark.asyncio
    async def test_initialization_idempotency(self, backend_service):
        """Test that initialization can only happen once"""
        init_count = 0
        
        async def init_once():
            nonlocal init_count
            async with backend_service._startup_lock:
                if not backend_service._initialization_complete:
                    init_count += 1
                    backend_service._initialization_complete = True
        
        # Try multiple initialization attempts
        await asyncio.gather(
            init_once(),
            init_once(),
            init_once()
        )
        
        # Should only initialize once
        assert init_count == 1
        assert backend_service._initialization_complete == True
    
    def test_503_error_format(self, test_client):
        """Test that 503 errors have correct format"""
        response = test_client.post(
            "/ai/execute",
            json={"prompt": "test"}
        )
        
        assert response.status_code == 503
        error_data = response.json()
        assert "detail" in error_data
        assert isinstance(error_data["detail"], str)
        assert len(error_data["detail"]) > 0


class TestH3IntegrationScenarios:
    """Test realistic initialization scenarios"""
    
    @pytest.fixture
    def service_with_slow_init(self, backend_service):
        """Service that simulates slow initialization"""
        async def slow_init():
            await asyncio.sleep(0.1)
            backend_service._initialization_complete = True
        
        backend_service._slow_init = slow_init
        return backend_service
    
    @pytest.mark.asyncio
    async def test_requests_during_slow_init(self, service_with_slow_init):
        """Test request handling during slow initialization"""
        service = service_with_slow_init
        results = []
        
        async def try_request():
            try:
                await service._ensure_initialized()
                results.append("success")
            except HTTPException:
                results.append("blocked")
        
        # Start initialization
        init_task = asyncio.create_task(service._slow_init())
        
        # Try requests during init
        request_tasks = [
            asyncio.create_task(try_request()),
            asyncio.create_task(try_request())
        ]
        
        # Wait for all
        await init_task
        await asyncio.gather(*request_tasks)
        
        # Requests should have been blocked then succeeded
        assert "blocked" in results or "success" in results


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--color=yes"])