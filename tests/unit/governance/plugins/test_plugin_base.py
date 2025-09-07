"""
Test suite for the plugin base interface system.

Tests cover all aspects of the plugin interface including:
- Data model validation
- Plugin lifecycle management
- Configuration handling
- Health monitoring
- Event handling
- Thread safety
"""

import asyncio
import pytest
import time
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

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


class MockValidatorPlugin(BaseValidatorPlugin):
    """Concrete test implementation of BaseValidatorPlugin."""
    
    def __init__(self):
        metadata = PluginMetadata(
            name="test-validator",
            version="1.0.0",
            description="Test validator plugin",
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


class TestBaseValidatorPlugin:
    """Test BaseValidatorPlugin implementation."""
    
    def test_plugin_creation(self):
        """Test plugin creation with metadata."""
        plugin = MockValidatorPlugin()
        
        assert plugin.metadata.name == "test-validator"
        assert plugin.state == PluginState.UNLOADED
        assert plugin.validation_mode == ValidationMode.ASYNC
    
    def test_health_property(self):
        """Test health property returns current status."""
        plugin = MockValidatorPlugin()
        health = plugin.health
        
        assert health.state == PluginState.UNLOADED
        assert health.healthy is False  # Not ready yet
        assert health.error_count == 0
        assert health.uptime_seconds == 0.0
    
    def test_config_property_thread_safe(self):
        """Test config property returns copy."""
        plugin = MockValidatorPlugin()
        config1 = plugin.config
        config2 = plugin.config
        
        # Should be equal but different objects
        assert config1 == config2
        assert config1 is not config2
    
    @pytest.mark.asyncio
    async def test_initialize_success(self):
        """Test successful plugin initialization."""
        plugin = MockValidatorPlugin()
        config = {"validation_mode": "async", "test_param": "value"}
        
        await plugin.initialize(config)
        
        assert plugin.state == PluginState.READY
        assert plugin.initialize_called
        assert plugin.config["test_param"] == "value"
        assert plugin.validation_mode == ValidationMode.ASYNC
    
    @pytest.mark.asyncio
    async def test_initialize_with_sync_mode(self):
        """Test initialization with sync validation mode."""
        plugin = MockValidatorPlugin()
        config = {"validation_mode": "sync"}
        
        await plugin.initialize(config)
        
        assert plugin.validation_mode == ValidationMode.SYNC
    
    @pytest.mark.asyncio
    async def test_initialize_already_initialized(self):
        """Test initialization when already initialized."""
        plugin = MockValidatorPlugin()
        await plugin.initialize({})
        
        with pytest.raises(RuntimeError, match="already initialized"):
            await plugin.initialize({})
    
    @pytest.mark.asyncio
    async def test_initialize_failure(self):
        """Test initialization failure handling."""
        plugin = MockValidatorPlugin()
        
        with pytest.raises(RuntimeError, match="Initialization failed"):
            await plugin.initialize({"fail_init": True})
        
        assert plugin.state == PluginState.ERROR
        assert plugin.health.error_count == 1
    
    @pytest.mark.asyncio
    async def test_validate_not_ready(self):
        """Test validation when plugin not ready."""
        plugin = MockValidatorPlugin()
        
        result = await plugin.validate({"test": "data"})
        
        assert not result.success
        assert result.severity == ValidationSeverity.ERROR
        assert "not ready" in result.errors[0].lower()
    
    @pytest.mark.asyncio
    async def test_validate_async_mode(self):
        """Test validation in async mode with proper timing handling."""
        plugin = MockValidatorPlugin()
        await plugin.initialize({"validation_mode": "async"})
        
        result = await plugin.validate({"test": "data"})
        
        assert result.success
        assert result.plugin_name == "test-validator"
        assert "Async validation passed" in result.messages
        # Fix: Accept 0.0 as valid for very fast operations
        assert result.duration_ms >= 0, "Duration should be non-negative"
        assert plugin.validation_calls[0][0] == "async"
    
    @pytest.mark.asyncio
    async def test_validate_sync_mode(self):
        """Test validation in sync mode."""
        plugin = MockValidatorPlugin()
        await plugin.initialize({"validation_mode": "sync"})
        
        result = await plugin.validate({"test": "data"})
        
        assert result.success
        assert "Sync validation passed" in result.messages
        assert plugin.validation_calls[0][0] == "sync"
    
    @pytest.mark.asyncio
    async def test_validate_failure(self):
        """Test validation failure handling."""
        plugin = MockValidatorPlugin()
        await plugin.initialize({})
        
        result = await plugin.validate({"fail": True})
        
        assert not result.success
        assert result.severity == ValidationSeverity.ERROR
        assert "Validation failed" in result.errors[0]
        assert plugin.health.error_count == 1
    
    @pytest.mark.asyncio
    async def test_configure_success(self):
        """Test successful configuration update."""
        plugin = MockValidatorPlugin()
        await plugin.initialize({})
        
        new_config = {"validation_mode": "sync", "new_param": "new_value"}
        await plugin.configure(new_config)
        
        assert plugin.configure_called
        assert plugin.config["new_param"] == "new_value"
        assert plugin.validation_mode == ValidationMode.SYNC
    
    @pytest.mark.asyncio
    async def test_configure_failure(self):
        """Test configuration failure handling."""
        plugin = MockValidatorPlugin()
        await plugin.initialize({})
        
        with pytest.raises(ValueError, match="Configuration failed"):
            await plugin.configure({"fail_configure": True})
    
    @pytest.mark.asyncio
    async def test_configure_invalid_validation_mode(self):
        """Test configuration with invalid validation mode."""
        plugin = MockValidatorPlugin()
        await plugin.initialize({})
        
        with pytest.raises(ValueError, match="Invalid validation_mode"):
            await plugin.configure({"validation_mode": "invalid"})
    
    @pytest.mark.asyncio
    async def test_teardown_success(self):
        """Test successful teardown."""
        plugin = MockValidatorPlugin()
        await plugin.initialize({})
        
        await plugin.teardown()
        
        assert plugin.teardown_called
        assert plugin.state == PluginState.STOPPED
    
    @pytest.mark.asyncio
    async def test_teardown_already_stopped(self):
        """Test teardown when already stopped."""
        plugin = MockValidatorPlugin()
        await plugin.initialize({})
        await plugin.teardown()
        
        # Should not raise error
        await plugin.teardown()
        assert plugin.state == PluginState.STOPPED
    
    @pytest.mark.asyncio
    async def test_event_handling(self):
        """Test event registration and emission."""
        plugin = MockValidatorPlugin()
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
    
    def test_event_handler_unregistration(self):
        """Test event handler unregistration."""
        plugin = MockValidatorPlugin()
        
        def handler(event, data):
            pass
        
        plugin.register_event_handler('test', handler)
        assert 'test' in plugin._event_handlers
        
        plugin.unregister_event_handler('test', handler)
        assert 'test' not in plugin._event_handlers
    
    def test_event_handler_unregister_nonexistent(self):
        """Test unregistering nonexistent handler doesn't error."""
        plugin = MockValidatorPlugin()
        
        def handler(event, data):
            pass
        
        # Should not raise error
        plugin.unregister_event_handler('nonexistent', handler)
    
    @pytest.mark.asyncio
    async def test_validate_config_non_dict(self):
        """Test configuration validation with non-dict input."""
        plugin = MockValidatorPlugin()
        
        with pytest.raises(ValueError, match="Configuration must be a dictionary"):
            await plugin._validate_config("not a dict")
    
    def test_collect_metrics(self):
        """Test metrics collection."""
        plugin = MockValidatorPlugin()
        
        def handler(event, data):
            pass
        
        plugin.register_event_handler('test_event', handler)
        
        metrics = plugin._collect_metrics()
        
        assert metrics['validation_mode'] == 'async'
        assert metrics['config_keys'] == []
        assert metrics['event_handlers']['test_event'] == 1
    
    @pytest.mark.asyncio
    async def test_full_plugin_lifecycle(self):
        """Test complete plugin lifecycle."""
        plugin = MockValidatorPlugin()
        
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
