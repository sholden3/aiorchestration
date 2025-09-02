"""
Circuit Breaker Pattern for Database Connections
Prevents repeated connection attempts when database is down

@author: Dr. Sarah Chen - Senior Backend/Systems Architect
@architecture: Resilience Pattern - Circuit Breaker
@business_logic: Prevents cascading failures by failing fast when external services are unavailable
@testing: Unit tests required for state transitions and timeout behavior
@integration: Used by DatabaseService to manage PostgreSQL connection attempts
"""

import asyncio
import time
from enum import Enum
from typing import Optional, Callable, Any
import logging

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Circuit broken, fast fail
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """
    Circuit breaker implementation to prevent cascading failures
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service is down, fail fast without attempting connection
    - HALF_OPEN: Testing if service has recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: int = 30,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying half-open
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call function through circuit breaker
        
        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception(f"Circuit breaker is OPEN. Service unavailable for {self._time_until_retry():.0f} more seconds")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
            
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call async function through circuit breaker
        
        Args:
            func: Async function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                time_left = self._time_until_retry()
                logger.warning(f"Circuit breaker is OPEN. Retry in {time_left:.0f} seconds")
                raise Exception(f"Circuit breaker is OPEN. Service unavailable for {time_left:.0f} more seconds")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
            
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try recovery"""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _time_until_retry(self) -> float:
        """Calculate seconds until retry is allowed"""
        if not self.last_failure_time:
            return 0
        elapsed = time.time() - self.last_failure_time
        return max(0, self.recovery_timeout - elapsed)
        
    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            logger.info("Circuit breaker recovered, entering CLOSED state")
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(f"Circuit breaker opened after {self.failure_count} failures")
        else:
            logger.warning(f"Circuit breaker failure {self.failure_count}/{self.failure_threshold}")
            
    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "time_until_retry": self._time_until_retry() if self.state == CircuitState.OPEN else 0
        }
        
    def reset(self):
        """Manually reset circuit breaker"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        logger.info("Circuit breaker manually reset")