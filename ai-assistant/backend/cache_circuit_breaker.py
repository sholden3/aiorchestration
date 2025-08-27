"""
FIX C2: Circuit breaker pattern for cache resilience
Architecture: Dr. Sarah Chen
Pattern: Circuit breaker with automatic recovery
"""
import time
import logging
from enum import Enum
from typing import TypeVar, Callable, Awaitable, Optional

try:
    from cache_errors import CacheCircuitBreakerOpenError
except ImportError:
    from .cache_errors import CacheCircuitBreakerOpenError

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failures exceeded threshold, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CacheCircuitBreaker:
    """
    Circuit breaker for cache operations
    Sarah's Three Questions Framework:
    1. What breaks first? Disk I/O operations
    2. How do we know? Track failure count and types
    3. What's Plan B? Bypass cache and serve from source
    """
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_time: int = 60,
                 test_requests: int = 3):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_time: Seconds to wait before testing recovery
            test_requests: Successful requests needed to close circuit
        """
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self.test_requests = test_requests
        
        # State tracking
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.success_count = 0
        self.total_opens = 0  # Track for metrics
        
    async def execute(self, operation: Callable[[], Awaitable[T]], 
                     fallback: Optional[Callable[[], Awaitable[T]]] = None) -> T:
        """
        Execute operation with circuit breaker protection
        
        Args:
            operation: The cache operation to execute
            fallback: Optional fallback operation if circuit is open
        """
        
        # Check if circuit should transition from OPEN to HALF_OPEN
        if (self.state == CircuitState.OPEN and 
            time.time() - self.last_failure_time > self.recovery_time):
            self.state = CircuitState.HALF_OPEN
            self.success_count = 0
            logger.info("Cache circuit breaker transitioning to HALF_OPEN")
        
        # Reject requests if circuit is OPEN
        if self.state == CircuitState.OPEN:
            if fallback:
                logger.debug("Circuit breaker OPEN - using fallback")
                return await fallback()
            raise CacheCircuitBreakerOpenError("Cache circuit breaker is OPEN")
        
        try:
            result = await operation()
            self.record_success()
            return result
            
        except Exception as e:
            self.record_failure()
            
            # If we have a fallback, use it
            if fallback:
                logger.debug(f"Operation failed, using fallback: {e}")
                return await fallback()
            raise
    
    def record_success(self):
        """Record successful operation"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.test_requests:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info("Cache circuit breaker CLOSED - recovery successful")
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success in closed state
            if self.failure_count > 0:
                self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if (self.state in [CircuitState.CLOSED, CircuitState.HALF_OPEN] and 
            self.failure_count >= self.failure_threshold):
            self.state = CircuitState.OPEN
            self.total_opens += 1
            logger.warning(f"Cache circuit breaker OPEN - {self.failure_count} failures")
    
    def is_open(self) -> bool:
        """Check if circuit breaker is open"""
        return self.state == CircuitState.OPEN
    
    def reset(self):
        """Reset circuit breaker to closed state"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logger.info("Cache circuit breaker manually reset")
    
    def get_state(self) -> dict:
        """Get circuit breaker state for monitoring"""
        return {
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time,
            'total_opens': self.total_opens,
            'is_healthy': self.state == CircuitState.CLOSED
        }