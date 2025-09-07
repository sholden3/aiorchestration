"""
Test suite for plugin lifecycle management system.

This module provides comprehensive tests for the PluginLifecycleManager,
covering state management, health monitoring, auto-restart, resource
monitoring, and event handling.
"""

import asyncio
import pytest
import threading
import time
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from typing import Any, Dict

# Test imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from libs.governance.plugins.lifecycle import (
    PluginLifecycleManager,
    PluginLifecycleError,
    PluginStateTransitionError,
    ResourceLimitExceededError,
    RestartAttempt,
    PluginResourceUsage,
    StateTransitionRecord
)
from libs.governance.plugins.base import (
    IValidatorPlugin,
    PluginState,
    PluginHealth,
    PluginMetadata,
    ValidationResult,
    ValidationSeverity
)
from libs.governance.plugins.registry import PluginRegistry


class MockValidatorPlugin(IValidatorPlugin):
    """Mock plugin for testing."""
    
    def __init__(self, metadata: PluginMetadata):
        self._metadata = metadata
        self._state = PluginState.UNLOADED
        self._config = {}
        self._start_time = None
        self._error_count = 0
        self._initialized = False
        self._fail_initialization = False
        self._fail_teardown = False
        self._fail_validation = False
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    @property
    def health(self) -> PluginHealth:
        uptime = time.time() - self._start_time if self._start_time else 0.0
        return PluginHealth(
            state=self._state,
            healthy=self._state == PluginState.READY and self._error_count == 0,
            last_check=datetime.now(),
            uptime_seconds=uptime,
            error_count=self._error_count
        )
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        if self._fail_initialization:
            raise RuntimeError("Mock initialization failure")
        
        self._state = PluginState.READY
        self._config = config
        self._start_time = time.time()
        self._initialized = True
    
    async def validate(self, context: Dict[str, Any]) -> ValidationResult:
        if self._fail_validation:
            raise RuntimeError("Mock validation failure")
        
        return ValidationResult(
            success=True,
            plugin_name=self._metadata.name,
            severity=ValidationSeverity.INFO,
            messages=["Mock validation passed"]
        )
    
    async def configure(self, config: Dict[str, Any]) -> None:
        self._config.update(config)
    
    async def teardown(self) -> None:
        if self._fail_teardown:
            raise RuntimeError("Mock teardown failure")
        
        self._state = PluginState.STOPPED
        self._initialized = False
    
    def set_fail_initialization(self, fail: bool = True):
        """Set whether initialization should fail."""
        self._fail_initialization = fail
    
    def set_fail_teardown(self, fail: bool = True):
        """Set whether teardown should fail."""
        self._fail_teardown = fail
    
    def set_fail_validation(self, fail: bool = True):
        """Set whether validation should fail."""
        self._fail_validation = fail


@pytest.fixture
def mock_registry():
    """Create a mock plugin registry."""
    registry = Mock(spec=PluginRegistry)
    registry._registry_lock = threading.RLock()
    registry._metadata = {}
    
    # Mock metadata
    test_metadata = PluginMetadata(
        name="test_plugin",
        version="1.0.0",
        description="Test plugin",
        author="Test Author",
        license="MIT"
    )
    registry._metadata["test_plugin"] = test_metadata
    
    registry.get_plugin.return_value = MockValidatorPlugin
    registry.list_plugins.return_value = [test_metadata]
    
    return registry


@pytest.fixture
def lifecycle_manager(mock_registry, tmp_path):
    """Create a lifecycle manager with mock registry."""
    # Create temporary config
    config_dir = tmp_path / "config" / "governance"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / "lifecycle.yaml"
    config_content = {
        'health_check': {
            'interval_seconds': 1,  # Fast for testing
            'timeout_seconds': 5
        },
        'restart_policy': {
            'max_attempts': 3,
            'backoff_multiplier': 2,
            'initial_delay_seconds': 0.1  # Fast for testing
        },
        'resource_limits': {
            'max_memory_mb': 100,
            'max_cpu_percent': 50
        },
        'state_transitions': {
            'timeout_seconds': 5  # Fast for testing
        },
        'logging': {
            'level': 'INFO',
            'log_state_transitions': True,
            'log_health_checks': True,
            'log_resource_usage': True
        }
    }
    
    with open(config_file, 'w') as f:
        yaml.dump(config_content, f)
    
    # Mock the config path lookup
    with patch('libs.governance.plugins.lifecycle.Path') as mock_path:
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.__truediv__ = lambda self, other: config_file
        
        # Create manager in the context of the mocked path
        with patch.object(PluginLifecycleManager, '_load_config') as mock_load_config:
            manager = PluginLifecycleManager(registry=mock_registry)
            manager._config = config_content
            return manager


@pytest.mark.asyncio
class TestPluginLifecycleManager:
    """Test suite for PluginLifecycleManager."""
    
    async def test_start_plugin_success(self, lifecycle_manager):
        """Test successful plugin start."""
        result = await lifecycle_manager.start_plugin("test_plugin")
        
        assert result is True
        assert lifecycle_manager.get_plugin_state("test_plugin") == PluginState.READY
        assert "test_plugin" in lifecycle_manager._plugin_instances
    
    async def test_start_plugin_not_found(self, lifecycle_manager):
        """Test starting non-existent plugin."""
        lifecycle_manager._registry.get_plugin.return_value = None
        
        result = await lifecycle_manager.start_plugin("nonexistent_plugin")
        
        assert result is False
        assert lifecycle_manager.get_plugin_state("nonexistent_plugin") == PluginState.ERROR
    
    async def test_start_plugin_initialization_failure(self, lifecycle_manager):
        """Test plugin start with initialization failure."""
        # Mock plugin class to fail initialization
        def failing_plugin_class(metadata):
            plugin = MockValidatorPlugin(metadata)
            plugin.set_fail_initialization(True)
            return plugin
        
        lifecycle_manager._registry.get_plugin.return_value = failing_plugin_class
        
        result = await lifecycle_manager.start_plugin("test_plugin")
        
        assert result is False
        assert lifecycle_manager.get_plugin_state("test_plugin") == PluginState.ERROR
    
    async def test_stop_plugin_success(self, lifecycle_manager):
        """Test successful plugin stop."""
        # Start plugin first
        await lifecycle_manager.start_plugin("test_plugin")
        
        result = await lifecycle_manager.stop_plugin("test_plugin")
        
        assert result is True
        assert lifecycle_manager.get_plugin_state("test_plugin") == PluginState.STOPPED
        assert "test_plugin" not in lifecycle_manager._plugin_instances
    
    async def test_stop_plugin_not_running(self, lifecycle_manager):
        """Test stopping non-running plugin."""
        result = await lifecycle_manager.stop_plugin("test_plugin")
        
        assert result is False
    
    async def test_restart_plugin_success(self, lifecycle_manager):
        """Test successful plugin restart."""
        # Start plugin first
        await lifecycle_manager.start_plugin("test_plugin")
        
        result = await lifecycle_manager.restart_plugin("test_plugin")
        
        assert result is True
        assert lifecycle_manager.get_plugin_state("test_plugin") == PluginState.READY
    
    async def test_restart_plugin_max_attempts(self, lifecycle_manager):
        """Test restart with max attempts exceeded."""
        # Create failing plugin
        def failing_plugin_class(metadata):
            plugin = MockValidatorPlugin(metadata)
            plugin.set_fail_initialization(True)
            return plugin
        
        lifecycle_manager._registry.get_plugin.return_value = failing_plugin_class
        
        # Attempt multiple restarts
        results = []
        for _ in range(4):  # More than max_attempts (3)
            result = await lifecycle_manager.restart_plugin("test_plugin")
            results.append(result)
        
        # First 3 should be attempted, 4th should be blocked by circuit breaker
        assert results == [False, False, False, False]
        assert lifecycle_manager._circuit_breakers.get("test_plugin") is True
    
    async def test_start_all_plugins(self, lifecycle_manager):
        """Test starting all plugins."""
        result = await lifecycle_manager.start_all()
        
        assert "test_plugin" in result
        assert result["test_plugin"] is True
    
    async def test_stop_all_plugins(self, lifecycle_manager):
        """Test stopping all plugins."""
        # Start some plugins first
        await lifecycle_manager.start_plugin("test_plugin")
        
        result = await lifecycle_manager.stop_all()
        
        assert "test_plugin" in result
        assert result["test_plugin"] is True
    
    async def test_monitor_health(self, lifecycle_manager):
        """Test health monitoring."""
        # Start plugin first
        await lifecycle_manager.start_plugin("test_plugin")
        
        health_status = await lifecycle_manager.monitor_health()
        
        assert "test_plugin" in health_status
        assert isinstance(health_status["test_plugin"], PluginHealth)
        assert health_status["test_plugin"].state == PluginState.READY
    
    async def test_state_transitions(self, lifecycle_manager):
        """Test state transition validation."""
        # Test valid transition
        async with lifecycle_manager._state_transition_context("test_plugin", PluginState.LOADING):
            pass
        
        assert lifecycle_manager.get_plugin_state("test_plugin") == PluginState.LOADING
        
        # Test invalid transition
        with pytest.raises(PluginStateTransitionError):
            async with lifecycle_manager._state_transition_context("test_plugin", PluginState.STOPPED):
                pass
    
    def test_event_system(self, lifecycle_manager):
        """Test event registration and handling."""
        events_received = []
        
        def event_handler(event, data):
            events_received.append((event, data))
        
        # Register handler
        lifecycle_manager.register_event_handler("test_event", event_handler)
        
        # Emit event
        asyncio.run(lifecycle_manager._emit_event("test_event", {"test": "data"}))
        
        assert len(events_received) == 1
        assert events_received[0][0] == "test_event"
        assert events_received[0][1]["test"] == "data"
        
        # Unregister handler
        lifecycle_manager.unregister_event_handler("test_event", event_handler)
        
        # Emit again - should not be received
        asyncio.run(lifecycle_manager._emit_event("test_event", {"test": "data2"}))
        
        assert len(events_received) == 1  # Still only 1
    
    async def test_monitoring_tasks(self, lifecycle_manager):
        """Test starting and stopping monitoring tasks."""
        await lifecycle_manager.start_monitoring()
        
        assert lifecycle_manager._health_check_task is not None
        assert not lifecycle_manager._health_check_task.done()
        
        await lifecycle_manager.stop_monitoring()
        
        assert lifecycle_manager._health_check_task is None
    
    async def test_graceful_shutdown(self, lifecycle_manager):
        """Test graceful shutdown."""
        # Start plugin and monitoring
        await lifecycle_manager.start_plugin("test_plugin")
        await lifecycle_manager.start_monitoring()
        
        # Shutdown
        await lifecycle_manager.shutdown()
        
        assert len(lifecycle_manager._plugin_instances) == 0
        assert len(lifecycle_manager._plugin_states) == 0
        assert lifecycle_manager._health_check_task is None
    
    @pytest.mark.skipif(
        __import__('libs.governance.plugins.lifecycle').governance.plugins.lifecycle.psutil is None,
        reason="psutil not available"
    )
    async def test_resource_monitoring(self, lifecycle_manager):
        """Test resource usage monitoring."""
        # Start plugin first
        await lifecycle_manager.start_plugin("test_plugin")
        
        # Update resource usage
        await lifecycle_manager._update_resource_usage("test_plugin")
        
        assert "test_plugin" in lifecycle_manager._resource_usage
        usage = lifecycle_manager._resource_usage["test_plugin"]
        assert isinstance(usage, PluginResourceUsage)
        assert usage.memory_mb >= 0
    
    def test_configuration_loading(self, tmp_path):
        """Test configuration loading with defaults."""
        # Mock the registry to avoid initialization issues
        with patch('libs.governance.plugins.lifecycle.PluginRegistry') as mock_registry_class:
            mock_registry = Mock()
            mock_registry._registry_lock = threading.RLock()
            mock_registry_class.return_value = mock_registry
            
            # Mock Path to return non-existent file so defaults are used
            with patch('libs.governance.plugins.lifecycle.Path') as mock_path:
                mock_path.return_value.exists.return_value = False
                
                manager = PluginLifecycleManager()
                
                # Verify the default config was loaded
                assert 'health_check' in manager._config
                assert 'restart_policy' in manager._config
                assert 'resource_limits' in manager._config
                assert manager._config['health_check']['interval_seconds'] == 60
                assert manager._config['restart_policy']['max_attempts'] == 3


@pytest.mark.asyncio 
class TestPluginLifecycleExceptions:
    """Test exception handling in lifecycle manager."""
    
    async def test_plugin_lifecycle_error(self):
        """Test PluginLifecycleError exception."""
        original_error = ValueError("Original error")
        error = PluginLifecycleError(
            "Lifecycle error",
            plugin_name="test_plugin",
            original_exception=original_error
        )
        
        assert str(error) == "Lifecycle error"
        assert error.plugin_name == "test_plugin"
        assert error.original_exception == original_error
    
    async def test_plugin_state_transition_error(self):
        """Test PluginStateTransitionError exception."""
        error = PluginStateTransitionError(
            "Invalid transition",
            plugin_name="test_plugin",
            current_state=PluginState.READY,
            target_state=PluginState.UNLOADED
        )
        
        assert str(error) == "Invalid transition"
        assert error.plugin_name == "test_plugin"
        assert error.current_state == PluginState.READY
        assert error.target_state == PluginState.UNLOADED
    
    async def test_resource_limit_exceeded_error(self):
        """Test ResourceLimitExceededError exception."""
        error = ResourceLimitExceededError(
            "Memory limit exceeded",
            plugin_name="test_plugin",
            resource_type="memory",
            current_value=150.0,
            limit=100.0
        )
        
        assert str(error) == "Memory limit exceeded"
        assert error.plugin_name == "test_plugin"
        assert error.resource_type == "memory"
        assert error.current_value == 150.0
        assert error.limit == 100.0


@pytest.mark.asyncio
class TestPluginLifecycleDataClasses:
    """Test data classes used in lifecycle management."""
    
    def test_restart_attempt(self):
        """Test RestartAttempt dataclass."""
        timestamp = datetime.now()
        attempt = RestartAttempt(
            timestamp=timestamp,
            attempt_number=1,
            reason="Test restart",
            success=True,
            error=None
        )
        
        assert attempt.timestamp == timestamp
        assert attempt.attempt_number == 1
        assert attempt.reason == "Test restart"
        assert attempt.success is True
        assert attempt.error is None
    
    def test_plugin_resource_usage(self):
        """Test PluginResourceUsage dataclass."""
        usage = PluginResourceUsage(
            memory_mb=50.5,
            cpu_percent=25.0,
            uptime_seconds=3600.0
        )
        
        assert usage.memory_mb == 50.5
        assert usage.cpu_percent == 25.0
        assert usage.uptime_seconds == 3600.0
        assert isinstance(usage.last_updated, datetime)
    
    def test_state_transition_record(self):
        """Test StateTransitionRecord dataclass."""
        timestamp = datetime.now()
        record = StateTransitionRecord(
            timestamp=timestamp,
            plugin_name="test_plugin",
            from_state=PluginState.UNLOADED,
            to_state=PluginState.LOADING,
            success=True,
            duration_ms=150.0,
            error=None
        )
        
        assert record.timestamp == timestamp
        assert record.plugin_name == "test_plugin"
        assert record.from_state == PluginState.UNLOADED
        assert record.to_state == PluginState.LOADING
        assert record.success is True
        assert record.duration_ms == 150.0
        assert record.error is None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
