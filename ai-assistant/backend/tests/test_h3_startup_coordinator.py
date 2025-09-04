"""
Test suite for H3: Database Initialization Race Condition Fix
Validates startup coordination, dependency management, and health checks
Architecture: Dr. Sarah Chen
"""
import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from startup_coordinator import (
    ApplicationStartupCoordinator,
    StartupState,
    ComponentState,
    ComponentStatus,
    ApplicationReadiness,
    StartupMetrics
)


class TestApplicationStartupCoordinator:
    """Test H3: Application startup coordination"""
    
    @pytest.fixture
    def coordinator(self):
        """Create coordinator instance"""
        return ApplicationStartupCoordinator()
    
    @pytest.mark.asyncio
    async def test_dependency_resolution(self, coordinator):
        """Test that dependency order is correctly resolved"""
        # Get resolved order
        order = coordinator._resolve_dependency_order()
        
        # Verify correct order
        assert order.index('config') < order.index('database')
        assert order.index('config') < order.index('cache')
        assert order.index('database') < order.index('orchestrator')
        assert order.index('cache') < order.index('orchestrator')
        assert order.index('orchestrator') < order.index('api_routes')
    
    @pytest.mark.asyncio
    async def test_circular_dependency_detection(self):
        """Test that circular dependencies are detected"""
        coordinator = ApplicationStartupCoordinator()
        
        # Create circular dependency
        coordinator.dependency_graph = {
            'a': ['b'],
            'b': ['c'],
            'c': ['a']  # Circular!
        }
        
        with pytest.raises(Exception, match="Circular dependency"):
            coordinator._resolve_dependency_order()
    
    @pytest.mark.asyncio
    async def test_component_registration(self, coordinator):
        """Test component registration"""
        # Mock initializer and health checker
        initializer = AsyncMock()
        health_checker = AsyncMock(return_value=True)
        
        # Register component
        coordinator.register_component(
            name='test_component',
            initializer=initializer,
            health_checker=health_checker,
            dependencies=['config'],
            critical=True
        )
        
        assert 'test_component' in coordinator.initializers
        assert 'test_component' in coordinator.health_checkers
        assert 'test_component' in coordinator.critical_components
        assert coordinator.dependency_graph['test_component'] == ['config']
    
    @pytest.mark.asyncio
    async def test_successful_initialization(self, coordinator):
        """Test successful application initialization"""
        # Register mock components
        for component in ['config', 'database', 'cache']:
            coordinator.register_component(
                name=component,
                initializer=AsyncMock(),
                health_checker=AsyncMock(return_value=True),
                dependencies=coordinator.dependency_graph.get(component, []),
                critical=(component in ['config', 'database'])
            )
        
        # Initialize application
        readiness = await coordinator.initialize_application()
        
        assert readiness.ready is True
        assert readiness.state == StartupState.READY
        assert len(readiness.failed_components) == 0
    
    @pytest.mark.asyncio
    async def test_critical_component_failure(self, coordinator):
        """Test that critical component failure prevents startup"""
        # Register components with failing database
        coordinator.register_component(
            name='config',
            initializer=AsyncMock(),
            health_checker=AsyncMock(return_value=True),
            dependencies=[],
            critical=True
        )
        
        # Database will fail
        failing_init = AsyncMock(side_effect=Exception("Database connection failed"))
        coordinator.register_component(
            name='database',
            initializer=failing_init,
            health_checker=AsyncMock(return_value=False),
            dependencies=['config'],
            critical=True
        )
        
        # Initialize application
        readiness = await coordinator.initialize_application()
        
        assert readiness.ready is False
        assert readiness.state == StartupState.FAILED
        assert 'database' in readiness.failed_components
    
    @pytest.mark.asyncio
    async def test_degraded_mode_operation(self, coordinator):
        """Test degraded mode when non-critical component fails"""
        # Register components
        coordinator.register_component(
            name='config',
            initializer=AsyncMock(),
            health_checker=AsyncMock(return_value=True),
            dependencies=[],
            critical=True
        )
        
        coordinator.register_component(
            name='database',
            initializer=AsyncMock(),
            health_checker=AsyncMock(return_value=True),
            dependencies=['config'],
            critical=True
        )
        
        # Cache is non-critical and will fail
        coordinator.register_component(
            name='cache',
            initializer=AsyncMock(side_effect=Exception("Cache unavailable")),
            health_checker=AsyncMock(return_value=False),
            dependencies=['config'],
            critical=False
        )
        
        # Initialize application
        readiness = await coordinator.initialize_application()
        
        assert readiness.ready is True
        assert readiness.state == StartupState.DEGRADED
        assert readiness.degraded is True
        assert 'cache' in readiness.failed_components
    
    @pytest.mark.asyncio
    async def test_initialization_timeout(self, coordinator):
        """Test component initialization timeout"""
        # Create slow initializer
        async def slow_init():
            await asyncio.sleep(10)  # Longer than timeout
        
        coordinator.component_timeout = 0.1  # Short timeout
        coordinator.register_component(
            name='slow_component',
            initializer=slow_init,
            critical=False
        )
        
        # Initialize
        await coordinator._initialize_component_safely('slow_component')
        
        # Check component failed due to timeout
        component = coordinator.components['slow_component']
        assert component.state == ComponentState.FAILED
        assert "timeout" in component.error.lower()
    
    @pytest.mark.asyncio
    async def test_health_check_validation(self, coordinator):
        """Test health check validation"""
        # Register components with different health states
        coordinator.register_component(
            name='healthy',
            initializer=AsyncMock(),
            health_checker=AsyncMock(return_value=True)
        )
        
        coordinator.register_component(
            name='unhealthy',
            initializer=AsyncMock(),
            health_checker=AsyncMock(return_value=False)
        )
        
        # Mark components as ready
        coordinator.components['healthy'].state = ComponentState.READY
        coordinator.components['unhealthy'].state = ComponentState.READY
        
        # Perform health checks
        health_results = await coordinator._perform_health_checks()
        
        assert health_results['healthy'] is True
        assert health_results['unhealthy'] is False
    
    @pytest.mark.asyncio
    async def test_startup_metrics_tracking(self, coordinator):
        """Test that startup metrics are tracked"""
        # Register and initialize components
        coordinator.register_component(
            name='config',
            initializer=AsyncMock(),
            health_checker=AsyncMock(return_value=True)
        )
        
        # Initialize application
        await coordinator.initialize_application()
        
        # Check metrics
        metrics = coordinator.startup_metrics.get_metrics()
        assert metrics['startup_attempts'] == 1
        assert metrics['successful_startups'] == 1
        assert 'config' in metrics['component_average_times']
    
    def test_is_ready_status(self, coordinator):
        """Test is_ready and is_healthy methods"""
        # Initially not ready
        assert coordinator.is_ready() is False
        assert coordinator.is_healthy() is False
        
        # Set to ready
        coordinator.startup_state = StartupState.READY
        assert coordinator.is_ready() is True
        assert coordinator.is_healthy() is True
        
        # Set to degraded
        coordinator.startup_state = StartupState.DEGRADED
        assert coordinator.is_ready() is True  # Still ready in degraded
        assert coordinator.is_healthy() is False  # Not healthy
        
        # Set to failed
        coordinator.startup_state = StartupState.FAILED
        assert coordinator.is_ready() is False
        assert coordinator.is_healthy() is False


class TestStartupMetrics:
    """Test startup metrics tracking"""
    
    def test_successful_startup_recording(self):
        """Test recording successful startups"""
        metrics = StartupMetrics()
        
        metrics.record_successful_startup(1500.0)
        metrics.record_successful_startup(2000.0)
        
        assert metrics.successful_startups == 2
        assert metrics.get_average_startup_time() == 1750.0
    
    def test_failed_startup_recording(self):
        """Test recording failed startups"""
        metrics = StartupMetrics()
        
        metrics.record_failed_startup("Database connection failed")
        metrics.record_failed_startup("Database connection failed")
        metrics.record_failed_startup("Cache initialization error")
        
        assert metrics.failed_startups == 3
        assert metrics.failure_reasons["Database connection failed"] == 2
        assert metrics.failure_reasons["Cache initialization error"] == 1
    
    def test_component_init_time_tracking(self):
        """Test component initialization time tracking"""
        metrics = StartupMetrics()
        
        metrics.record_component_init("database", 500.0)
        metrics.record_component_init("database", 700.0)
        metrics.record_component_init("cache", 100.0)
        
        result = metrics.get_metrics()
        assert result['component_average_times']['database'] == 600.0
        assert result['component_average_times']['cache'] == 100.0
    
    def test_metrics_aggregation(self):
        """Test complete metrics aggregation"""
        metrics = StartupMetrics()
        
        # Record various events
        metrics.startup_attempts = 5
        metrics.record_successful_startup(1000.0)
        metrics.record_successful_startup(1500.0)
        metrics.record_failed_startup("Error A")
        metrics.record_component_init("comp1", 200.0)
        
        result = metrics.get_metrics()
        
        assert result['startup_attempts'] == 5
        assert result['successful_startups'] == 2
        assert result['failed_startups'] == 1
        assert result['average_startup_time_ms'] == 1250.0
        assert 'Error A' in result['top_failure_reasons']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])