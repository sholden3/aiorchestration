"""
Simplified test for plugin base interface system.
Tests just the plugin base module without importing the entire governance package.
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


class TestValidatorPlugin(BaseValidatorPlugin):
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


class TestBaseValidatorPlugin:
    """Test BaseValidatorPlugin implementation."""
    
    def test_plugin_creation(self):
        """Test plugin creation with metadata."""
        plugin = TestValidatorPlugin()
        
        assert plugin.metadata.name == "test-validator"
        assert plugin.state == PluginState.UNLOADED
        assert plugin.validation_mode == ValidationMode.ASYNC
    
    def test_health_property(self):
        """Test health property returns current status."""
        plugin = TestValidatorPlugin()
        health = plugin.health
        
        assert health.state == PluginState.UNLOADED
        assert health.healthy is False  # Not ready yet
        assert health.error_count == 0
        assert health.uptime_seconds == 0.0
    
    @pytest.mark.asyncio
    async def test_initialize_success(self):
        """Test successful plugin initialization."""
        plugin = TestValidatorPlugin()
        config = {"validation_mode": "async", "test_param": "value"}
        
        await plugin.initialize(config)
        
        assert plugin.state == PluginState.READY
        assert plugin.initialize_called
        assert plugin.config["test_param"] == "value"
        assert plugin.validation_mode == ValidationMode.ASYNC
    
    @pytest.mark.asyncio
    async def test_initialize_already_initialized(self):
        """Test initialization when already initialized."""
        plugin = TestValidatorPlugin()
        await plugin.initialize({})
        
        with pytest.raises(RuntimeError, match="already initialized"):
            await plugin.initialize({})
    
    @pytest.mark.asyncio
    async def test_validate_not_ready(self):
        """Test validation when plugin not ready."""
        plugin = TestValidatorPlugin()
        
        result = await plugin.validate({"test": "data"})
        
        assert not result.success
        assert result.severity == ValidationSeverity.ERROR
        assert "not ready" in result.errors[0].lower()
    
    @pytest.mark.asyncio
    async def test_validate_async_mode(self):
        """Test validation in async mode."""
        plugin = TestValidatorPlugin()
        await plugin.initialize({"validation_mode": "async"})
        
        result = await plugin.validate({"test": "data"})
        
        assert result.success
        assert result.plugin_name == "test-validator"
        assert "Async validation passed" in result.messages
        assert result.duration_ms > 0
        assert plugin.validation_calls[0][0] == "async"
    
    @pytest.mark.asyncio
    async def test_validate_sync_mode(self):
        """Test validation in sync mode."""
        plugin = TestValidatorPlugin()
        await plugin.initialize({"validation_mode": "sync"})
        
        result = await plugin.validate({"test": "data"})
        
        assert result.success
        assert "Sync validation passed" in result.messages
        assert plugin.validation_calls[0][0] == "sync"
    
    @pytest.mark.asyncio
    async def test_configure_success(self):
        """Test successful configuration update."""
        plugin = TestValidatorPlugin()
        await plugin.initialize({})
        
        new_config = {"validation_mode": "sync", "new_param": "new_value"}
        await plugin.configure(new_config)
        
        assert plugin.configure_called
        assert plugin.config["new_param"] == "new_value"
        assert plugin.validation_mode == ValidationMode.SYNC
    
    @pytest.mark.asyncio
    async def test_teardown_success(self):
        """Test successful teardown."""
        plugin = TestValidatorPlugin()
        await plugin.initialize({})
        
        await plugin.teardown()
        
        assert plugin.teardown_called
        assert plugin.state == PluginState.STOPPED
    
    @pytest.mark.asyncio
    async def test_event_handling(self):
        """Test event registration and emission."""
        plugin = TestValidatorPlugin()
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
    async def test_full_plugin_lifecycle(self):
        """Test complete plugin lifecycle."""
        plugin = TestValidatorPlugin()
        
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
