"""
Unified Base Patterns and Abstractions
Orchestrated Design: All three personas collaborated to eliminate boilerplate
Architecture: DRY principle, decorator patterns, base classes
"""

import asyncio
import logging
from typing import TypeVar, Generic, Optional, Dict, Any, Callable, Union, List
from functools import wraps
from datetime import datetime
from abc import ABC, abstractmethod
import asyncpg
from config import config

# Type variables for generic patterns
T = TypeVar('T')
R = TypeVar('R')

class OrchestrationResult(Generic[T]):
    """
    Unified result wrapper for all operations
    Eliminates repetitive success/error dict patterns
    """
    
    def __init__(
        self,
        success: bool,
        data: Optional[T] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
    
    @classmethod
    def ok(cls, data: T, **metadata) -> 'OrchestrationResult[T]':
        """Create successful result"""
        return cls(success=True, data=data, metadata=metadata)
    
    @classmethod
    def error(cls, error_msg: str, code: Optional[str] = None, **metadata) -> 'OrchestrationResult[T]':
        """Create error result"""
        meta = metadata
        if code:
            meta['error_code'] = code
        return cls(success=False, error=error_msg, metadata=meta)
    
    @classmethod
    def fail(cls, error: str, **metadata) -> 'OrchestrationResult[T]':
        """Create failed result"""
        return cls(success=False, error=error, metadata=metadata)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }

def orchestrated_error_handler(
    fallback_value: Any = None,
    log_errors: bool = True,
    persona: str = "system"
):
    """
    Decorator for unified error handling across all personas
    Dr. Sarah Chen: AI operation safety
    Marcus Rodriguez: Performance monitoring
    Emily Watson: User-friendly error messages
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> OrchestrationResult:
            start_time = datetime.now()
            logger = logging.getLogger(func.__module__)
            
            try:
                result = await func(*args, **kwargs)
                
                # Performance tracking (Marcus)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                if isinstance(result, OrchestrationResult):
                    result.metadata['execution_time'] = execution_time
                    result.metadata['persona'] = persona
                    return result
                else:
                    return OrchestrationResult.ok(
                        result,
                        execution_time=execution_time,
                        persona=persona
                    )
                    
            except Exception as e:
                if log_errors:
                    logger.error(f"[{persona}] Error in {func.__name__}: {e}")
                
                # User-friendly error (Emily)
                user_message = _get_user_friendly_error(str(e))
                
                return OrchestrationResult.fail(
                    user_message,
                    technical_error=str(e),
                    fallback=fallback_value,
                    persona=persona
                )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> OrchestrationResult:
            start_time = datetime.now()
            logger = logging.getLogger(func.__module__)
            
            try:
                result = func(*args, **kwargs)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                if isinstance(result, OrchestrationResult):
                    result.metadata['execution_time'] = execution_time
                    result.metadata['persona'] = persona
                    return result
                else:
                    return OrchestrationResult.ok(
                        result,
                        execution_time=execution_time,
                        persona=persona
                    )
                    
            except Exception as e:
                if log_errors:
                    logger.error(f"[{persona}] Error in {func.__name__}: {e}")
                
                user_message = _get_user_friendly_error(str(e))
                
                return OrchestrationResult.fail(
                    user_message,
                    technical_error=str(e),
                    fallback=fallback_value,
                    persona=persona
                )
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def _get_user_friendly_error(technical_error: str) -> str:
    """
    Emily Watson's contribution: Convert technical errors to user-friendly messages
    """
    error_mappings = {
        "connection refused": "Unable to connect to the service. Please check if all components are running.",
        "timeout": "The operation took too long. Please try again.",
        "permission denied": "You don't have permission to perform this action.",
        "not found": "The requested resource was not found.",
        "invalid": "The provided input is invalid. Please check and try again."
    }
    
    lower_error = technical_error.lower()
    for key, message in error_mappings.items():
        if key in lower_error:
            return message
    
    return "An unexpected error occurred. Please try again or contact support."

class DatabaseOperation(ABC):
    """
    Base class for database operations (Marcus Rodriguez)
    Eliminates repetitive connection pool and error handling code
    """
    
    def __init__(self, pool: Optional[asyncpg.Pool] = None):
        self.pool = pool
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @orchestrated_error_handler(fallback_value=None, persona="systems_performance")
    async def execute(self, *args, **kwargs) -> Any:
        """Execute database operation with automatic connection handling"""
        if not self.pool:
            return None
        
        async with self.pool.acquire() as conn:
            return await self._perform_operation(conn, *args, **kwargs)
    
    @abstractmethod
    async def _perform_operation(self, conn: asyncpg.Connection, *args, **kwargs) -> Any:
        """Implement specific database operation"""
        raise NotImplementedError("Subclasses must implement _perform_operation")

class MetricsCollectorBase(ABC):
    """
    Base class for metrics collection (Marcus Rodriguez)
    Eliminates repetitive metrics recording patterns
    """
    
    def __init__(self, window_size: int = None):
        self.window_size = window_size or config.systems.metrics_window_size
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def record_metric(self, metric_name: str, value: Union[int, float], metadata: Dict = None):
        """Unified metric recording"""
        timestamp = datetime.now()
        
        # Store in appropriate collection
        if not hasattr(self, f"_{metric_name}_collection"):
            setattr(self, f"_{metric_name}_collection", [])
        
        collection = getattr(self, f"_{metric_name}_collection")
        collection.append({
            'value': value,
            'timestamp': timestamp,
            'metadata': metadata or {}
        })
        
        # Maintain window size
        if len(collection) > self.window_size:
            collection.pop(0)
        
        self.logger.debug(f"Recorded {metric_name}: {value}")
    
    def get_metric_stats(self, metric_name: str) -> Dict[str, Any]:
        """Get statistics for a metric"""
        collection = getattr(self, f"_{metric_name}_collection", [])
        
        if not collection:
            return {'count': 0, 'average': 0, 'min': 0, 'max': 0}
        
        values = [item['value'] for item in collection]
        
        return {
            'count': len(values),
            'average': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'latest': values[-1] if values else 0
        }

class PersonaOperation(ABC):
    """
    Base class for persona-specific operations (Dr. Sarah Chen)
    Provides consistent interface for all persona operations
    """
    
    def __init__(self, persona_type: str):
        self.persona_type = persona_type
        self.logger = logging.getLogger(f"Persona.{persona_type}")
        self.confidence_threshold = config.ai.persona_confidence_threshold
    
    @abstractmethod
    async def analyze(self, input_data: Any) -> Dict[str, Any]:
        """Analyze input from persona perspective"""
        raise NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    def get_confidence(self, input_data: Any) -> float:
        """Calculate confidence score for this persona"""
        raise NotImplementedError("Subclasses must implement this method")
    
    @orchestrated_error_handler(persona="ai_integration")
    async def execute_with_validation(self, input_data: Any) -> OrchestrationResult:
        """Execute operation with confidence validation"""
        confidence = self.get_confidence(input_data)
        
        if confidence < self.confidence_threshold:
            return OrchestrationResult.fail(
                f"Low confidence ({confidence:.2f}) for {self.persona_type}",
                confidence=confidence,
                threshold=self.confidence_threshold
            )
        
        result = await self.analyze(input_data)
        
        return OrchestrationResult.ok(
            result,
            confidence=confidence,
            persona=self.persona_type
        )

class CacheOperation(ABC):
    """
    Base class for cache operations (Marcus Rodriguez + Dr. Sarah Chen)
    Unified caching interface across all components
    """
    
    @abstractmethod
    def generate_key(self, *args, **kwargs) -> str:
        """Generate cache key"""
        raise NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve from cache"""
        raise NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Store in cache"""
        raise NotImplementedError("Subclasses must implement this method")
    
    @orchestrated_error_handler(fallback_value=None, persona="systems_performance")
    async def get_or_compute(
        self,
        compute_func: Callable,
        *args,
        ttl: int = None,
        **kwargs
    ) -> Any:
        """Get from cache or compute if missing"""
        key = self.generate_key(*args, **kwargs)
        
        # Try cache first
        cached = await self.get(key)
        if cached is not None:
            return cached
        
        # Compute if not cached
        result = await compute_func(*args, **kwargs)
        
        # Store in cache
        if result is not None:
            await self.set(key, result, ttl or config.systems.cache_default_ttl_seconds)
        
        return result

class UIComponent(ABC):
    """
    Base class for UI components (Emily Watson)
    Provides consistent interface and accessibility
    """
    
    def __init__(self, component_id: str):
        self.component_id = component_id
        self.theme = config.ux.ui_theme
        self.accessibility_enabled = config.ux.accessibility_screen_reader
        self.logger = logging.getLogger(f"UI.{component_id}")
    
    @abstractmethod
    def render(self) -> Dict[str, Any]:
        """Render component data"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def get_aria_labels(self) -> Dict[str, str]:
        """Get accessibility labels"""
        return {
            'role': 'region',
            'aria-label': self.component_id,
            'aria-live': 'polite'
        }
    
    def get_theme_classes(self) -> List[str]:
        """Get theme-specific CSS classes"""
        base_classes = ['ui-component']
        
        if self.theme == 'dark':
            base_classes.extend(['dark-theme', 'bg-dark', 'text-light'])
        else:
            base_classes.extend(['light-theme', 'bg-light', 'text-dark'])
        
        if config.ux.accessibility_high_contrast:
            base_classes.append('high-contrast')
        
        return base_classes

# Singleton instances for common operations
class OrchestrationContext:
    """
    Global orchestration context
    Shared state and utilities for all personas
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.config = config
        self.logger = logging.getLogger("Orchestration")
        self.start_time = datetime.now()
        self._initialized = True
    
    def get_uptime(self) -> float:
        """Get application uptime in seconds"""
        return (datetime.now() - self.start_time).total_seconds()
    
    def log_orchestration_event(
        self,
        event_type: str,
        personas_involved: List[str],
        details: Dict[str, Any] = None
    ):
        """Log orchestration events for monitoring"""
        self.logger.info(
            f"Orchestration Event: {event_type}",
            extra={
                'personas': personas_involved,
                'details': details or {},
                'timestamp': datetime.now().isoformat()
            }
        )

# Global context instance
orchestration_context = OrchestrationContext()