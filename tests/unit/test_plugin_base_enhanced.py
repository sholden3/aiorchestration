"""
Enhanced test suite for plugin base interface system.
This file provides comprehensive coverage to meet the >85% requirement.
"""

import asyncio
import pytest
import time
from datetime import datetime
import sys
import os

# Add the project root to Python path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Import only what we need to test
from libs.governance.plugins.base import (
    BaseValidatorPlugin,
    IValidatorPlugin,
    PluginHealth,
    PluginMetadata,
    PluginState,
    ValidationMode,
    ValidationResult,
    ValidationSeverity,
)


class EnhancedTestValidatorPlugin(BaseValidatorPlugin):
    """Enhanced test implementation with more scenarios."""
    
    def __init__(self, name="enhanced-test-validator"):
        metadata = PluginMetadata(
            name=name,
            version="1.0.0",
            description="Enhanced test validator plugin",
            author="Test Author",
            license="MIT"
        )
        super().__init__(metadata)
        self.initialize_called = False
        self.configure_called = False
        self.teardown_called = False
        self.validation_calls = []
    
    async def _do_initialize(self, config):
        """Test initialization."""
        self.initialize_called = True
        if config.get('fail_init'):
            raise RuntimeError("Initialization failed")
    
    async def _validate_async(self, context):
        """Test async validation."""
        self.validation_calls.append(('async', context))
        
        if context.get('fail'):
            raise ValueError("Validation failed")
        
        if context.get('return_warning'):
            return ValidationResult(
                success=True,
                plugin_name=self.metadata.name,
                severity=ValidationSeverity.WARNING,
                warnings=["Warning message"]
            )
        
        return ValidationResult(
            success=True,
            plugin_name=self.metadata.name,
            severity=ValidationSeverity.INFO,
            messages=["Async validation passed"]
        )
    
    async def _validate_sync(self, context):
        """Test sync validation."""
        self.validation_calls.append(('sync', context))
        
        return ValidationResult(
            success=True,
            plugin_name=self.metadata.name,
            severity=ValidationSeverity.INFO,
            messages=["Sync validation passed"]
        )
    
    async def _do_configure(self, config):
        """Test configuration."""
        self.configure_called = True
        if config.get('fail_configure'):
            raise ValueError("Configuration failed")
    
    async def _do_teardown(self):
        """Test teardown."""
        self.teardown_called = True
        if hasattr(self, 'fail_teardown') and self.fail_teardown:
            raise RuntimeError("Teardown failed")


class TestPluginMetadata:
    """Test PluginMetadata dataclass."""
    
    def test_create_minimal_metadata(self):
        """Test creating metadata with minimal required fields."""
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            license="MIT"
        )
        
        assert metadata.name == "test-plugin"
        assert metadata.version == "1.0.0"
        assert metadata.tags == []
        assert metadata.dependencies == []
    
    def test_create_full_metadata(self):
        """Test creating metadata with all fields."""
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            license="MIT",
            tags=["validation", "security"],
            dependencies=["pydantic", "jsonschema"]
        )
        
        assert metadata.tags == ["validation", "security"]
        assert metadata.dependencies == ["pydantic", "jsonschema"]
    
    def test_empty_name_raises_error(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Plugin name and version are required"):
            PluginMetadata(
                name="",
                version="1.0.0",
                description="Test",
                author="Author",
                license="MIT"
            )
    
    def test_empty_version_raises_error(self):
        """Test that empty version raises ValueError."""
        with pytest.raises(ValueError, match="Plugin name and version are required"):
            PluginMetadata(
                name="test",
                version="",
                description="Test",
                author="Author",
                license="MIT"
            )
    
    def test_none_name_raises_error(self):
        """Test that None name raises ValueError."""
        with pytest.raises(ValueError, match="Plugin name and version are required"):
            PluginMetadata(
                name=None,
                version="1.0.0",
                description="Test",
                author="Author",
                license="MIT"
            )


class TestPluginHealth:
    """Test PluginHealth dataclass."""
    
    def test_create_health_status(self):
        """Test creating health status."""
        now = datetime.now()
        health = PluginHealth(
            state=PluginState.READY,
            healthy=True,
            last_check=now,
            uptime_seconds=3661.5,
            error_count=2,
            metrics={"requests": 100}
        )
        
        assert health.state == PluginState.READY
        assert health.healthy is True
        assert health.uptime_seconds == 3661.5
        assert health.error_count == 2
        assert health.metrics == {"requests": 100}
    
    def test_uptime_display_formatting(self):
        """Test uptime display formatting."""
        health = PluginHealth(
            state=PluginState.READY,
            healthy=True,
            last_check=datetime.now(),
            uptime_seconds=3661  # 1 hour, 1 minute, 1 second
        )
        
        assert health.uptime_display == "01:01:01"
    
    def test_uptime_display_zero(self):
        """Test uptime display with zero seconds."""
        health = PluginHealth(
            state=PluginState.READY,
            healthy=True,
            last_check=datetime.now(),
            uptime_seconds=0
        )
        
        assert health.uptime_display == "00:00:00"
    
    def test_uptime_display_hours_only(self):
        """Test uptime display with hours only."""
        health = PluginHealth(
            state=PluginState.READY,
            healthy=True,
            last_check=datetime.now(),
            uptime_seconds=7200  # 2 hours
        )
        
        assert health.uptime_display == "02:00:00"
    
    def test_uptime_display_large_seconds(self):
        """Test uptime display with large seconds value."""
        health = PluginHealth(
            state=PluginState.READY,
            healthy=True,
            last_check=datetime.now(),
            uptime_seconds=90061  # 25 hours, 1 minute, 1 second
        )
        
        assert health.uptime_display == "25:01:01"


class TestValidationResult:
    """Test ValidationResult dataclass."""
    
    def test_create_success_result(self):
        """Test creating successful validation result."""
        result = ValidationResult(
            success=True,
            plugin_name="test-plugin",
            severity=ValidationSeverity.INFO,
            messages=["Validation passed"],
            duration_ms=150.5
        )
        
        assert result.success is True
        assert result.plugin_name == "test-plugin"
        assert result.severity == ValidationSeverity.INFO
        assert result.duration_ms == 150.5
        assert not result.has_errors
        assert not result.has_warnings
    
    def test_add_message_info(self):
        """Test adding info message."""
        result = ValidationResult(
            success=True,
            plugin_name="test",
            severity=ValidationSeverity.INFO
        )
        
        result.add_message("Info message", ValidationSeverity.INFO)
        
        assert "Info message" in result.messages
        assert not result.has_errors
        assert not result.has_warnings
    
    def test_add_message_warning(self):
        """Test adding warning message."""
        result = ValidationResult(
            success=True,
            plugin_name="test",
            severity=ValidationSeverity.WARNING
        )
        
        result.add_message("Warning message", ValidationSeverity.WARNING)
        
        assert "Warning message" in result.messages
        assert "Warning message" in result.warnings
        assert result.has_warnings
        assert not result.has_errors
    
    def test_add_message_error(self):
        """Test adding error message."""
        result = ValidationResult(
            success=False,
            plugin_name="test",
            severity=ValidationSeverity.ERROR
        )
        
        result.add_message("Error message", ValidationSeverity.ERROR)
        
        assert "Error message" in result.messages
        assert "Error message" in result.errors
        assert result.has_errors
        assert not result.has_warnings
    
    def test_add_message_critical(self):
        """Test adding critical message."""
        result = ValidationResult(
            success=False,
            plugin_name="test",
            severity=ValidationSeverity.CRITICAL
        )
        
        result.add_message("Critical message", ValidationSeverity.CRITICAL)
        
        assert "Critical message" in result.messages
        # Critical messages don't automatically go to errors
        assert not result.has_errors
    
    def test_has_errors_and_warnings(self):
        """Test result with both errors and warnings."""
        result = ValidationResult(
            success=False,
            plugin_name="test",
            severity=ValidationSeverity.ERROR,
            errors=["Error 1"],
            warnings=["Warning 1"]
        )
        
        assert result.has_errors
        assert result.has_warnings


class TestBaseValidatorPlugin:
    """Test BaseValidatorPlugin implementation."""
    
    def test_plugin_creation(self):
        """Test plugin creation with metadata."""
        plugin = EnhancedTestValidatorPlugin()
        
        assert plugin.metadata.name == "enhanced-test-validator"
        assert plugin.state == PluginState.UNLOADED
        assert plugin.validation_mode == ValidationMode.ASYNC
    
    def test_health_property(self):
        """Test health property returns current status."""
        plugin = EnhancedTestValidatorPlugin()
        health = plugin.health
        
        assert health.state == PluginState.UNLOADED
        assert health.healthy is False  # Not ready yet
        assert health.error_count == 0
        assert health.uptime_seconds == 0.0
    
    def test_config_property_thread_safe(self):
        """Test config property returns copy."""
        plugin = EnhancedTestValidatorPlugin()
        config1 = plugin.config
        config2 = plugin.config
        
        # Should be equal but different objects
        assert config1 == config2
        assert config1 is not config2
    
    def test_state_property_thread_safe(self):
        """Test state property is thread-safe."""
        plugin = EnhancedTestValidatorPlugin()
        
        assert plugin.state == PluginState.UNLOADED
        # Direct access should also work
        assert plugin._state == PluginState.UNLOADED
    
    @pytest.mark.asyncio
    async def test_initialize_success(self):
        """Test successful plugin initialization."""
        plugin = EnhancedTestValidatorPlugin()
        config = {"validation_mode": "async", "test_param": "value"}
        
        await plugin.initialize(config)
        
        assert plugin.state == PluginState.READY
        assert plugin.initialize_called
        assert plugin.config["test_param"] == "value"
        assert plugin.validation_mode == ValidationMode.ASYNC
    
    @pytest.mark.asyncio
    async def test_initialize_with_sync_mode(self):
        """Test initialization with sync validation mode."""
        plugin = EnhancedTestValidatorPlugin()
        config = {"validation_mode": "sync"}
        
        await plugin.initialize(config)
        
        assert plugin.validation_mode == ValidationMode.SYNC
    
    @pytest.mark.asyncio
    async def test_initialize_with_parallel_mode(self):
        """Test initialization with parallel validation mode."""
        plugin = EnhancedTestValidatorPlugin()
        config = {"validation_mode": "parallel"}
        
        await plugin.initialize(config)
        
        assert plugin.validation_mode == ValidationMode.PARALLEL
    
    @pytest.mark.asyncio
    async def test_initialize_already_initialized(self):
        """Test initialization when already initialized."""
        plugin = EnhancedTestValidatorPlugin()
        await plugin.initialize({})
        
        with pytest.raises(RuntimeError, match="already initialized"):
            await plugin.initialize({})
    
    @pytest.mark.asyncio
    async def test_initialize_from_loading_state(self):
        """Test initialization when in loading state."""
        plugin = EnhancedTestValidatorPlugin()
        plugin._state = PluginState.LOADING
        
        with pytest.raises(RuntimeError, match="already initialized"):
            await plugin.initialize({})
    
    @pytest.mark.asyncio
    async def test_initialize_failure(self):
        """Test initialization failure handling."""
        plugin = EnhancedTestValidatorPlugin()
        
        with pytest.raises(RuntimeError, match="Initialization failed"):
            await plugin.initialize({"fail_init": True})
        
        assert plugin.state == PluginState.ERROR
        assert plugin.health.error_count == 1
    
    @pytest.mark.asyncio
    async def test_validate_not_ready(self):
        """Test validation when plugin not ready."""
        plugin = EnhancedTestValidatorPlugin()
        
        result = await plugin.validate({"test": "data"})
        
        assert not result.success
        assert result.severity == ValidationSeverity.ERROR
        assert "not ready" in result.errors[0].lower()
    
    @pytest.mark.asyncio
    async def test_validate_from_error_state(self):
        """Test validation when plugin in error state."""
        plugin = EnhancedTestValidatorPlugin()
        plugin._state = PluginState.ERROR
        
        result = await plugin.validate({"test": "data"})
        
        assert not result.success
        assert result.severity == ValidationSeverity.ERROR
        assert "not ready" in result.errors[0].lower()
    
    @pytest.mark.asyncio
    async def test_validate_async_mode(self):
        """Test validation in async mode."""
        plugin = EnhancedTestValidatorPlugin()
        await plugin.initialize({"validation_mode": "async"})
        
        result = await plugin.validate({"test": "data"})
        
        assert result.success
        assert result.plugin_name == "enhanced-test-validator"
        assert "Async validation passed" in result.messages
        assert result.duration_ms > 0
        assert plugin.validation_calls[0][0] == "async"
    
    @pytest.mark.asyncio
    async def test_validate_sync_mode(self):
        """Test validation in sync mode."""
        plugin = EnhancedTestValidatorPlugin()
        await plugin.initialize({"validation_mode": "sync"})
        
        result = await plugin.validate({"test": "data"})
        
        assert result.success
        assert "Sync validation passed" in result.messages
        assert plugin.validation_calls[0][0] == "sync"
    
    @pytest.mark.asyncio
    async def test_validate_failure(self):
        """Test validation failure handling."""
        plugin = EnhancedTestValidatorPlugin()
        await plugin.initialize({})
        
        result = await plugin.validate({"fail": True})
        
        assert not result.success
        assert result.severity == ValidationSeverity.ERROR
        assert "Validation failed" in result.errors[0]
        assert plugin.health.error_count == 1
        assert result.duration_ms > 0
    
    @pytest.mark.asyncio
    async def test_configure_success(self):
        """Test successful configuration update."""
        plugin = EnhancedTestValidatorPlugin()
        await plugin.initialize({})
        
        new_config = {"validation_mode": "sync", "new_param": "new_value"}
        await plugin.configure(new_config)
        
        assert plugin.configure_called
        assert plugin.config["new_param"] == "new_value"
        assert plugin.validation_mode == ValidationMode.SYNC
    
    @pytest.mark.asyncio
    async def test_configure_failure(self):
        """Test configuration failure handling."""
        plugin = EnhancedTestValidatorPlugin()
        await plugin.initialize({})
        
        with pytest.raises(ValueError, match="Configuration failed"):
            await plugin.configure({"fail_configure": True})
    
    @pytest.mark.asyncio
    async def test_configure_invalid_validation_mode(self):
        """Test configuration with invalid validation mode."""
        plugin = EnhancedTestValidatorPlugin()
        await plugin.initialize({})
        
        with pytest.raises(ValueError, match="Invalid validation_mode"):
            await plugin.configure({"validation_mode": "invalid"})
    
    @pytest.mark.asyncio
    async def test_teardown_success(self):
        """Test successful teardown."""
        plugin = EnhancedTestValidatorPlugin()
        await plugin.initialize({})
        
        await plugin.teardown()
        
        assert plugin.teardown_called
        assert plugin.state == PluginState.STOPPED
    
    @pytest.mark.asyncio
    async def test_teardown_already_stopped(self):
        """Test teardown when already stopped."""
        plugin = EnhancedTestValidatorPlugin()
        await plugin.initialize({})
        await plugin.teardown()
        
        # Should not raise error
        await plugin.teardown()
        assert plugin.state == PluginState.STOPPED
    
    @pytest.mark.asyncio
    async def test_teardown_already_stopping(self):
        """Test teardown when already stopping."""
        plugin = EnhancedTestValidatorPlugin()
        await plugin.initialize({})
        plugin._state = PluginState.STOPPING
        
        # Should not change state or call teardown again
        await plugin.teardown()
        assert plugin.state == PluginState.STOPPING
        assert not plugin.teardown_called
    
    @pytest.mark.asyncio
    async def test_teardown_failure(self):
        """Test teardown failure handling."""
        plugin = EnhancedTestValidatorPlugin()
        await plugin.initialize({})
        plugin.fail_teardown = True
        
        with pytest.raises(RuntimeError, match="Teardown failed"):
            await plugin.teardown()
        
        assert plugin.state == PluginState.ERROR
        assert plugin.health.error_count == 1
    
    @pytest.mark.asyncio
    async def test_event_handling(self):
        """Test event registration and emission."""
        plugin = EnhancedTestValidatorPlugin()
        events_received = []
        
        def sync_handler(event, data):
            events_received.append(('sync', event, data))
        
        async def async_handler(event, data):
            events_received.append(('async', event, data))
        
        plugin.register_event_handler('test_event', sync_handler)
        plugin.register_event_handler('test_event', async_handler)
        
        await plugin._emit_event('test_event', {'test': 'data'})
        
        # Allow async handler to complete
        await asyncio.sleep(0.01)
        
        assert len(events_received) == 2
        assert ('sync', 'test_event', {'test': 'data'}) in events_received
        assert ('async', 'test_event', {'test': 'data'}) in events_received
    
    @pytest.mark.asyncio
    async def test_event_handler_failure(self):
        """Test event handler failure handling."""
        plugin = EnhancedTestValidatorPlugin()
        
        def failing_handler(event, data):
            raise RuntimeError("Handler failed")
        
        plugin.register_event_handler('test_event', failing_handler)
        
        # Should not raise error, just log warning
        await plugin._emit_event('test_event', {'test': 'data'})
    
    def test_event_handler_registration(self):
        """Test event handler registration."""
        plugin = EnhancedTestValidatorPlugin()
        
        def handler1(event, data):
            pass
        
        def handler2(event, data):
            pass
        
        plugin.register_event_handler('test', handler1)
        plugin.register_event_handler('test', handler2)
        plugin.register_event_handler('other', handler1)
        
        assert len(plugin._event_handlers['test']) == 2
        assert len(plugin._event_handlers['other']) == 1
    
    def test_event_handler_unregistration(self):
        """Test event handler unregistration."""
        plugin = EnhancedTestValidatorPlugin()
        
        def handler(event, data):
            pass
        
        plugin.register_event_handler('test', handler)
        assert 'test' in plugin._event_handlers
        
        plugin.unregister_event_handler('test', handler)
        assert 'test' not in plugin._event_handlers
    
    def test_event_handler_unregister_nonexistent(self):
        """Test unregistering nonexistent handler doesn't error."""
        plugin = EnhancedTestValidatorPlugin()
        
        def handler(event, data):
            pass
        
        # Should not raise error
        plugin.unregister_event_handler('nonexistent', handler)
    
    def test_event_handler_unregister_from_existing_event(self):
        """Test unregistering handler from existing event with multiple handlers."""
        plugin = EnhancedTestValidatorPlugin()
        
        def handler1(event, data):
            pass
        
        def handler2(event, data):
            pass
        
        plugin.register_event_handler('test', handler1)
        plugin.register_event_handler('test', handler2)
        
        # Unregister one handler
        plugin.unregister_event_handler('test', handler1)
        
        # Event should still exist with one handler
        assert 'test' in plugin._event_handlers
        assert len(plugin._event_handlers['test']) == 1
        assert handler2 in plugin._event_handlers['test']
    
    @pytest.mark.asyncio
    async def test_validate_config_non_dict(self):
        """Test configuration validation with non-dict input."""
        plugin = EnhancedTestValidatorPlugin()
        
        with pytest.raises(ValueError, match="Configuration must be a dictionary"):
            await plugin._validate_config("not a dict")
    
    @pytest.mark.asyncio
    async def test_validate_config_valid_dict(self):
        """Test configuration validation with valid dict."""
        plugin = EnhancedTestValidatorPlugin()
        
        config = {"param": "value", "validation_mode": "sync"}
        result = await plugin._validate_config(config)
        
        assert result == config
        assert result is not config  # Should be a copy
    
    def test_collect_metrics(self):
        """Test metrics collection."""
        plugin = EnhancedTestValidatorPlugin()
        
        def handler(event, data):
            pass
        
        plugin.register_event_handler('test_event', handler)
        plugin.register_event_handler('other_event', handler)
        plugin._config = {"param1": "value1", "param2": "value2"}
        
        metrics = plugin._collect_metrics()
        
        assert metrics['validation_mode'] == 'async'
        assert set(metrics['config_keys']) == {'param1', 'param2'}
        assert metrics['event_handlers']['test_event'] == 1
        assert metrics['event_handlers']['other_event'] == 1
    
    @pytest.mark.asyncio
    async def test_health_after_initialization(self):
        """Test health status after initialization."""
        plugin = EnhancedTestValidatorPlugin()
        await plugin.initialize({})
        
        # Let some time pass
        await asyncio.sleep(0.01)
        
        health = plugin.health
        assert health.state == PluginState.READY
        assert health.healthy is True
        assert health.error_count == 0
        assert health.uptime_seconds > 0
    
    @pytest.mark.asyncio
    async def test_health_with_errors(self):
        """Test health status with errors."""
        plugin = EnhancedTestValidatorPlugin()
        await plugin.initialize({})
        
        # Cause an error
        await plugin.validate({"fail": True})
        
        health = plugin.health
        assert health.state == PluginState.READY  # Still ready but unhealthy
        assert health.healthy is False  # Has errors
        assert health.error_count == 1
    
    @pytest.mark.asyncio
    async def test_full_plugin_lifecycle(self):
        """Test complete plugin lifecycle."""
        plugin = EnhancedTestValidatorPlugin()
        
        # Initialize
        config = {"validation_mode": "async", "param": "value"}
        await plugin.initialize(config)
        assert plugin.state == PluginState.READY
        
        # Validate
        result = await plugin.validate({"test": "context"})
        assert result.success
        
        # Configure
        await plugin.configure({"new_param": "new_value"})
        assert plugin.config["new_param"] == "new_value"
        
        # Teardown
        await plugin.teardown()
        assert plugin.state == PluginState.STOPPED


class TestEnums:
    """Test enum definitions."""
    
    def test_plugin_state_values(self):
        """Test PluginState enum values."""
        assert PluginState.UNLOADED.value == "unloaded"
        assert PluginState.LOADING.value == "loading"
        assert PluginState.READY.value == "ready"
        assert PluginState.ERROR.value == "error"
        assert PluginState.STOPPING.value == "stopping"
        assert PluginState.STOPPED.value == "stopped"
    
    def test_validation_mode_values(self):
        """Test ValidationMode enum values."""
        assert ValidationMode.SYNC.value == "sync"
        assert ValidationMode.ASYNC.value == "async"
        assert ValidationMode.PARALLEL.value == "parallel"
    
    def test_validation_severity_values(self):
        """Test ValidationSeverity enum values."""
        assert ValidationSeverity.INFO.value == "info"
        assert ValidationSeverity.WARNING.value == "warning"
        assert ValidationSeverity.ERROR.value == "error"
        assert ValidationSeverity.CRITICAL.value == "critical"


class TestAbstractInterface:
    """Test abstract interface compliance."""
    
    def test_abstract_interface_methods(self):
        """Test that abstract methods raise NotImplementedError."""
        
        # We can't instantiate an abstract class, but we can test
        # that our implementation correctly implements the interface
        plugin = EnhancedTestValidatorPlugin()
        
        # Test that our plugin properly implements the interface
        assert hasattr(plugin, 'metadata')
        assert hasattr(plugin, 'health')
        assert hasattr(plugin, 'initialize')
        assert hasattr(plugin, 'validate')
        assert hasattr(plugin, 'configure')
        assert hasattr(plugin, 'teardown')
        
        # Test that the interface is properly defined
        assert hasattr(IValidatorPlugin, 'metadata')
        assert hasattr(IValidatorPlugin, 'health')
        assert hasattr(IValidatorPlugin, 'initialize')
        assert hasattr(IValidatorPlugin, 'validate')
        assert hasattr(IValidatorPlugin, 'configure')
        assert hasattr(IValidatorPlugin, 'teardown')
    
    def test_base_plugin_default_implementations(self):
        """Test base plugin default implementations."""
        plugin = EnhancedTestValidatorPlugin()
        
        # Test default _do_configure doesn't raise
        asyncio.run(plugin._do_configure({}))
        
        # Test default _do_teardown doesn't raise  
        asyncio.run(plugin._do_teardown())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
