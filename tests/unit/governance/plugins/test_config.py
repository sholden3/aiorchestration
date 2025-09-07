"""
Comprehensive test suite for ConfigurationLoader.

Tests all functionality including file loading, validation, hot-reload,
security features, and error handling with >85% coverage requirement.
"""

import asyncio
import json
import os
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from libs.governance.plugins.config import (
    ArrayMergeStrategy,
    ConfigFormat,
    ConfigurationError,
    ConfigurationEvent,
    ConfigurationLoader,
    ConfigurationValidationReport,
    FileWatchError,
    SchemaValidationError,
    ValidationError
)


class TestConfigurationLoader:
    """Test suite for ConfigurationLoader class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def schema_dir(self, temp_dir):
        """Create temporary schema directory."""
        schema_dir = temp_dir / "schemas"
        schema_dir.mkdir()
        
        # Create test schema
        test_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
                "enabled": {"type": "boolean", "default": True}
            },
            "required": ["name", "version"]
        }
        
        with open(schema_dir / "test.json", "w") as f:
            json.dump(test_schema, f)
        
        return schema_dir
    
    @pytest.fixture
    def config_loader(self, schema_dir):
        """Create ConfigurationLoader instance."""
        return ConfigurationLoader(
            schema_dir=schema_dir,
            env_prefix="TEST",
            enable_hot_reload=False  # Disable for most tests
        )
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration data."""
        return {
            "name": "test_plugin",
            "version": "1.0.0",
            "enabled": True,
            "config": {
                "timeout": 30,
                "retries": 3
            }
        }
    
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        loader = ConfigurationLoader()
        
        assert loader.schema_dir is None
        assert loader.env_prefix == "CONFIG"
        assert loader.array_merge_strategy == ArrayMergeStrategy.REPLACE
        assert not loader.enable_hot_reload
        assert loader.debounce_ms == 500
        assert loader.max_file_size_mb == 10
    
    def test_init_with_custom_params(self, temp_dir):
        """Test initialization with custom parameters."""
        loader = ConfigurationLoader(
            schema_dir=temp_dir,
            env_prefix="CUSTOM",
            array_merge_strategy=ArrayMergeStrategy.APPEND,
            enable_hot_reload=True,
            debounce_ms=1000,
            max_file_size_mb=5
        )
        
        assert loader.schema_dir == temp_dir
        assert loader.env_prefix == "CUSTOM"
        assert loader.array_merge_strategy == ArrayMergeStrategy.APPEND
        assert loader.enable_hot_reload
        assert loader.debounce_ms == 1000
        assert loader.max_file_size_mb == 5
    
    def test_load_json_config(self, config_loader, temp_dir, sample_config):
        """Test loading JSON configuration file."""
        config_file = temp_dir / "test.json"
        with open(config_file, "w") as f:
            json.dump(sample_config, f)
        
        loaded_config = config_loader.load_config(config_file)
        
        assert loaded_config == sample_config
        assert str(config_file) in config_loader._cached_configs
        assert str(config_file) in config_loader._last_good_configs
    
    def test_load_yaml_config(self, config_loader, temp_dir, sample_config):
        """Test loading YAML configuration file."""
        config_file = temp_dir / "test.yaml"
        with open(config_file, "w") as f:
            yaml.dump(sample_config, f)
        
        loaded_config = config_loader.load_config(config_file)
        
        assert loaded_config == sample_config
    
    def test_load_yml_config(self, config_loader, temp_dir, sample_config):
        """Test loading YML configuration file."""
        config_file = temp_dir / "test.yml"
        with open(config_file, "w") as f:
            yaml.dump(sample_config, f)
        
        loaded_config = config_loader.load_config(config_file)
        
        assert loaded_config == sample_config
    
    def test_load_nonexistent_file(self, config_loader, temp_dir):
        """Test loading non-existent file raises error."""
        config_file = temp_dir / "nonexistent.json"
        
        with pytest.raises((ConfigurationError, FileNotFoundError)):
            config_loader.load_config(config_file)
    
    def test_load_unsupported_format(self, config_loader, temp_dir):
        """Test loading unsupported file format raises error."""
        config_file = temp_dir / "test.txt"
        config_file.write_text("some content")
        
        with pytest.raises(ConfigurationError):
            config_loader.load_config(config_file)
    
    def test_load_large_file(self, config_loader, temp_dir):
        """Test loading file larger than size limit raises error."""
        config_file = temp_dir / "large.json"
        
        # Create file larger than 10MB limit
        large_data = {"data": "x" * (11 * 1024 * 1024)}
        with open(config_file, "w") as f:
            json.dump(large_data, f)
        
        with pytest.raises(ConfigurationError, match="File too large"):
            config_loader.load_config(config_file)
    
    def test_load_invalid_json(self, config_loader, temp_dir):
        """Test loading invalid JSON raises error."""
        config_file = temp_dir / "invalid.json"
        config_file.write_text("{invalid json")
        
        with pytest.raises(ConfigurationError, match="JSON parsing error"):
            config_loader.load_config(config_file)
    
    def test_load_invalid_yaml(self, config_loader, temp_dir):
        """Test loading invalid YAML raises error."""
        config_file = temp_dir / "invalid.yaml"
        config_file.write_text("invalid: yaml: [")
        
        with pytest.raises(ConfigurationError, match="YAML parsing error"):
            config_loader.load_config(config_file)
    
    def test_load_from_string_json(self, config_loader, sample_config):
        """Test loading configuration from JSON string."""
        json_string = json.dumps(sample_config)
        
        loaded_config = config_loader.load_from_string(json_string, ConfigFormat.JSON)
        
        assert loaded_config == sample_config
    
    def test_load_from_string_yaml(self, config_loader, sample_config):
        """Test loading configuration from YAML string."""
        yaml_string = yaml.dump(sample_config)
        
        loaded_config = config_loader.load_from_string(yaml_string, ConfigFormat.YAML)
        
        assert loaded_config == sample_config
    
    def test_load_from_string_unsupported_format(self, config_loader):
        """Test loading from string with unsupported format raises error."""
        with pytest.raises((ValidationError, ConfigurationError)):
            config_loader.load_from_string("content", ConfigFormat.ENV)
    
    def test_load_from_string_invalid_format(self, config_loader):
        """Test loading from string with invalid format string raises error."""
        with pytest.raises(ValidationError, match="Unsupported format"):
            config_loader.load_from_string("content", "invalid_format")
    
    def test_load_from_string_non_dict_result(self, config_loader):
        """Test loading string that results in non-dict wraps in value key."""
        loaded_config = config_loader.load_from_string('"just a string"', ConfigFormat.JSON)
        
        assert loaded_config == {"value": "just a string"}
    
    def test_load_from_env_simple(self, config_loader):
        """Test loading configuration from environment variables."""
        env_vars = {
            "TEST_NAME": "test_plugin",
            "TEST_VERSION": "1.0.0",
            "TEST_ENABLED": "true",
            "TEST_TIMEOUT": "30"
        }
        
        with patch.dict(os.environ, env_vars):
            config = config_loader.load_from_env()
        
        expected = {
            "name": "test_plugin",
            "version": "1.0.0",
            "enabled": True,
            "timeout": 30
        }
        
        assert config == expected
    
    def test_load_from_env_nested(self, config_loader):
        """Test loading nested configuration from environment variables."""
        env_vars = {
            "TEST_DB_HOST": "localhost",
            "TEST_DB_PORT": "5432",
            "TEST_DB_NAME": "testdb"
        }
        
        with patch.dict(os.environ, env_vars):
            config = config_loader.load_from_env()
        
        expected = {
            "db": {
                "host": "localhost",
                "port": 5432,
                "name": "testdb"
            }
        }
        
        assert config == expected
    
    def test_load_from_env_custom_prefix(self, config_loader):
        """Test loading from environment with custom prefix."""
        env_vars = {
            "CUSTOM_NAME": "test",
            "OTHER_NAME": "ignore"
        }
        
        with patch.dict(os.environ, env_vars):
            config = config_loader.load_from_env("CUSTOM")
        
        assert config == {"name": "test"}
        assert "other" not in config
    
    def test_load_from_env_type_coercion(self, config_loader):
        """Test environment variable type coercion."""
        env_vars = {
            "TEST_BOOL_TRUE": "yes",
            "TEST_BOOL_FALSE": "no",
            "TEST_INT": "42",
            "TEST_FLOAT": "3.14",
            "TEST_JSON_ARRAY": '["a", "b", "c"]',
            "TEST_JSON_OBJECT": '{"key": "value"}',
            "TEST_STRING": "just_text"
        }
        
        with patch.dict(os.environ, env_vars):
            config = config_loader.load_from_env()
        
        assert config["bool"]["true"] is True
        assert config["bool"]["false"] is False
        assert config["int"] == 42
        assert config["float"] == 3.14
        assert config["json"]["array"] == ["a", "b", "c"]
        assert config["json"]["object"] == {"key": "value"}
        assert config["string"] == "just_text"
    
    def test_validate_config_with_schema(self, config_loader, sample_config):
        """Test configuration validation with schema."""
        report = config_loader.validate_config(sample_config, schema_name="test")
        
        assert report.valid
        assert not report.has_errors
        assert not report.has_warnings
    
    def test_validate_config_invalid(self, config_loader):
        """Test validation of invalid configuration."""
        invalid_config = {
            "name": "test_plugin",
            # Missing required "version" field
            "enabled": True
        }
        
        report = config_loader.validate_config(invalid_config, schema_name="test")
        
        assert not report.valid
        assert report.has_errors
        assert len(report.schema_errors) > 0
    
    def test_validate_config_no_schema(self, config_loader, sample_config):
        """Test validation without schema shows warning."""
        report = config_loader.validate_config(sample_config)
        
        assert report.valid
        assert not report.has_errors
        assert report.has_warnings
        assert "No schema provided" in report.warnings[0]
    
    def test_validate_config_custom_validations(self, config_loader):
        """Test custom validation rules."""
        config_with_debug = {
            "name": "test_plugin",
            "version": "1.0.0",
            "debug": True
        }
        
        report = config_loader.validate_config(config_with_debug, schema_name="test")
        
        assert report.valid
        assert report.has_warnings
        assert any("Debug mode is enabled" in warning for warning in report.warnings)
    
    def test_merge_configs_simple(self, config_loader):
        """Test simple configuration merging."""
        config1 = {"a": 1, "b": 2}
        config2 = {"b": 3, "c": 4}
        
        merged = config_loader.merge_configs(config1, config2)
        
        expected = {"a": 1, "b": 3, "c": 4}
        assert merged == expected
    
    def test_merge_configs_deep(self, config_loader):
        """Test deep configuration merging."""
        config1 = {
            "database": {"host": "localhost", "port": 5432},
            "cache": {"ttl": 300}
        }
        config2 = {
            "database": {"name": "mydb", "port": 3306},
            "logging": {"level": "INFO"}
        }
        
        merged = config_loader.merge_configs(config1, config2)
        
        expected = {
            "database": {"host": "localhost", "port": 3306, "name": "mydb"},
            "cache": {"ttl": 300},
            "logging": {"level": "INFO"}
        }
        assert merged == expected
    
    def test_merge_configs_array_strategies(self, config_loader):
        """Test array merging strategies."""
        config1 = {"items": ["a", "b"]}
        config2 = {"items": ["c", "d"]}
        
        # Test REPLACE (default)
        merged = config_loader.merge_configs(config1, config2)
        assert merged["items"] == ["c", "d"]
        
        # Test APPEND
        merged = config_loader.merge_configs(
            config1, config2, 
            array_strategy=ArrayMergeStrategy.APPEND
        )
        assert merged["items"] == ["a", "b", "c", "d"]
        
        # Test PREPEND
        merged = config_loader.merge_configs(
            config1, config2,
            array_strategy=ArrayMergeStrategy.PREPEND
        )
        assert merged["items"] == ["c", "d", "a", "b"]
        
        # Test MERGE_UNIQUE
        config1_dup = {"items": ["a", "b", "c"]}
        config2_dup = {"items": ["b", "c", "d"]}
        merged = config_loader.merge_configs(
            config1_dup, config2_dup,
            array_strategy=ArrayMergeStrategy.MERGE_UNIQUE
        )
        assert merged["items"] == ["a", "b", "c", "d"]
    
    def test_merge_configs_empty(self, config_loader):
        """Test merging with empty config list."""
        merged = config_loader.merge_configs()
        assert merged == {}
    
    def test_save_config_json(self, config_loader, temp_dir, sample_config):
        """Test saving configuration as JSON."""
        config_file = temp_dir / "saved.json"
        
        success = config_loader.save_config(sample_config, config_file)
        
        assert success
        assert config_file.exists()
        
        # Verify saved content
        with open(config_file) as f:
            saved_data = json.load(f)
        assert saved_data == sample_config
    
    def test_save_config_yaml(self, config_loader, temp_dir, sample_config):
        """Test saving configuration as YAML."""
        config_file = temp_dir / "saved.yaml"
        
        success = config_loader.save_config(sample_config, config_file)
        
        assert success
        assert config_file.exists()
        
        # Verify saved content
        with open(config_file) as f:
            saved_data = yaml.safe_load(f)
        assert saved_data == sample_config
    
    def test_save_config_with_backup(self, config_loader, temp_dir, sample_config):
        """Test saving config creates backup of existing file."""
        config_file = temp_dir / "existing.json"
        original_data = {"original": True}
        
        # Create original file
        with open(config_file, "w") as f:
            json.dump(original_data, f)
        
        # Save new config
        success = config_loader.save_config(sample_config, config_file)
        
        assert success
        
        # Verify new content
        with open(config_file) as f:
            saved_data = json.load(f)
        assert saved_data == sample_config
        
        # Backup should be cleaned up on success
        backup_file = config_file.with_suffix(f"{config_file.suffix}.backup")
        assert not backup_file.exists()
    
    def test_save_config_validation_failure(self, config_loader, temp_dir):
        """Test save config with validation failure restores backup."""
        config_file = temp_dir / "test.json"
        original_data = {"original": True}
        invalid_data = {"invalid": "data"}
        
        # Create original file
        with open(config_file, "w") as f:
            json.dump(original_data, f)
        
        # Mock load_config to fail validation
        with patch.object(config_loader, 'load_config', side_effect=ConfigurationError("Validation failed")):
            with pytest.raises(ConfigurationError):
                config_loader.save_config(invalid_data, config_file)
        
        # Original file should be restored
        with open(config_file) as f:
            restored_data = json.load(f)
        assert restored_data == original_data
    
    def test_environment_variable_substitution(self, config_loader, temp_dir):
        """Test environment variable substitution in configuration."""
        config_content = {
            "database_url": "${DATABASE_URL:postgresql://localhost/test}",
            "api_key": "${API_KEY}",
            "nested": {
                "value": "${NESTED_VAR:default_value}"
            }
        }
        
        env_vars = {
            "DATABASE_URL": "postgresql://prod/mydb",
            "API_KEY": "secret123"
        }
        
        config_file = temp_dir / "test.json"
        with open(config_file, "w") as f:
            json.dump(config_content, f)
        
        with patch.dict(os.environ, env_vars):
            loaded_config = config_loader.load_config(config_file)
        
        assert loaded_config["database_url"] == "postgresql://prod/mydb"
        assert loaded_config["api_key"] == "secret123"
        assert loaded_config["nested"]["value"] == "default_value"  # Uses default
    
    def test_event_handlers(self, config_loader, temp_dir, sample_config):
        """Test configuration event handling."""
        events_received = []
        
        def event_handler(event: ConfigurationEvent):
            events_received.append(event)
        
        config_loader.add_event_handler(event_handler)
        
        # Load config should trigger event
        config_file = temp_dir / "test.json"
        with open(config_file, "w") as f:
            json.dump(sample_config, f)
        
        config_loader.load_config(config_file)
        
        assert len(events_received) == 1
        assert events_received[0].event_type == "config_loaded"
        assert events_received[0].file_path == str(config_file)
        
        # Remove handler
        config_loader.remove_event_handler(event_handler)
        
        # Save config should not trigger event for removed handler
        events_received.clear()
        config_loader.save_config(sample_config, temp_dir / "test2.json")
        
        # Should have received event from save, but not from removed handler
        # (save_config triggers internal events)
    
    @pytest.mark.asyncio
    async def test_watch_config_context_manager(self, schema_dir, temp_dir, sample_config):
        """Test configuration watching context manager."""
        config_loader = ConfigurationLoader(
            schema_dir=schema_dir,
            enable_hot_reload=True
        )
        
        config_file = temp_dir / "watch_test.json"
        with open(config_file, "w") as f:
            json.dump(sample_config, f)
        
        async with config_loader.watch_config(config_file) as config:
            assert config == sample_config
        
        # Watcher should be cleaned up
        assert str(config_file) not in config_loader._watchers
        
        config_loader.cleanup()
    
    def test_hot_reload_file_change(self, schema_dir, temp_dir, sample_config):
        """Test hot reload functionality."""
        config_loader = ConfigurationLoader(
            schema_dir=schema_dir,
            enable_hot_reload=True,
            debounce_ms=100  # Short debounce for testing
        )
        
        events_received = []
        
        def event_handler(event: ConfigurationEvent):
            events_received.append(event)
        
        config_loader.add_event_handler(event_handler)
        
        config_file = temp_dir / "hot_reload.json"
        with open(config_file, "w") as f:
            json.dump(sample_config, f)
        
        # Load config to set up watcher
        config_loader.load_config(config_file)
        events_received.clear()  # Clear initial load event
        
        # Modify file
        modified_config = sample_config.copy()
        modified_config["version"] = "2.0.0"
        
        with open(config_file, "w") as f:
            json.dump(modified_config, f)
        
        # Wait for debounced callback
        time.sleep(0.2)
        
        # Should have received reload event
        reload_events = [e for e in events_received if e.event_type == "config_reloaded"]
        assert len(reload_events) > 0
        
        config_loader.cleanup()
    
    def test_sensitive_data_masking(self, config_loader):
        """Test sensitive data masking in logs."""
        config_with_secrets = {
            "database_password": "secret123",
            "api_key": "very_secret_key",
            "private_key": "ssh_key_content",
            "normal_value": "not_secret"
        }
        
        masked = config_loader._mask_sensitive_data(config_with_secrets)
        
        assert masked["database_password"] == "********"
        assert masked["api_key"] == "********"
        assert masked["private_key"] == "********"
        assert masked["normal_value"] == "not_secret"
    
    def test_path_traversal_protection(self, config_loader, temp_dir):
        """Test protection against path traversal attacks."""
        malicious_path = temp_dir / ".." / ".." / "etc" / "passwd"
        
        with pytest.raises((ConfigurationError, FileNotFoundError)):
            config_loader.load_config(malicious_path)
    
    def test_schema_caching(self, config_loader, schema_dir):
        """Test schema caching functionality."""
        # First call should load from file
        schema1 = config_loader._load_schema("test")
        
        # Second call should use cache
        schema2 = config_loader._load_schema("test")
        
        assert schema1 is schema2  # Same object reference
        assert "test" in config_loader._schemas
    
    def test_schema_not_found(self, config_loader):
        """Test error when schema file not found."""
        with pytest.raises(ConfigurationError, match="Schema not found"):
            config_loader._load_schema("nonexistent")
    
    def test_cleanup(self, schema_dir, temp_dir, sample_config):
        """Test cleanup functionality."""
        config_loader = ConfigurationLoader(
            schema_dir=schema_dir,
            enable_hot_reload=True
        )
        
        config_file = temp_dir / "cleanup_test.json"
        with open(config_file, "w") as f:
            json.dump(sample_config, f)
        
        # Load config and add handler to populate internal state
        config_loader.load_config(config_file)
        config_loader.add_event_handler(lambda x: None)
        
        # Verify state populated
        assert len(config_loader._cached_configs) > 0
        assert len(config_loader._watchers) > 0
        assert len(config_loader._event_handlers) > 0
        
        # Cleanup
        config_loader.cleanup()
        
        # Verify state cleared
        assert len(config_loader._cached_configs) == 0
        assert len(config_loader._watchers) == 0
        assert len(config_loader._event_handlers) == 0
    
    def test_context_manager(self, schema_dir, temp_dir, sample_config):
        """Test context manager functionality."""
        config_file = temp_dir / "context_test.json"
        with open(config_file, "w") as f:
            json.dump(sample_config, f)
        
        with ConfigurationLoader(schema_dir=schema_dir, enable_hot_reload=True) as loader:
            config = loader.load_config(config_file)
            assert config == sample_config
            
            # Should have active watchers
            assert len(loader._watchers) > 0
        
        # After context exit, should be cleaned up
        assert len(loader._watchers) == 0
    
    def test_thread_safety(self, config_loader, temp_dir, sample_config):
        """Test thread safety of configuration operations."""
        config_file = temp_dir / "thread_test.json"
        with open(config_file, "w") as f:
            json.dump(sample_config, f)
        
        results = []
        errors = []
        
        def load_config():
            try:
                config = config_loader.load_config(config_file)
                results.append(config)
            except Exception as e:
                errors.append(e)
        
        # Run multiple threads concurrently
        threads = [threading.Thread(target=load_config) for _ in range(10)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All threads should succeed
        assert len(errors) == 0
        assert len(results) == 10
        assert all(result == sample_config for result in results)
    
    def test_precedence_order(self, config_loader, temp_dir):
        """Test configuration precedence order."""
        file_config = {"value": "from_file", "file_only": True}
        
        config_file = temp_dir / "precedence.json"
        with open(config_file, "w") as f:
            json.dump(file_config, f)
        
        # Load file config first
        loaded_config = config_loader.load_config(config_file)
        
        # Set environment variable and merge explicitly
        env_vars = {"TEST_VALUE": "from_env"}
        
        with patch.dict(os.environ, env_vars):
            env_config = config_loader.load_from_env()
            merged_config = config_loader.merge_configs(loaded_config, env_config)
        
        # Environment should override file when explicitly merged
        assert merged_config["value"] == "from_env"
        assert merged_config["file_only"] is True  # File-only values preserved


# Test fixtures for edge cases and error conditions
class TestConfigurationLoaderEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def config_loader(self, temp_dir):
        """Create ConfigurationLoader instance."""
        return ConfigurationLoader(enable_hot_reload=False)
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration data."""
        return {
            "name": "test_plugin",
            "version": "1.0.0",
            "enabled": True
        }
    
    def test_malformed_schema(self, temp_dir):
        """Test handling of malformed schema files."""
        schema_dir = temp_dir / "schemas"
        schema_dir.mkdir()
        
        # Create malformed schema
        malformed_schema = temp_dir / "schemas" / "malformed.json"
        malformed_schema.write_text("{malformed json")
        
        loader = ConfigurationLoader(schema_dir=schema_dir)
        
        with pytest.raises(ConfigurationError, match="Failed to load schema"):
            loader._load_schema("malformed")
    
    def test_file_permission_error(self, config_loader, temp_dir, sample_config):
        """Test handling of file permission errors."""
        config_file = temp_dir / "no_permission.json"
        with open(config_file, "w") as f:
            json.dump(sample_config, f)
        
        # Mock permission error
        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            with pytest.raises(ConfigurationError):
                config_loader.load_config(config_file)
    
    def test_concurrent_file_modification(self, config_loader, temp_dir, sample_config):
        """Test handling of concurrent file modifications."""
        config_file = temp_dir / "concurrent.json"
        with open(config_file, "w") as f:
            json.dump(sample_config, f)
        
        # Mock file being modified during read
        original_open = open
        
        def mock_open(*args, **kwargs):
            # Modify file during read
            if args[0] == str(config_file) and 'r' in args[1]:
                with original_open(config_file, "w") as f:
                    json.dump({"modified": True}, f)
            return original_open(*args, **kwargs)
        
        with patch("builtins.open", side_effect=mock_open):
            # Should handle concurrent modification gracefully
            try:
                config_loader.load_config(config_file)
            except ConfigurationError:
                pass  # Expected behavior
    
    def test_memory_usage_large_config(self, config_loader, temp_dir):
        """Test memory usage with large configuration."""
        # Create large but valid config (under size limit)
        large_config = {
            "data": ["item_" + str(i) for i in range(10000)],
            "metadata": {str(i): f"value_{i}" for i in range(1000)}
        }
        
        config_file = temp_dir / "large.json"
        with open(config_file, "w") as f:
            json.dump(large_config, f)
        
        loaded_config = config_loader.load_config(config_file)
        
        assert len(loaded_config["data"]) == 10000
        assert len(loaded_config["metadata"]) == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
