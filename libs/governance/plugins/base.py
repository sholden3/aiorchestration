"""
Base plugin interface system for governance validators.

This module provides the core abstractions and interfaces for implementing
validator plugins in the governance system. It includes the base plugin
interface, data models, and utilities for plugin lifecycle management.

@description: Core plugin interface and base implementation for validator plugins
@author: AI Assistant (GitHub Copilot generated, reviewed by team)
@version: 1.0.0
@dependencies: asyncio, logging, threading, dataclasses, abc, typing
@exports: IValidatorPlugin, BaseValidatorPlugin, PluginMetadata, PluginHealth,
          ValidationResult, PluginState, ValidationMode, ValidationSeverity
@testing: tests/unit/governance/plugins/test_base.py
@last_review: 2025-01-06
"""

import asyncio
import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

__all__ = [
    'PluginState',
    'ValidationMode', 
    'ValidationSeverity',
    'PluginMetadata',
    'PluginHealth',
    'ValidationResult',
    'IValidatorPlugin',
    'BaseValidatorPlugin'
]


class PluginState(Enum):
    """Plugin lifecycle states."""
    UNLOADED = "unloaded"
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"
    STOPPING = "stopping"
    STOPPED = "stopped"


class ValidationMode(Enum):
    """Validation execution modes."""
    SYNC = "sync"
    ASYNC = "async"
    PARALLEL = "parallel"


class ValidationSeverity(Enum):
    """Validation result severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True)
class PluginMetadata:
    """Plugin metadata information."""
    name: str
    version: str
    description: str
    author: str
    license: str
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.name or not self.version:
            raise ValueError("Plugin name and version are required")


@dataclass
class PluginHealth:
    """Plugin health and status information."""
    state: PluginState
    healthy: bool
    last_check: datetime
    uptime_seconds: float = 0.0
    error_count: int = 0
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def uptime_display(self) -> str:
        """Human readable uptime."""
        hours, remainder = divmod(int(self.uptime_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    success: bool
    plugin_name: str
    severity: ValidationSeverity
    messages: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    
    def add_message(self, message: str, severity: ValidationSeverity = ValidationSeverity.INFO):
        """Add a message with specified severity."""
        self.messages.append(message)
        if severity == ValidationSeverity.ERROR:
            self.errors.append(message)
        elif severity == ValidationSeverity.WARNING:
            self.warnings.append(message)
    
    @property
    def has_errors(self) -> bool:
        """Check if result contains errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if result contains warnings."""
        return len(self.warnings) > 0


class IValidatorPlugin(ABC):
    """Abstract base interface for validator plugins."""
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        raise NotImplementedError
    
    @property 
    @abstractmethod
    def health(self) -> PluginHealth:
        """Get current plugin health status."""
        raise NotImplementedError
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the plugin with configuration.
        
        Args:
            config: Plugin configuration dictionary
            
        Raises:
            ValueError: If configuration is invalid
            RuntimeError: If initialization fails
        """
        raise NotImplementedError
    
    @abstractmethod
    async def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Perform validation on the given context.
        
        Args:
            context: Validation context data
            
        Returns:
            ValidationResult: Result of validation
            
        Raises:
            ValidationError: If validation cannot be performed
        """
        raise NotImplementedError
    
    @abstractmethod
    async def configure(self, config: Dict[str, Any]) -> None:
        """
        Update plugin configuration.
        
        Args:
            config: New configuration to apply
            
        Raises:
            ValueError: If configuration is invalid
        """
        raise NotImplementedError
    
    @abstractmethod
    async def teardown(self) -> None:
        """
        Clean up resources and shut down plugin.
        
        Raises:
            RuntimeError: If teardown fails
        """
        raise NotImplementedError


class BaseValidatorPlugin(IValidatorPlugin):
    """
    Base implementation of validator plugin with common functionality.
    
    Provides thread-safe state management, configuration validation,
    health monitoring, and event handling capabilities.
    """
    
    def __init__(self, metadata: PluginMetadata):
        """Initialize base plugin with metadata."""
        self._metadata = metadata
        self._lock = threading.RLock()
        self._state = PluginState.UNLOADED
        self._config: Dict[str, Any] = {}
        self._start_time = time.time()
        self._error_count = 0
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._logger = logging.getLogger(f"plugin.{metadata.name}")
        self._validation_mode = ValidationMode.ASYNC
        
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return self._metadata
    
    @property
    def health(self) -> PluginHealth:
        """Get current plugin health status."""
        with self._lock:
            uptime = time.time() - self._start_time if self._state == PluginState.READY else 0.0
            return PluginHealth(
                state=self._state,
                healthy=self._state == PluginState.READY and self._error_count == 0,
                last_check=datetime.now(),
                uptime_seconds=uptime,
                error_count=self._error_count,
                metrics=self._collect_metrics()
            )
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get current configuration (thread-safe)."""
        with self._lock:
            return self._config.copy()
    
    @property
    def state(self) -> PluginState:
        """Get current plugin state (thread-safe)."""
        with self._lock:
            return self._state
    
    @property
    def validation_mode(self) -> ValidationMode:
        """Get current validation mode."""
        with self._lock:
            return self._validation_mode
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        with self._lock:
            if self._state != PluginState.UNLOADED:
                raise RuntimeError(f"Plugin {self.metadata.name} already initialized")
            
            self._state = PluginState.LOADING
        
        try:
            self._logger.info(f"Initializing plugin {self.metadata.name}")
            
            # Validate configuration
            validated_config = await self._validate_config(config)
            
            with self._lock:
                self._config = validated_config
                self._validation_mode = ValidationMode(
                    validated_config.get('validation_mode', 'async')
                )
            
            # Perform plugin-specific initialization
            await self._do_initialize(validated_config)
            
            with self._lock:
                self._state = PluginState.READY
                self._start_time = time.time()
            
            await self._emit_event('initialized', {'config': validated_config})
            self._logger.info(f"Plugin {self.metadata.name} initialized successfully")
            
        except Exception as e:
            with self._lock:
                self._state = PluginState.ERROR
                self._error_count += 1
            
            self._logger.error(f"Failed to initialize plugin {self.metadata.name}: {e}")
            await self._emit_event('initialization_failed', {'error': str(e)})
            raise
    
    async def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """Perform validation with timing and error handling."""
        start_time = time.time()
        
        with self._lock:
            if self._state != PluginState.READY:
                return ValidationResult(
                    success=False,
                    plugin_name=self.metadata.name,
                    severity=ValidationSeverity.ERROR,
                    errors=[f"Plugin not ready (state: {self._state.value})"]
                )
        
        try:
            # Perform validation based on mode
            if self._validation_mode == ValidationMode.SYNC:
                result = await self._validate_sync(context)
            else:
                result = await self._validate_async(context)
            
            result.duration_ms = (time.time() - start_time) * 1000
            
            await self._emit_event('validation_completed', {
                'context': context,
                'result': result
            })
            
            return result
            
        except Exception as e:
            with self._lock:
                self._error_count += 1
            
            self._logger.error(f"Validation failed in {self.metadata.name}: {e}")
            
            return ValidationResult(
                success=False,
                plugin_name=self.metadata.name,
                severity=ValidationSeverity.ERROR,
                errors=[str(e)],
                duration_ms=(time.time() - start_time) * 1000
            )
    
    async def configure(self, config: Dict[str, Any]) -> None:
        """Update plugin configuration."""
        try:
            validated_config = await self._validate_config(config)
            
            with self._lock:
                old_config = self._config.copy()
                self._config.update(validated_config)
                
                if 'validation_mode' in validated_config:
                    self._validation_mode = ValidationMode(validated_config['validation_mode'])
            
            await self._do_configure(validated_config)
            await self._emit_event('configured', {
                'old_config': old_config,
                'new_config': validated_config
            })
            
            self._logger.info(f"Plugin {self.metadata.name} reconfigured")
            
        except Exception as e:
            self._logger.error(f"Failed to configure plugin {self.metadata.name}: {e}")
            raise
    
    async def teardown(self) -> None:
        """Clean up resources and shut down plugin."""
        with self._lock:
            if self._state in (PluginState.STOPPED, PluginState.STOPPING):
                return
            
            self._state = PluginState.STOPPING
        
        try:
            self._logger.info(f"Shutting down plugin {self.metadata.name}")
            await self._do_teardown()
            
            with self._lock:
                self._state = PluginState.STOPPED
                self._event_handlers.clear()
            
            self._logger.info(f"Plugin {self.metadata.name} shut down successfully")
            
        except Exception as e:
            with self._lock:
                self._state = PluginState.ERROR
                self._error_count += 1
            
            self._logger.error(f"Failed to shut down plugin {self.metadata.name}: {e}")
            raise
    
    def register_event_handler(self, event: str, handler: Callable) -> None:
        """Register an event handler."""
        with self._lock:
            if event not in self._event_handlers:
                self._event_handlers[event] = []
            self._event_handlers[event].append(handler)
    
    def unregister_event_handler(self, event: str, handler: Callable) -> None:
        """Unregister an event handler."""
        with self._lock:
            if event in self._event_handlers:
                try:
                    self._event_handlers[event].remove(handler)
                    if not self._event_handlers[event]:
                        del self._event_handlers[event]
                except ValueError:
                    pass  # Handler not found
    
    async def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration before applying."""
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
        
        validated = config.copy()
        
        # Validate validation_mode if present
        if 'validation_mode' in validated:
            try:
                ValidationMode(validated['validation_mode'])
            except ValueError:
                raise ValueError(f"Invalid validation_mode: {validated['validation_mode']}")
        
        return validated
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect plugin metrics."""
        return {
            'validation_mode': self._validation_mode.value,
            'config_keys': list(self._config.keys()),
            'event_handlers': {
                event: len(handlers) 
                for event, handlers in self._event_handlers.items()
            }
        }
    
    async def _emit_event(self, event: str, data: Dict[str, Any]) -> None:
        """Emit an event to registered handlers."""
        with self._lock:
            handlers = self._event_handlers.get(event, []).copy()
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event, data)
                else:
                    handler(event, data)
            except Exception as e:
                self._logger.warning(f"Event handler failed for {event}: {e}")
    
    # Abstract methods for plugin-specific implementation
    async def _do_initialize(self, config: Dict[str, Any]) -> None:
        """Plugin-specific initialization logic."""
        pass
    
    async def _validate_async(self, context: Dict[str, Any]) -> ValidationResult:
        """Perform async validation - override in subclass."""
        return ValidationResult(
            success=True,
            plugin_name=self.metadata.name,
            severity=ValidationSeverity.INFO,
            messages=["Base validation passed"]
        )
    
    async def _validate_sync(self, context: Dict[str, Any]) -> ValidationResult:
        """Perform sync validation - override in subclass."""
        return await self._validate_async(context)
    
    async def _do_configure(self, config: Dict[str, Any]) -> None:
        """Plugin-specific configuration logic."""
        pass
    
    async def _do_teardown(self) -> None:
        """Plugin-specific teardown logic."""
        pass
