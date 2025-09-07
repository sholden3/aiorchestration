"""
Plugin lifecycle management system for governance validators.

This module provides comprehensive plugin lifecycle management including state
management, health monitoring, auto-restart with backoff, resource monitoring,
and event handling. It ensures thread-safe operations and graceful handling
of plugin initialization, execution, and teardown.
"""

import asyncio
import logging
import threading
import time
import yaml
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set, Tuple, Union

try:
    import psutil
except ImportError:
    psutil = None

from .base import IValidatorPlugin, PluginState, PluginHealth
from .registry import PluginRegistry

__all__ = [
    'PluginLifecycleError',
    'PluginStateTransitionError', 
    'ResourceLimitExceededError',
    'RestartAttempt',
    'PluginResourceUsage',
    'StateTransitionRecord',
    'PluginLifecycleManager'
]


class PluginLifecycleError(Exception):
    """Base exception for plugin lifecycle errors."""
    
    def __init__(self, message: str, plugin_name: str = None, original_exception: Exception = None):
        super().__init__(message)
        self.plugin_name = plugin_name
        self.original_exception = original_exception


class PluginStateTransitionError(PluginLifecycleError):
    """Raised when an invalid state transition is attempted."""
    
    def __init__(self, message: str, plugin_name: str, current_state: PluginState, 
                 target_state: PluginState, original_exception: Exception = None):
        super().__init__(message, plugin_name, original_exception)
        self.current_state = current_state
        self.target_state = target_state


class ResourceLimitExceededError(PluginLifecycleError):
    """Raised when a plugin exceeds resource limits."""
    
    def __init__(self, message: str, plugin_name: str, resource_type: str, 
                 current_value: float, limit: float):
        super().__init__(message, plugin_name)
        self.resource_type = resource_type
        self.current_value = current_value
        self.limit = limit


@dataclass
class RestartAttempt:
    """Records a restart attempt for a plugin."""
    timestamp: datetime
    attempt_number: int
    reason: str
    success: bool = False
    error: Optional[str] = None


@dataclass
class PluginResourceUsage:
    """Resource usage information for a plugin."""
    memory_mb: float = 0.0
    cpu_percent: float = 0.0
    uptime_seconds: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class StateTransitionRecord:
    """Records a state transition for audit purposes."""
    timestamp: datetime
    plugin_name: str
    from_state: PluginState
    to_state: PluginState
    success: bool
    duration_ms: float = 0.0
    error: Optional[str] = None


class PluginLifecycleManager:
    """
    Comprehensive plugin lifecycle management system.
    
    Provides state management, health monitoring, auto-restart capabilities,
    resource monitoring, and event handling for validator plugins.
    
    Features:
    - Thread-safe plugin state management
    - Automatic health monitoring with configurable intervals
    - Auto-restart with exponential backoff
    - Resource usage monitoring and limits
    - Comprehensive event system
    - Graceful shutdown handling
    - Circuit breaker pattern for failed plugins
    """
    
    # Valid state transitions
    _VALID_TRANSITIONS = {
        PluginState.UNLOADED: {PluginState.LOADING, PluginState.ERROR},
        PluginState.LOADING: {PluginState.READY, PluginState.ERROR, PluginState.STOPPING},
        PluginState.READY: {PluginState.STOPPING, PluginState.ERROR},
        PluginState.ERROR: {PluginState.LOADING, PluginState.STOPPING},
        PluginState.STOPPING: {PluginState.STOPPED, PluginState.ERROR},
        PluginState.STOPPED: {PluginState.LOADING, PluginState.ERROR}
    }
    
    def __init__(self, registry: Optional[PluginRegistry] = None):
        """
        Initialize the lifecycle manager.
        
        Args:
            registry: Optional plugin registry instance. If None, uses singleton.
        """
        self._registry = registry or PluginRegistry()
        self._lock = threading.RLock()
        self._logger = logging.getLogger(__name__)
        
        # Plugin instances and state tracking
        self._plugin_instances: Dict[str, IValidatorPlugin] = {}
        self._plugin_states: Dict[str, PluginState] = {}
        self._state_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Resource monitoring
        self._resource_usage: Dict[str, PluginResourceUsage] = {}
        self._resource_monitoring_task: Optional[asyncio.Task] = None
        
        # Health monitoring
        self._health_check_task: Optional[asyncio.Task] = None
        self._last_health_check: Dict[str, datetime] = {}
        
        # Restart management
        self._restart_attempts: Dict[str, List[RestartAttempt]] = defaultdict(list)
        self._circuit_breakers: Dict[str, bool] = {}  # plugin_name -> is_open
        
        # Event handling
        self._event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Configuration
        self._config: Dict[str, Any] = {}
        self._load_config()
        
        # Shutdown flag
        self._shutdown_requested = False
        
        self._logger.info("Plugin lifecycle manager initialized")
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        config_path = Path("config/governance/lifecycle.yaml")
        
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
            else:
                self._logger.warning(f"Config file not found: {config_path}, using defaults")
                self._config = self._get_default_config()
        except Exception as e:
            self._logger.error(f"Failed to load config from {config_path}: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'health_check': {
                'interval_seconds': 60,
                'timeout_seconds': 5
            },
            'restart_policy': {
                'max_attempts': 3,
                'backoff_multiplier': 2,
                'initial_delay_seconds': 1
            },
            'resource_limits': {
                'max_memory_mb': 100,
                'max_cpu_percent': 50
            },
            'state_transitions': {
                'timeout_seconds': 30
            },
            'logging': {
                'level': 'INFO',
                'log_state_transitions': True,
                'log_health_checks': True,
                'log_resource_usage': True
            }
        }
    
    async def start_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Start a plugin by name.
        
        Args:
            plugin_name: Name of the plugin to start
            config: Optional plugin configuration
            
        Returns:
            True if plugin started successfully, False otherwise
            
        Raises:
            PluginLifecycleError: If plugin cannot be started
        """
        try:
            self._logger.info(f"Starting plugin: {plugin_name}")
            
            # Transition to LOADING state first
            async with self._state_transition_context(plugin_name, PluginState.LOADING):
                # Get plugin class from registry
                plugin_class = self._registry.get_plugin(plugin_name)
                if plugin_class is None:
                    raise PluginLifecycleError(
                        f"Plugin not found in registry: {plugin_name}",
                        plugin_name
                    )
                
                # Create plugin instance to get metadata
                # We'll need to get the metadata from the registry's internal store
                with self._registry._registry_lock:
                    metadata = self._registry._metadata.get(plugin_name)
                
                if metadata is None:
                    raise PluginLifecycleError(
                        f"Plugin metadata not found: {plugin_name}",
                        plugin_name
                    )
                
                # Create plugin instance
                plugin_instance = plugin_class(metadata)
                
                # Initialize plugin with timeout
                timeout = self._config.get('state_transitions', {}).get('timeout_seconds', 30)
                plugin_config = config or {}
                
                await asyncio.wait_for(
                    plugin_instance.initialize(plugin_config),
                    timeout=timeout
                )
                
                with self._lock:
                    self._plugin_instances[plugin_name] = plugin_instance
                    self._resource_usage[plugin_name] = PluginResourceUsage()
                    self._circuit_breakers[plugin_name] = False
            
            # Transition to READY state after successful initialization
            async with self._state_transition_context(plugin_name, PluginState.READY):
                await self._emit_event('plugin_started', {
                    'plugin_name': plugin_name,
                    'config': plugin_config
                })
                
                self._logger.info(f"Plugin started successfully: {plugin_name}")
                return True
                
        except asyncio.TimeoutError:
            error_msg = f"Plugin initialization timeout: {plugin_name}"
            self._logger.error(error_msg)
            await self._transition_to_error_state(plugin_name, error_msg)
            return False
            
        except Exception as e:
            error_msg = f"Failed to start plugin {plugin_name}: {e}"
            self._logger.error(error_msg)
            await self._transition_to_error_state(plugin_name, str(e))
            return False
    
    async def stop_plugin(self, plugin_name: str) -> bool:
        """
        Stop a plugin by name.
        
        Args:
            plugin_name: Name of the plugin to stop
            
        Returns:
            True if plugin stopped successfully, False otherwise
        """
        # Check current state first
        current_state = self.get_plugin_state(plugin_name)
        if current_state is None:
            self._logger.warning(f"Plugin not found: {plugin_name}")
            return False
            
        if current_state in (PluginState.UNLOADED, PluginState.STOPPED):
            self._logger.info(f"Plugin already stopped: {plugin_name}")
            return True
            
        # Handle plugins in ERROR state - we can stop them directly
        if current_state == PluginState.ERROR:
            try:
                with self._lock:
                    self._plugin_instances.pop(plugin_name, None)
                    self._resource_usage.pop(plugin_name, None)
                    self._last_health_check.pop(plugin_name, None)
                    self._plugin_states[plugin_name] = PluginState.STOPPED
                
                await self._emit_event('plugin_stopped', {'plugin_name': plugin_name})
                self._logger.info(f"Plugin in error state stopped: {plugin_name}")
                return True
            except Exception as e:
                self._logger.error(f"Failed to stop plugin in error state {plugin_name}: {e}")
                return False
        
        # For plugins not in READY state, we need to handle them differently
        if current_state != PluginState.READY:
            self._logger.warning(f"Attempting to stop plugin not in READY state: {plugin_name} (state: {current_state})")
            # Still try to clean up
            try:
                with self._lock:
                    self._plugin_instances.pop(plugin_name, None)
                    self._resource_usage.pop(plugin_name, None)
                    self._last_health_check.pop(plugin_name, None)
                    self._plugin_states[plugin_name] = PluginState.STOPPED
                return True
            except Exception:
                return False
        
        try:
            async with self._state_transition_context(plugin_name, PluginState.STOPPING):
                self._logger.info(f"Stopping plugin: {plugin_name}")
                
                with self._lock:
                    plugin_instance = self._plugin_instances.get(plugin_name)
                
                if plugin_instance is None:
                    self._logger.warning(f"Plugin instance not found: {plugin_name}")
                    return False
                
                # Teardown plugin with timeout
                timeout = self._config.get('state_transitions', {}).get('timeout_seconds', 30)
                await asyncio.wait_for(
                    plugin_instance.teardown(),
                    timeout=timeout
                )
                
                with self._lock:
                    # Clean up resources
                    self._plugin_instances.pop(plugin_name, None)
                    self._resource_usage.pop(plugin_name, None)
                    self._last_health_check.pop(plugin_name, None)
            
            # Transition to STOPPED state
            async with self._state_transition_context(plugin_name, PluginState.STOPPED):
                await self._emit_event('plugin_stopped', {'plugin_name': plugin_name})
                self._logger.info(f"Plugin stopped successfully: {plugin_name}")
                return True
                
        except asyncio.TimeoutError:
            error_msg = f"Plugin teardown timeout: {plugin_name}"
            self._logger.error(error_msg)
            await self._transition_to_error_state(plugin_name, error_msg)
            return False
            
        except Exception as e:
            error_msg = f"Failed to stop plugin {plugin_name}: {e}"
            self._logger.error(error_msg)
            await self._transition_to_error_state(plugin_name, str(e))
            return False
    
    async def restart_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Restart a plugin with exponential backoff.
        
        Args:
            plugin_name: Name of the plugin to restart
            config: Optional new plugin configuration
            
        Returns:
            True if plugin restarted successfully, False otherwise
        """
        # Check circuit breaker
        if self._circuit_breakers.get(plugin_name, False):
            self._logger.warning(f"Circuit breaker open for plugin: {plugin_name}")
            return False
        
        # Check restart attempts
        attempts = self._restart_attempts.get(plugin_name, [])
        max_attempts = self._config.get('restart_policy', {}).get('max_attempts', 3)
        
        # Clean old attempts (older than 1 hour)
        current_time = datetime.now()
        recent_attempts = [
            attempt for attempt in attempts
            if (current_time - attempt.timestamp).total_seconds() < 3600
        ]
        self._restart_attempts[plugin_name] = recent_attempts
        
        if len(recent_attempts) >= max_attempts:
            self._logger.error(f"Maximum restart attempts exceeded for plugin: {plugin_name}")
            self._circuit_breakers[plugin_name] = True
            return False
        
        attempt_number = len(recent_attempts) + 1
        restart_attempt = RestartAttempt(
            timestamp=current_time,
            attempt_number=attempt_number,
            reason="Manual restart"
        )
        
        try:
            # Calculate backoff delay
            if attempt_number > 1:
                initial_delay = self._config.get('restart_policy', {}).get('initial_delay_seconds', 1)
                multiplier = self._config.get('restart_policy', {}).get('backoff_multiplier', 2)
                delay = initial_delay * (multiplier ** (attempt_number - 2))
                
                self._logger.info(f"Waiting {delay}s before restart attempt {attempt_number} for {plugin_name}")
                await asyncio.sleep(delay)
            
            # Stop the plugin first if it's running
            current_state = self.get_plugin_state(plugin_name)
            if current_state in (PluginState.READY, PluginState.ERROR, PluginState.LOADING):
                success = await self.stop_plugin(plugin_name)
                if not success:
                    self._logger.warning(f"Failed to stop plugin before restart: {plugin_name}")
            
            # Start the plugin
            success = await self.start_plugin(plugin_name, config)
            
            restart_attempt.success = success
            if success:
                self._logger.info(f"Plugin restarted successfully: {plugin_name} (attempt {attempt_number})")
            else:
                restart_attempt.error = "Failed to start plugin after stop"
            
            return success
            
        except Exception as e:
            restart_attempt.success = False
            restart_attempt.error = str(e)
            self._logger.error(f"Restart attempt {attempt_number} failed for {plugin_name}: {e}")
            return False
            
        finally:
            self._restart_attempts[plugin_name].append(restart_attempt)
    
    def get_plugin_state(self, plugin_name: str) -> Optional[PluginState]:
        """
        Get the current state of a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Current plugin state or None if plugin not found
        """
        with self._lock:
            return self._plugin_states.get(plugin_name)
    
    async def start_all(self) -> Dict[str, bool]:
        """
        Start all registered plugins.
        
        Returns:
            Dictionary mapping plugin names to success status
        """
        self._logger.info("Starting all plugins")
        results = {}
        
        # Get plugin metadata list and extract names
        plugin_metadata_list = self._registry.list_plugins()
        plugin_names = [metadata.name for metadata in plugin_metadata_list]
        
        for plugin_name in plugin_names:
            try:
                results[plugin_name] = await self.start_plugin(plugin_name)
            except Exception as e:
                self._logger.error(f"Failed to start plugin {plugin_name}: {e}")
                results[plugin_name] = False
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        self._logger.info(f"Started {successful}/{total} plugins successfully")
        
        return results
    
    async def stop_all(self) -> Dict[str, bool]:
        """
        Stop all running plugins.
        
        Returns:
            Dictionary mapping plugin names to success status
        """
        self._logger.info("Stopping all plugins")
        results = {}
        
        with self._lock:
            plugin_names = list(self._plugin_instances.keys())
        
        # Stop plugins in reverse dependency order
        for plugin_name in reversed(plugin_names):
            try:
                results[plugin_name] = await self.stop_plugin(plugin_name)
            except Exception as e:
                self._logger.error(f"Failed to stop plugin {plugin_name}: {e}")
                results[plugin_name] = False
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        self._logger.info(f"Stopped {successful}/{total} plugins successfully")
        
        return results
    
    async def monitor_health(self) -> Dict[str, PluginHealth]:
        """
        Monitor the health of all running plugins.
        
        Returns:
            Dictionary mapping plugin names to health information
        """
        health_status = {}
        
        with self._lock:
            plugin_instances = self._plugin_instances.copy()
        
        for plugin_name, plugin_instance in plugin_instances.items():
            try:
                # Get plugin health
                health = plugin_instance.health
                
                # Update resource usage
                await self._update_resource_usage(plugin_name)
                
                # Check resource limits
                await self._check_resource_limits(plugin_name)
                
                # Update last health check
                with self._lock:
                    self._last_health_check[plugin_name] = datetime.now()
                
                health_status[plugin_name] = health
                
                await self._emit_event('health_check', {
                    'plugin_name': plugin_name,
                    'health': health
                })
                
            except Exception as e:
                self._logger.error(f"Health check failed for plugin {plugin_name}: {e}")
                await self._emit_event('plugin_error', {
                    'plugin_name': plugin_name,
                    'error': str(e)
                })
                
                # Consider transitioning to error state
                if self.get_plugin_state(plugin_name) == PluginState.READY:
                    await self._transition_to_error_state(plugin_name, str(e))
        
        return health_status
    
    def register_event_handler(self, event: str, handler: Callable) -> None:
        """
        Register an event handler.
        
        Args:
            event: Event name
            handler: Async or sync callable to handle the event
        """
        with self._lock:
            self._event_handlers[event].append(handler)
        
        self._logger.debug(f"Registered event handler for '{event}'")
    
    def unregister_event_handler(self, event: str, handler: Callable) -> None:
        """
        Unregister an event handler.
        
        Args:
            event: Event name
            handler: Handler to remove
        """
        with self._lock:
            try:
                self._event_handlers[event].remove(handler)
                if not self._event_handlers[event]:
                    del self._event_handlers[event]
            except (ValueError, KeyError):
                pass
        
        self._logger.debug(f"Unregistered event handler for '{event}'")
    
    async def start_monitoring(self) -> None:
        """Start background monitoring tasks."""
        if self._health_check_task is None or self._health_check_task.done():
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            self._logger.info("Started health monitoring")
        
        if psutil and (self._resource_monitoring_task is None or self._resource_monitoring_task.done()):
            self._resource_monitoring_task = asyncio.create_task(self._resource_monitoring_loop())
            self._logger.info("Started resource monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop background monitoring tasks."""
        self._shutdown_requested = True
        
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None
        
        if self._resource_monitoring_task:
            self._resource_monitoring_task.cancel()
            try:
                await self._resource_monitoring_task
            except asyncio.CancelledError:
                pass
            self._resource_monitoring_task = None
        
        self._logger.info("Stopped monitoring tasks")
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the lifecycle manager."""
        self._logger.info("Shutting down plugin lifecycle manager")
        
        # Stop monitoring
        await self.stop_monitoring()
        
        # Stop all plugins
        await self.stop_all()
        
        # Clear state
        with self._lock:
            self._plugin_instances.clear()
            self._plugin_states.clear()
            self._resource_usage.clear()
            self._event_handlers.clear()
        
        self._logger.info("Plugin lifecycle manager shutdown complete")
    
    # Private methods
    
    @asynccontextmanager
    async def _state_transition_context(self, plugin_name: str, target_state: PluginState):
        """Context manager for atomic state transitions."""
        start_time = time.time()
        
        with self._lock:
            current_state = self._plugin_states.get(plugin_name, PluginState.UNLOADED)
            
            # Validate transition
            if current_state not in self._VALID_TRANSITIONS:
                raise PluginStateTransitionError(
                    f"No valid transitions defined for state: {current_state}",
                    plugin_name, current_state, target_state
                )
            
            if target_state not in self._VALID_TRANSITIONS[current_state]:
                raise PluginStateTransitionError(
                    f"Invalid transition from {current_state} to {target_state}",
                    plugin_name, current_state, target_state
                )
            
            # Set transitioning state
            self._plugin_states[plugin_name] = target_state
        
        transition_record = StateTransitionRecord(
            timestamp=datetime.now(),
            plugin_name=plugin_name,
            from_state=current_state,
            to_state=target_state,
            success=False
        )
        
        try:
            yield
            
            # Transition successful
            transition_record.success = True
            
            await self._emit_event('state_change', {
                'plugin_name': plugin_name,
                'old_state': current_state,
                'new_state': target_state
            })
            
            if self._config.get('logging', {}).get('log_state_transitions', True):
                self._logger.info(f"State transition: {plugin_name} {current_state} -> {target_state}")
        
        except Exception as e:
            # Transition failed, revert state
            with self._lock:
                self._plugin_states[plugin_name] = current_state
            
            transition_record.success = False
            transition_record.error = str(e)
            
            self._logger.error(f"State transition failed: {plugin_name} {current_state} -> {target_state}: {e}")
            raise
        
        finally:
            # Record transition
            transition_record.duration_ms = (time.time() - start_time) * 1000
            with self._lock:
                self._state_history[plugin_name].append(transition_record)
    
    async def _transition_to_error_state(self, plugin_name: str, error: str) -> None:
        """Transition a plugin to error state."""
        try:
            async with self._state_transition_context(plugin_name, PluginState.ERROR):
                await self._emit_event('plugin_error', {
                    'plugin_name': plugin_name,
                    'error': error
                })
        except Exception as e:
            self._logger.error(f"Failed to transition {plugin_name} to error state: {e}")
    
    async def _update_resource_usage(self, plugin_name: str) -> None:
        """Update resource usage for a plugin."""
        if not psutil:
            return
        
        try:
            # This is a simplified approach - in a real implementation,
            # you might need to track the actual processes/threads spawned by plugins
            process = psutil.Process()
            
            with self._lock:
                if plugin_name in self._resource_usage:
                    usage = self._resource_usage[plugin_name]
                    usage.memory_mb = process.memory_info().rss / (1024 * 1024)
                    usage.cpu_percent = process.cpu_percent()
                    usage.last_updated = datetime.now()
        
        except Exception as e:
            self._logger.debug(f"Failed to update resource usage for {plugin_name}: {e}")
    
    async def _check_resource_limits(self, plugin_name: str) -> None:
        """Check if a plugin has exceeded resource limits."""
        with self._lock:
            usage = self._resource_usage.get(plugin_name)
        
        if not usage:
            return
        
        limits = self._config.get('resource_limits', {})
        max_memory = limits.get('max_memory_mb', 100)
        max_cpu = limits.get('max_cpu_percent', 50)
        
        if usage.memory_mb > max_memory:
            error = f"Memory limit exceeded: {usage.memory_mb:.1f}MB > {max_memory}MB"
            await self._emit_event('resource_limit_exceeded', {
                'plugin_name': plugin_name,
                'resource_type': 'memory',
                'current_value': usage.memory_mb,
                'limit': max_memory
            })
            
            # Consider restarting or stopping the plugin
            if self.get_plugin_state(plugin_name) == PluginState.READY:
                self._logger.warning(f"Plugin {plugin_name}: {error}")
        
        if usage.cpu_percent > max_cpu:
            error = f"CPU limit exceeded: {usage.cpu_percent:.1f}% > {max_cpu}%"
            await self._emit_event('resource_limit_exceeded', {
                'plugin_name': plugin_name,
                'resource_type': 'cpu',
                'current_value': usage.cpu_percent,
                'limit': max_cpu
            })
    
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
    
    async def _health_check_loop(self) -> None:
        """Background task for periodic health checks."""
        interval = self._config.get('health_check', {}).get('interval_seconds', 60)
        
        while not self._shutdown_requested:
            try:
                await self.monitor_health()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(interval)
    
    async def _resource_monitoring_loop(self) -> None:
        """Background task for resource monitoring."""
        interval = 30  # Check every 30 seconds
        
        while not self._shutdown_requested:
            try:
                with self._lock:
                    plugin_names = list(self._plugin_instances.keys())
                
                for plugin_name in plugin_names:
                    await self._update_resource_usage(plugin_name)
                    await self._check_resource_limits(plugin_name)
                
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Resource monitoring loop error: {e}")
                await asyncio.sleep(interval)