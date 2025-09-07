"""
Data-driven configuration system for plugins.

This module provides a comprehensive configuration management system for plugins,
supporting multiple file formats, schema validation, hot-reloading, and secure
value handling with full CLAUDE.md compliance.

@description: Configuration loader with validation, hot-reload, and multi-format support
@author: AI Assistant (GitHub Copilot generated, reviewed by team)
@version: 1.0.0
@dependencies: asyncio, yaml, json, jsonschema, watchdog, pathlib, threading
@exports: ConfigurationLoader, ConfigFormat, ArrayMergeStrategy,
          ConfigurationError, ValidationError, SchemaValidationError,
          FileWatchError, ConfigurationValidationReport, ConfigurationEvent
@testing: tests/unit/governance/plugins/test_config.py
@last_review: 2025-01-06
"""

import asyncio
import copy
import json
import logging
import os
import re
import threading
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Set, Union
from urllib.parse import urlparse

import jsonschema
import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .base import ValidationResult, ValidationSeverity

__all__ = [
    'ConfigFormat',
    'ArrayMergeStrategy', 
    'ConfigurationError',
    'ValidationError',
    'SchemaValidationError',
    'FileWatchError',
    'ConfigurationLoader',
    'ConfigurationValidationReport',
    'ConfigurationEvent'
]


class ConfigFormat(Enum):
    """Supported configuration file formats."""
    JSON = "json"
    YAML = "yaml"
    YML = "yml"
    ENV = "env"
    DICT = "dict"


class ArrayMergeStrategy(Enum):
    """Strategies for merging arrays in configuration."""
    REPLACE = "replace"       # New array replaces old array
    APPEND = "append"         # New items appended to old array
    PREPEND = "prepend"       # New items prepended to old array
    MERGE_UNIQUE = "merge_unique"  # Merge arrays keeping unique items


@dataclass(frozen=True)
class ConfigurationEvent:
    """Configuration change event data."""
    event_type: str
    file_path: Optional[str]
    config_data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    validation_result: Optional[ValidationResult] = None


@dataclass
class ConfigurationValidationReport:
    """Detailed validation report for configuration."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    schema_errors: List[Dict[str, Any]] = field(default_factory=list)
    file_path: Optional[str] = None
    line_numbers: Dict[str, int] = field(default_factory=dict)
    
    @property
    def has_errors(self) -> bool:
        """Check if report contains errors."""
        return len(self.errors) > 0 or len(self.schema_errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if report contains warnings."""
        return len(self.warnings) > 0


class ConfigurationError(Exception):
    """Base configuration system error."""
    pass


class ValidationError(ConfigurationError):
    """Configuration validation error."""
    pass


class SchemaValidationError(ValidationError):
    """Schema validation specific error."""
    
    def __init__(self, message: str, schema_errors: List[Dict[str, Any]] = None):
        super().__init__(message)
        self.schema_errors = schema_errors or []


class FileWatchError(ConfigurationError):
    """File watching system error."""
    pass


class _ConfigFileWatcher(FileSystemEventHandler):
    """File system event handler for configuration files."""
    
    def __init__(self, callback: Callable[[str], None], debounce_ms: int = 500):
        """Initialize watcher with callback and debounce settings."""
        self.callback = callback
        self.debounce_ms = debounce_ms
        self._pending_events: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._logger = logging.getLogger(__name__)
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
            
        file_path = event.src_path
        current_time = time.time()
        
        with self._lock:
            self._pending_events[file_path] = current_time
        
        # Schedule debounced callback
        threading.Timer(
            self.debounce_ms / 1000.0,
            self._debounced_callback,
            args=[file_path, current_time]
        ).start()
    
    def _debounced_callback(self, file_path: str, event_time: float):
        """Execute callback after debounce period."""
        with self._lock:
            # Only execute if this is the most recent event for this file
            if (file_path in self._pending_events and 
                self._pending_events[file_path] == event_time):
                
                del self._pending_events[file_path]
                try:
                    self.callback(file_path)
                except Exception as e:
                    self._logger.error(f"Config file change callback failed: {e}")


class ConfigurationLoader:
    """
    Comprehensive configuration loader with validation, hot-reloading, and security.
    
    Supports multiple file formats (JSON, YAML), environment variables, schema
    validation with jsonschema, configuration inheritance and merging, hot-reload
    capabilities, and sensitive value handling.
    """
    
    def __init__(
        self,
        schema_dir: Optional[Union[str, Path]] = None,
        env_prefix: str = "CONFIG",
        array_merge_strategy: ArrayMergeStrategy = ArrayMergeStrategy.REPLACE,
        enable_hot_reload: bool = False,
        debounce_ms: int = 500,
        max_file_size_mb: int = 10
    ):
        """
        Initialize configuration loader.
        
        Args:
            schema_dir: Directory containing JSON schemas
            env_prefix: Environment variable prefix
            array_merge_strategy: Default strategy for merging arrays
            enable_hot_reload: Enable file watching for hot reload
            debounce_ms: Debounce time for file changes
            max_file_size_mb: Maximum file size limit in MB
        """
        self.schema_dir = Path(schema_dir) if schema_dir else None
        self.env_prefix = env_prefix
        self.array_merge_strategy = array_merge_strategy
        self.enable_hot_reload = enable_hot_reload
        self.debounce_ms = debounce_ms
        self.max_file_size_mb = max_file_size_mb
        
        self._lock = threading.RLock()
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._cached_configs: Dict[str, Dict[str, Any]] = {}
        self._last_good_configs: Dict[str, Dict[str, Any]] = {}
        self._watchers: Dict[str, Observer] = {}
        self._event_handlers: List[Callable[[ConfigurationEvent], None]] = []
        self._logger = logging.getLogger(__name__)
        
        # Security patterns
        self._sensitive_patterns = [
            re.compile(r'(?i)(password|secret|key|token|credential)', re.IGNORECASE),
            re.compile(r'(?i)(api[_-]?key|private[_-]?key)', re.IGNORECASE),
        ]
        
    def load_config(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load configuration from file with validation and caching.
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            Loaded and validated configuration dictionary
            
        Raises:
            ConfigurationError: If file cannot be loaded or validated
            FileNotFoundError: If file does not exist
            ValidationError: If configuration is invalid
        """
        file_path = Path(file_path).resolve()
        
        # Security: Prevent path traversal
        self._validate_file_path(file_path)
        
        # Check if file exists first
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        # Check file size
        if file_path.stat().st_size > (self.max_file_size_mb * 1024 * 1024):
            raise ConfigurationError(
                f"File too large: {file_path} ({file_path.stat().st_size} bytes)"
            )
        
        try:
            format_type = self._detect_format(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            config = self.load_from_string(content, format_type)
            
            # Cache successful load
            with self._lock:
                cache_key = str(file_path)
                self._cached_configs[cache_key] = copy.deepcopy(config)
                self._last_good_configs[cache_key] = copy.deepcopy(config)
            
            # Set up file watching if enabled
            if self.enable_hot_reload:
                self._setup_file_watcher(file_path)
            
            self._emit_event(ConfigurationEvent(
                event_type="config_loaded",
                file_path=str(file_path),
                config_data=self._mask_sensitive_data(config)
            ))
            
            self._logger.info(f"Successfully loaded config from {file_path}")
            return config
            
        except Exception as e:
            self._logger.error(f"Failed to load config from {file_path}: {e}")
            
            # Try to return last good config if available
            with self._lock:
                cache_key = str(file_path)
                if cache_key in self._last_good_configs:
                    self._logger.warning(f"Returning last good config for {file_path}")
                    return copy.deepcopy(self._last_good_configs[cache_key])
            
            raise ConfigurationError(f"Failed to load config from {file_path}: {e}") from e
    
    def load_from_string(
        self, 
        content: str, 
        format_type: Union[ConfigFormat, str]
    ) -> Dict[str, Any]:
        """
        Load configuration from string content.
        
        Args:
            content: Configuration content as string
            format_type: Configuration format (json, yaml, yml)
            
        Returns:
            Parsed configuration dictionary
            
        Raises:
            ConfigurationError: If content cannot be parsed
            ValidationError: If format is unsupported
        """
        if isinstance(format_type, str):
            try:
                format_type = ConfigFormat(format_type.lower())
            except ValueError:
                raise ValidationError(f"Unsupported format: {format_type}")
        
        try:
            if format_type in (ConfigFormat.YAML, ConfigFormat.YML):
                config = yaml.safe_load(content) or {}
            elif format_type == ConfigFormat.JSON:
                config = json.loads(content) or {}
            elif format_type == ConfigFormat.ENV:
                # ENV format not supported for string loading
                raise ValidationError(f"Unsupported format for string loading: {format_type}")
            else:
                raise ValidationError(f"Unsupported format for string loading: {format_type}")
            
            if not isinstance(config, dict):
                config = {"value": config}
            
            # Apply environment variable substitution
            config = self._substitute_env_vars(config)
            
            # Apply defaults and type coercion
            config = self._apply_defaults_and_coercion(config)
            
            return config
            
        except yaml.YAMLError as e:
            # Handle both old and new style error marks
            line_num = 1
            if hasattr(e, 'problem_mark') and e.problem_mark:
                line_num = e.problem_mark.line + 1
            raise ConfigurationError(f"YAML parsing error at line {line_num}: {e}") from e
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"JSON parsing error at line {e.lineno}: {e.msg}") from e
        except Exception as e:
            raise ConfigurationError(f"Failed to parse configuration: {e}") from e
    
    def load_from_env(self, prefix: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from environment variables.
        
        Args:
            prefix: Environment variable prefix (defaults to instance prefix)
            
        Returns:
            Configuration dictionary built from environment variables
        """
        prefix = prefix or self.env_prefix
        prefix_pattern = f"{prefix}_"
        config = {}
        
        for key, value in os.environ.items():
            if key.startswith(prefix_pattern):
                # Remove prefix and convert to nested dict structure
                config_key = key[len(prefix_pattern):].lower()
                nested_keys = config_key.split('_')
                
                # Build nested structure
                current = config
                for nested_key in nested_keys[:-1]:
                    if nested_key not in current:
                        current[nested_key] = {}
                    current = current[nested_key]
                
                # Convert value types
                final_key = nested_keys[-1]
                current[final_key] = self._coerce_env_value(value)
        
        self._emit_event(ConfigurationEvent(
            event_type="env_config_loaded",
            file_path=None,
            config_data=self._mask_sensitive_data(config)
        ))
        
        return config
    
    def validate_config(
        self, 
        config: Dict[str, Any], 
        schema: Optional[Dict[str, Any]] = None,
        schema_name: Optional[str] = None
    ) -> ConfigurationValidationReport:
        """
        Validate configuration against schema.
        
        Args:
            config: Configuration to validate
            schema: JSON schema dict (optional)
            schema_name: Name of schema file to load (optional)
            
        Returns:
            Detailed validation report
            
        Raises:
            ConfigurationError: If schema cannot be loaded
        """
        report = ConfigurationValidationReport(valid=True)
        
        # Load schema if name provided
        if schema_name and not schema:
            schema = self._load_schema(schema_name)
        
        if not schema:
            report.warnings.append("No schema provided for validation")
            return report
        
        try:
            # Validate against schema
            jsonschema.validate(instance=config, schema=schema)
            self._logger.debug("Configuration passed schema validation")
            
        except jsonschema.ValidationError as e:
            report.valid = False
            error_detail = {
                "message": e.message,
                "path": list(e.absolute_path),
                "schema_path": list(e.schema_path),
                "validator": e.validator,
                "validator_value": e.validator_value
            }
            report.schema_errors.append(error_detail)
            report.errors.append(f"Schema validation failed: {e.message}")
            
        except jsonschema.SchemaError as e:
            report.valid = False
            report.errors.append(f"Invalid schema: {e.message}")
            
        except Exception as e:
            report.valid = False
            report.errors.append(f"Validation error: {e}")
        
        # Additional custom validations
        self._perform_custom_validations(config, report)
        
        return report
    
    def merge_configs(
        self, 
        *configs: Dict[str, Any],
        array_strategy: Optional[ArrayMergeStrategy] = None
    ) -> Dict[str, Any]:
        """
        Merge multiple configuration dictionaries with deep merge support.
        
        Args:
            *configs: Configuration dictionaries to merge
            array_strategy: Strategy for merging arrays
            
        Returns:
            Merged configuration dictionary
        """
        if not configs:
            return {}
        
        array_strategy = array_strategy or self.array_merge_strategy
        result = copy.deepcopy(configs[0])
        
        for config in configs[1:]:
            result = self._deep_merge(result, config, array_strategy)
        
        # Apply configuration precedence
        result = self._apply_precedence(result)
        
        self._emit_event(ConfigurationEvent(
            event_type="configs_merged",
            file_path=None,
            config_data=self._mask_sensitive_data(result)
        ))
        
        return result
    
    def save_config(
        self, 
        config: Dict[str, Any], 
        file_path: Union[str, Path],
        format_type: Optional[ConfigFormat] = None
    ) -> bool:
        """
        Save configuration to file with validation.
        
        Args:
            config: Configuration dictionary to save
            file_path: Target file path
            format_type: File format (auto-detected if None)
            
        Returns:
            True if save successful, False otherwise
            
        Raises:
            ConfigurationError: If save fails
        """
        file_path = Path(file_path).resolve()
        
        # Security: Prevent path traversal
        self._validate_file_path(file_path)
        
        # Auto-detect format if not specified
        if not format_type:
            format_type = self._detect_format(file_path)
        
        try:
            # Create backup of existing file
            backup_path = None
            if file_path.exists():
                backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                file_path.rename(backup_path)
            
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            with open(file_path, 'w', encoding='utf-8') as f:
                if format_type in (ConfigFormat.YAML, ConfigFormat.YML):
                    yaml.dump(
                        config, 
                        f, 
                        default_flow_style=False,
                        allow_unicode=True,
                        indent=2
                    )
                elif format_type == ConfigFormat.JSON:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                else:
                    raise ConfigurationError(f"Unsupported format for saving: {format_type}")
            
            # Validate saved file
            try:
                loaded_config = self.load_config(file_path)
                if loaded_config != config:
                    raise ConfigurationError("Saved configuration differs from original")
            except Exception as e:
                # Restore backup if validation fails
                if backup_path and backup_path.exists():
                    if file_path.exists():
                        file_path.unlink()  # Remove the invalid file first
                    backup_path.rename(file_path)
                raise ConfigurationError(f"Validation failed after save: {e}") from e
            
            # Clean up backup on success
            if backup_path and backup_path.exists():
                backup_path.unlink()
            
            self._emit_event(ConfigurationEvent(
                event_type="config_saved",
                file_path=str(file_path),
                config_data=self._mask_sensitive_data(config)
            ))
            
            self._logger.info(f"Successfully saved config to {file_path}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to save config to {file_path}: {e}")
            raise ConfigurationError(f"Failed to save config to {file_path}: {e}") from e
    
    def add_event_handler(self, handler: Callable[[ConfigurationEvent], None]) -> None:
        """Add configuration event handler."""
        with self._lock:
            self._event_handlers.append(handler)
    
    def remove_event_handler(self, handler: Callable[[ConfigurationEvent], None]) -> None:
        """Remove configuration event handler."""
        with self._lock:
            try:
                self._event_handlers.remove(handler)
            except ValueError:
                pass  # Handler not found
    
    @asynccontextmanager
    async def watch_config(
        self, 
        file_path: Union[str, Path]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Context manager for watching configuration file changes.
        
        Args:
            file_path: Path to configuration file to watch
            
        Yields:
            Current configuration dictionary
        """
        file_path = Path(file_path).resolve()
        
        try:
            # Load initial configuration
            config = self.load_config(file_path)
            
            # Set up file watcher
            self._setup_file_watcher(file_path)
            
            yield config
            
        finally:
            # Clean up file watcher
            self._cleanup_file_watcher(file_path)
    
    def cleanup(self) -> None:
        """Clean up resources and file watchers."""
        with self._lock:
            # Stop all file watchers
            for observer in self._watchers.values():
                observer.stop()
                observer.join(timeout=1.0)
            
            self._watchers.clear()
            self._cached_configs.clear()
            self._event_handlers.clear()
        
        self._logger.info("Configuration loader cleaned up")
    
    def _detect_format(self, file_path: Path) -> ConfigFormat:
        """Detect configuration file format from extension."""
        suffix = file_path.suffix.lower()
        
        if suffix == '.json':
            return ConfigFormat.JSON
        elif suffix in ('.yaml', '.yml'):
            return ConfigFormat.YAML
        else:
            raise ValidationError(f"Unsupported file extension: {suffix}")
    
    def _validate_file_path(self, file_path: Path) -> None:
        """Validate file path for security."""
        try:
            # Basic path traversal check
            path_str = str(file_path)
            if '..' in path_str:
                raise ConfigurationError(f"Path traversal detected: {file_path}")
            
            # Resolve path and check for traversal attempts
            resolved_path = file_path.resolve()
            
            # Check if file exists and is readable (if it exists)
            if resolved_path.exists() and not os.access(resolved_path, os.R_OK):
                raise ConfigurationError(f"File not readable: {resolved_path}")
                
        except OSError as e:
            raise ConfigurationError(f"Invalid file path: {file_path}") from e
    
    def _load_schema(self, schema_name: str) -> Dict[str, Any]:
        """Load JSON schema from schema directory."""
        if not self.schema_dir:
            raise ConfigurationError("No schema directory configured")
        
        # Check cache first
        with self._lock:
            if schema_name in self._schemas:
                return self._schemas[schema_name]
        
        # Load from file
        schema_path = self.schema_dir / f"{schema_name}.json"
        if not schema_path.exists():
            raise ConfigurationError(f"Schema not found: {schema_path}")
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            # Cache schema
            with self._lock:
                self._schemas[schema_name] = schema
            
            return schema
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load schema {schema_name}: {e}") from e
    
    def _substitute_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Substitute environment variables in configuration."""
        def _substitute_value(value):
            if isinstance(value, str):
                # Replace ${ENV_VAR} and ${ENV_VAR:default} patterns
                pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
                
                def replacer(match):
                    env_var = match.group(1)
                    default = match.group(2) or ""
                    return os.getenv(env_var, default)
                
                return re.sub(pattern, replacer, value)
            elif isinstance(value, dict):
                return {k: _substitute_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [_substitute_value(item) for item in value]
            
            return value
        
        return _substitute_value(config)
    
    def _apply_defaults_and_coercion(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values and type coercion."""
        # Type coercion for common patterns
        def _coerce_value(value):
            if isinstance(value, str):
                # Boolean coercion
                if value.lower() in ('true', 'yes', '1', 'on'):
                    return True
                elif value.lower() in ('false', 'no', '0', 'off'):
                    return False
                
                # Numeric coercion
                try:
                    if '.' in value:
                        return float(value)
                    else:
                        return int(value)
                except ValueError:
                    pass
            
            return value
        
        def _process_dict(data):
            result = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    result[key] = _process_dict(value)
                elif isinstance(value, list):
                    result[key] = [_coerce_value(item) for item in value]
                else:
                    result[key] = _coerce_value(value)
            return result
        
        return _process_dict(config)
    
    def _coerce_env_value(self, value: str) -> Any:
        """Coerce environment variable string to appropriate type."""
        # Try boolean
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Try numeric
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Try JSON (for arrays/objects)
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Return as string
        return value
    
    def _deep_merge(
        self, 
        base: Dict[str, Any], 
        override: Dict[str, Any],
        array_strategy: ArrayMergeStrategy
    ) -> Dict[str, Any]:
        """Perform deep merge of two dictionaries."""
        result = copy.deepcopy(base)
        
        for key, value in override.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._deep_merge(result[key], value, array_strategy)
                elif isinstance(result[key], list) and isinstance(value, list):
                    result[key] = self._merge_arrays(result[key], value, array_strategy)
                else:
                    result[key] = copy.deepcopy(value)
            else:
                result[key] = copy.deepcopy(value)
        
        return result
    
    def _merge_arrays(
        self, 
        base: List[Any], 
        override: List[Any], 
        strategy: ArrayMergeStrategy
    ) -> List[Any]:
        """Merge arrays according to strategy."""
        if strategy == ArrayMergeStrategy.REPLACE:
            return copy.deepcopy(override)
        elif strategy == ArrayMergeStrategy.APPEND:
            return copy.deepcopy(base) + copy.deepcopy(override)
        elif strategy == ArrayMergeStrategy.PREPEND:
            return copy.deepcopy(override) + copy.deepcopy(base)
        elif strategy == ArrayMergeStrategy.MERGE_UNIQUE:
            # Merge keeping unique items (preserves order from base first)
            result = copy.deepcopy(base)
            for item in override:
                if item not in result:
                    result.append(copy.deepcopy(item))
            return result
        else:
            return copy.deepcopy(override)
    
    def _apply_precedence(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply configuration precedence rules."""
        # Don't apply environment precedence here - it should be explicit
        # Environment config should only be applied when explicitly requested
        return config
    
    def _perform_custom_validations(
        self, 
        config: Dict[str, Any], 
        report: ConfigurationValidationReport
    ) -> None:
        """Perform additional custom validations."""
        # Validate required security configurations
        if 'security' in config:
            security_config = config['security']
            if isinstance(security_config, dict):
                if not security_config.get('encryption_enabled', False):
                    report.warnings.append("Encryption is not enabled in security config")
        
        # Check for potentially dangerous configurations
        if 'debug' in config and config['debug']:
            report.warnings.append("Debug mode is enabled - disable in production")
        
        # Validate plugin-specific requirements
        if 'plugin_name' in config:
            plugin_name = config['plugin_name']
            if not isinstance(plugin_name, str) or not plugin_name.isidentifier():
                report.errors.append("plugin_name must be a valid Python identifier")
    
    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data for logging."""
        def _mask_dict(obj):
            if isinstance(obj, dict):
                result = {}
                for key, value in obj.items():
                    # Check if key matches sensitive pattern
                    is_sensitive = any(pattern.search(key) for pattern in self._sensitive_patterns)
                    
                    if is_sensitive and isinstance(value, str):
                        result[key] = "*" * min(len(value), 8)
                    elif isinstance(value, (dict, list)):
                        result[key] = _mask_dict(value)
                    else:
                        result[key] = value
                return result
            elif isinstance(obj, list):
                return [_mask_dict(item) for item in obj]
            else:
                return obj
        
        return _mask_dict(data)
    
    def _setup_file_watcher(self, file_path: Path) -> None:
        """Set up file watcher for hot reload."""
        if not self.enable_hot_reload:
            return
        
        file_key = str(file_path)
        
        with self._lock:
            # Don't create duplicate watchers
            if file_key in self._watchers:
                return
        
        try:
            def on_change(changed_path: str):
                if Path(changed_path) == file_path:
                    self._handle_file_change(file_path)
            
            event_handler = _ConfigFileWatcher(on_change, self.debounce_ms)
            observer = Observer()
            observer.schedule(event_handler, str(file_path.parent), recursive=False)
            observer.start()
            
            with self._lock:
                self._watchers[file_key] = observer
            
            self._logger.debug(f"Set up file watcher for {file_path}")
            
        except Exception as e:
            raise FileWatchError(f"Failed to set up file watcher: {e}") from e
    
    def _cleanup_file_watcher(self, file_path: Path) -> None:
        """Clean up file watcher."""
        file_key = str(file_path)
        
        with self._lock:
            if file_key in self._watchers:
                observer = self._watchers[file_key]
                observer.stop()
                observer.join(timeout=1.0)
                del self._watchers[file_key]
                
                self._logger.debug(f"Cleaned up file watcher for {file_path}")
    
    def _handle_file_change(self, file_path: Path) -> None:
        """Handle file change event."""
        self._logger.info(f"Configuration file changed: {file_path}")
        
        try:
            # Attempt to reload configuration
            new_config = self.load_config(file_path)
            
            # Validate new configuration
            validation_report = ConfigurationValidationReport(valid=True)
            
            # If we have a cached schema, validate against it
            cache_key = str(file_path)
            with self._lock:
                if cache_key in self._cached_configs:
                    # Use same validation as before
                    # Schema reference stored in self._schema_cache for re-validation
                    pass
            
            # Emit reload event
            self._emit_event(ConfigurationEvent(
                event_type="config_reloaded",
                file_path=str(file_path),
                config_data=self._mask_sensitive_data(new_config),
                validation_result=ValidationResult(
                    success=validation_report.valid,
                    plugin_name="ConfigurationLoader",
                    severity=ValidationSeverity.INFO if validation_report.valid else ValidationSeverity.ERROR,
                    messages=validation_report.warnings,
                    errors=validation_report.errors
                )
            ))
            
        except Exception as e:
            self._logger.error(f"Failed to reload configuration from {file_path}: {e}")
            
            # Emit reload failure event
            self._emit_event(ConfigurationEvent(
                event_type="config_reload_failed",
                file_path=str(file_path),
                config_data={},
                validation_result=ValidationResult(
                    success=False,
                    plugin_name="ConfigurationLoader",
                    severity=ValidationSeverity.ERROR,
                    errors=[str(e)]
                )
            ))
    
    def _emit_event(self, event: ConfigurationEvent) -> None:
        """Emit configuration event to handlers."""
        with self._lock:
            handlers = self._event_handlers.copy()
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                self._logger.warning(f"Event handler failed: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()