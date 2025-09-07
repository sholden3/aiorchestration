"""
Dynamic plugin registry system for governance validators.

This module provides a thread-safe singleton registry for managing validator plugins,
including discovery, registration, dependency resolution, and version compatibility.
Supports dynamic loading from multiple directories with configurable patterns.
"""

import asyncio
import glob
import importlib
import importlib.util
import inspect
import logging
import os
import re
import threading
import time
import yaml
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, Union

from .base import IValidatorPlugin, PluginMetadata

__all__ = ['PluginRegistry', 'PluginDiscoveryError', 'PluginRegistrationError']


class PluginDiscoveryError(Exception):
    """
    Raised when plugin discovery fails.
    
    This exception is raised when the plugin discovery process encounters
    an error that prevents it from completing successfully, such as:
    - Directory access permissions issues
    - Module loading failures that affect the entire discovery process
    - Timeout during discovery operations
    """
    
    def __init__(self, message: str, plugin_path: str = None, original_exception: Exception = None):
        """
        Initialize the PluginDiscoveryError.
        
        Args:
            message: Descriptive error message
            plugin_path: Path where the error occurred (optional)
            original_exception: The underlying exception that caused this error (optional)
        """
        super().__init__(message)
        self.plugin_path = plugin_path
        self.original_exception = original_exception


class PluginRegistrationError(Exception):
    """
    Raised when plugin registration fails.
    
    This exception is raised when a plugin cannot be registered due to:
    - Plugin class validation failures
    - Circular dependency detection
    - Duplicate plugin name conflicts
    - Metadata validation errors
    """
    
    def __init__(self, message: str, plugin_name: str = None, plugin_class: type = None, original_exception: Exception = None):
        """
        Initialize the PluginRegistrationError.
        
        Args:
            message: Descriptive error message
            plugin_name: Name of the plugin that failed to register (optional)
            plugin_class: Class of the plugin that failed to register (optional)  
            original_exception: The underlying exception that caused this error (optional)
        """
        super().__init__(message)
        self.plugin_name = plugin_name
        self.plugin_class = plugin_class
        self.original_exception = original_exception


class PluginRegistry:
    """
    Thread-safe singleton registry for validator plugins.
    
    Provides dynamic plugin discovery, registration, dependency resolution,
    and version compatibility checking with configurable behavior.
    """
    
    _instance: Optional['PluginRegistry'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'PluginRegistry':
        """Ensure singleton pattern."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self) -> None:
        """Initialize registry if not already done."""
        if not getattr(self, '_initialized', False):
            self._plugins: Dict[str, Type[IValidatorPlugin]] = {}
            self._metadata: Dict[str, PluginMetadata] = {}
            self._dependencies: Dict[str, Set[str]] = {}
            self._config: Dict[str, Any] = {}
            self._registry_lock = threading.RLock()
            self._logger = logging.getLogger(__name__)
            self._discovery_cache: Dict[str, float] = {}  # path -> timestamp
            self._load_config()
            self._initialized = True
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        config_path = Path("config/governance/plugin_registry.yaml")
        
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
        
        self._logger.info(f"Plugin registry configured with {len(self._config.get('plugin_directories', []))} directories")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'plugin_directories': [
                'libs/governance/plugins/validators',
                'libs/governance/plugins/custom'
            ],
            'discovery': {
                'recursive': True,
                'file_pattern': '*_plugin.py',
                'exclude_patterns': ['test_*.py', '__pycache__']
            },
            'validation': {
                'strict_mode': True,
                'require_metadata': True
            },
            'timeout': {
                'discovery_seconds': 5,
                'initialization_seconds': 10
            },
            'logging': {
                'level': 'INFO',
                'plugin_events': True
            }
        }
    
    def register(self, plugin_class: Type[IValidatorPlugin], metadata: Optional[PluginMetadata] = None) -> bool:
        """
        Register a plugin class with optional metadata override.
        
        Args:
            plugin_class: Plugin class implementing IValidatorPlugin
            metadata: Optional metadata override
            
        Returns:
            True if registration successful, False otherwise
            
        Raises:
            PluginRegistrationError: If registration fails due to validation errors
        """
        with self._registry_lock:
            try:
                # Validate plugin class
                if not self._validate_plugin_class(plugin_class):
                    raise PluginRegistrationError(
                        f"Invalid plugin class: {plugin_class.__name__}",
                        plugin_name=getattr(plugin_class, '__name__', 'Unknown'),
                        plugin_class=plugin_class
                    )
                
                # Get metadata from class or use override
                if metadata is None:
                    metadata = self._extract_metadata(plugin_class)
                
                plugin_name = metadata.name
                
                # Check for duplicates
                if plugin_name in self._plugins:
                    if not self._config.get('validation', {}).get('allow_overrides', False):
                        raise PluginRegistrationError(
                            f"Plugin already registered: {plugin_name}",
                            plugin_name=plugin_name,
                            plugin_class=plugin_class
                        )
                    self._logger.warning(f"Overriding existing plugin: {plugin_name}")
                
                # Register plugin
                self._plugins[plugin_name] = plugin_class
                self._metadata[plugin_name] = metadata
                self._dependencies[plugin_name] = set(metadata.dependencies)
                
                # Validate dependency graph
                if self._has_circular_dependencies(plugin_name):
                    # Rollback registration
                    del self._plugins[plugin_name]
                    del self._metadata[plugin_name]
                    del self._dependencies[plugin_name]
                    raise PluginRegistrationError(
                        f"Circular dependency detected for plugin: {plugin_name}",
                        plugin_name=plugin_name,
                        plugin_class=plugin_class
                    )
                
                self._logger.info(f"Successfully registered plugin: {plugin_name} v{metadata.version}")
                return True
                
            except Exception as e:
                self._logger.error(f"Failed to register plugin {plugin_class.__name__}: {e}")
                if isinstance(e, PluginRegistrationError):
                    raise
                raise PluginRegistrationError(
                    f"Registration failed: {e}",
                    plugin_name=getattr(metadata, 'name', 'Unknown') if metadata else 'Unknown',
                    plugin_class=plugin_class,
                    original_exception=e
                ) from e
    
    def unregister(self, plugin_name: str) -> bool:
        """
        Unregister a plugin by name.
        
        Args:
            plugin_name: Name of plugin to unregister
            
        Returns:
            True if unregistration successful, False if plugin not found
        """
        with self._registry_lock:
            try:
                if plugin_name not in self._plugins:
                    self._logger.warning(f"Plugin not found for unregistration: {plugin_name}")
                    return False
                
                # Check for dependent plugins
                dependents = self._get_dependent_plugins(plugin_name)
                if dependents and self._config.get('validation', {}).get('strict_mode', True):
                    self._logger.error(f"Cannot unregister {plugin_name}, required by: {', '.join(dependents)}")
                    return False
                
                # Remove plugin
                del self._plugins[plugin_name]
                del self._metadata[plugin_name]
                del self._dependencies[plugin_name]
                
                self._logger.info(f"Successfully unregistered plugin: {plugin_name}")
                return True
                
            except Exception as e:
                self._logger.error(f"Failed to unregister plugin {plugin_name}: {e}")
                return False
    
    def get_plugin(self, name: str) -> Optional[Type[IValidatorPlugin]]:
        """
        Get a plugin class by name.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin class if found, None otherwise
        """
        with self._registry_lock:
            return self._plugins.get(name)
    
    def list_plugins(self) -> List[PluginMetadata]:
        """
        Get list of all registered plugin metadata.
        
        Returns:
            List of plugin metadata objects
        """
        with self._registry_lock:
            return list(self._metadata.values())
    
    def discover_plugins(self, directories: Optional[List[str]] = None) -> int:
        """
        Discover and register plugins from directories.
        
        Args:
            directories: List of directories to search, defaults to config
            
        Returns:
            Number of plugins discovered and registered
            
        Raises:
            PluginDiscoveryError: If discovery fails
        """
        if directories is None:
            directories = self._config.get('plugin_directories', [])
        
        discovered_count = 0
        timeout = self._config.get('timeout', {}).get('discovery_seconds', 5)
        
        try:
            with ThreadPoolExecutor(max_workers=4) as executor:
                future = executor.submit(self._discover_plugins_sync, directories)
                discovered_count = future.result(timeout=timeout)
                
        except TimeoutError:
            raise PluginDiscoveryError(
                f"Plugin discovery timed out after {timeout} seconds",
                plugin_path=str(directories)
            )
        except Exception as e:
            raise PluginDiscoveryError(
                f"Plugin discovery failed: {e}",
                plugin_path=str(directories),
                original_exception=e
            ) from e
        
        return discovered_count
    
    def _discover_plugins_sync(self, directories: List[str]) -> int:
        """Synchronous plugin discovery implementation."""
        discovered_count = 0
        discovery_config = self._config.get('discovery', {})
        file_pattern = discovery_config.get('file_pattern', '*_plugin.py')
        exclude_patterns = discovery_config.get('exclude_patterns', [])
        recursive = discovery_config.get('recursive', True)
        
        for directory in directories:
            try:
                directory_path = Path(directory)
                if not directory_path.exists():
                    self._logger.warning(f"Plugin directory not found: {directory}")
                    continue
                
                # Find plugin files
                pattern = f"**/{file_pattern}" if recursive else file_pattern
                plugin_files = list(directory_path.glob(pattern))
                
                # Filter excluded patterns
                for exclude_pattern in exclude_patterns:
                    plugin_files = [f for f in plugin_files if not f.match(exclude_pattern)]
                
                self._logger.debug(f"Found {len(plugin_files)} plugin files in {directory}")
                
                # Process each plugin file
                for plugin_file in plugin_files:
                    try:
                        if self._load_plugin_from_file(plugin_file):
                            discovered_count += 1
                    except Exception as e:
                        self._logger.error(f"Failed to load plugin from {plugin_file}: {e}")
                        continue
                        
            except Exception as e:
                self._logger.error(f"Failed to discover plugins in directory {directory}: {e}")
                continue
        
        self._logger.info(f"Plugin discovery completed: {discovered_count} plugins registered")
        return discovered_count
    
    def _load_plugin_from_file(self, plugin_file: Path) -> bool:
        """Load and register plugin from a file."""
        try:
            # Create module spec
            module_name = plugin_file.stem
            spec = importlib.util.spec_from_file_location(module_name, plugin_file)
            
            if spec is None or spec.loader is None:
                self._logger.warning(f"Could not create module spec for {plugin_file}")
                return False
            
            # Import module
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin classes in module
            plugin_classes = self._find_plugin_classes(module)
            
            if not plugin_classes:
                self._logger.debug(f"No plugin classes found in {plugin_file}")
                return False
            
            # Register each plugin class
            registered = False
            for plugin_class in plugin_classes:
                try:
                    if self.register(plugin_class):
                        registered = True
                except PluginRegistrationError as e:
                    self._logger.warning(f"Failed to register {plugin_class.__name__}: {e}")
                    continue
            
            return registered
            
        except Exception as e:
            self._logger.error(f"Error loading plugin from {plugin_file}: {e}")
            return False
    
    def _find_plugin_classes(self, module) -> List[Type[IValidatorPlugin]]:
        """Find plugin classes in a module."""
        plugin_classes = []
        
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (obj.__module__ == module.__name__ and
                issubclass(obj, IValidatorPlugin) and
                obj is not IValidatorPlugin):
                plugin_classes.append(obj)
        
        return plugin_classes
    
    def resolve_dependencies(self, plugin_name: str) -> List[str]:
        """
        Resolve plugin dependencies in correct order.
        
        Args:
            plugin_name: Plugin name to resolve dependencies for
            
        Returns:
            Ordered list of plugin names (dependencies first)
            
        Raises:
            ValueError: If plugin not found or circular dependency detected
        """
        with self._registry_lock:
            if plugin_name not in self._plugins:
                raise ValueError(f"Plugin not found: {plugin_name}")
            
            if self._has_circular_dependencies(plugin_name):
                raise ValueError(f"Circular dependency detected for: {plugin_name}")
            
            resolved = []
            visited = set()
            
            def resolve_recursive(name: str):
                if name in visited:
                    return
                
                visited.add(name)
                
                if name in self._dependencies:
                    for dependency in self._dependencies[name]:
                        if dependency in self._plugins:
                            resolve_recursive(dependency)
                
                if name not in resolved:
                    resolved.append(name)
            
            resolve_recursive(plugin_name)
            return resolved
    
    def check_circular_dependencies(self, plugin_name: str) -> bool:
        """
        Check if plugin has circular dependencies.
        
        Args:
            plugin_name: Plugin name to check
            
        Returns:
            True if circular dependencies detected
        """
        with self._registry_lock:
            return self._has_circular_dependencies(plugin_name)
    
    def _has_circular_dependencies(self, plugin_name: str, visited: Optional[Set[str]] = None) -> bool:
        """Internal circular dependency check."""
        if visited is None:
            visited = set()
        
        if plugin_name in visited:
            return True
        
        if plugin_name not in self._dependencies:
            return False
        
        visited.add(plugin_name)
        
        for dependency in self._dependencies[plugin_name]:
            if self._has_circular_dependencies(dependency, visited.copy()):
                return True
        
        return False
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get the complete dependency graph.
        
        Returns:
            Dictionary mapping plugin names to their dependencies
        """
        with self._registry_lock:
            return {name: list(deps) for name, deps in self._dependencies.items()}
    
    def check_version_compatibility(self, plugin_name: str, required_version: str) -> bool:
        """
        Check if plugin version is compatible with required version.
        
        Args:
            plugin_name: Plugin name
            required_version: Required version specification (e.g., ">=1.0.0", "~1.2.0")
            
        Returns:
            True if version is compatible
        """
        with self._registry_lock:
            if plugin_name not in self._metadata:
                return False
            
            current_version = self._metadata[plugin_name].version
            return self._check_version_spec(current_version, required_version)
    
    def _check_version_spec(self, current: str, required: str) -> bool:
        """Check if current version satisfies required version spec."""
        try:
            current_parts = self._parse_version(current)
            
            # Handle different requirement formats
            if required.startswith('>='):
                required_parts = self._parse_version(required[2:])
                return current_parts >= required_parts
            elif required.startswith('>'):
                required_parts = self._parse_version(required[1:])
                return current_parts > required_parts
            elif required.startswith('<='):
                required_parts = self._parse_version(required[2:])
                return current_parts <= required_parts
            elif required.startswith('<'):
                required_parts = self._parse_version(required[1:])
                return current_parts < required_parts
            elif required.startswith('~'):
                # Compatible version (~1.2.0 allows 1.2.x but not 1.3.0)
                required_parts = self._parse_version(required[1:])
                return (current_parts[:2] == required_parts[:2] and 
                       current_parts >= required_parts)
            elif required.startswith('^'):
                # Caret version (^1.2.0 allows 1.x.x but not 2.0.0)
                required_parts = self._parse_version(required[1:])
                return (current_parts[0] == required_parts[0] and
                       current_parts >= required_parts)
            else:
                # Exact version
                required_parts = self._parse_version(required)
                return current_parts == required_parts
                
        except ValueError:
            return False
    
    def _parse_version(self, version: str) -> tuple:
        """Parse semantic version string into comparable tuple."""
        # Remove any prefixes and split on dots
        clean_version = re.sub(r'^[v=]', '', version.strip())
        parts = clean_version.split('.')
        
        if len(parts) < 2:
            raise ValueError(f"Invalid version format: {version}")
        
        # Convert to integers, pad to 3 parts
        try:
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            return (major, minor, patch)
        except ValueError:
            raise ValueError(f"Invalid version format: {version}")
    
    def _validate_plugin_class(self, plugin_class: Type) -> bool:
        """Validate that a class is a proper plugin."""
        if not inspect.isclass(plugin_class):
            return False
        
        if not issubclass(plugin_class, IValidatorPlugin):
            return False
        
        # Check for required methods
        required_methods = ['initialize', 'validate', 'configure', 'teardown']
        for method_name in required_methods:
            if not hasattr(plugin_class, method_name):
                return False
        
        return True
    
    def _extract_metadata(self, plugin_class: Type[IValidatorPlugin]) -> PluginMetadata:
        """Extract metadata from plugin class."""
        # Try to get metadata from class
        if hasattr(plugin_class, 'METADATA'):
            metadata = plugin_class.METADATA
            if isinstance(metadata, PluginMetadata):
                return metadata
        
        # Try to get metadata from instance (temporary)
        try:
            temp_instance = plugin_class(PluginMetadata(
                name=plugin_class.__name__,
                version="0.0.0",
                description="Temporary instance for metadata extraction",
                author="Unknown",
                license="Unknown"
            ))
            
            if hasattr(temp_instance, 'metadata'):
                return temp_instance.metadata
                
        except Exception:
            pass
        
        # Fall back to class inspection
        return PluginMetadata(
            name=getattr(plugin_class, '__plugin_name__', plugin_class.__name__),
            version=getattr(plugin_class, '__version__', '1.0.0'),
            description=getattr(plugin_class, '__doc__', '').strip() or 'No description available',
            author=getattr(plugin_class, '__author__', 'Unknown'),
            license=getattr(plugin_class, '__license__', 'Unknown'),
            tags=getattr(plugin_class, '__tags__', []),
            dependencies=getattr(plugin_class, '__dependencies__', [])
        )
    
    def _get_dependent_plugins(self, plugin_name: str) -> List[str]:
        """Get list of plugins that depend on the given plugin."""
        dependents = []
        
        for name, deps in self._dependencies.items():
            if plugin_name in deps:
                dependents.append(name)
        
        return dependents
    
    def clear(self) -> None:
        """Clear all registered plugins (for testing)."""
        with self._registry_lock:
            self._plugins.clear()
            self._metadata.clear()
            self._dependencies.clear()
            self._discovery_cache.clear()
            self._logger.info("Plugin registry cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        with self._registry_lock:
            return {
                'total_plugins': len(self._plugins),
                'plugin_names': list(self._plugins.keys()),
                'total_dependencies': sum(len(deps) for deps in self._dependencies.values()),
                'config_directories': self._config.get('plugin_directories', []),
                'cache_size': len(self._discovery_cache)
            }