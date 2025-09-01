"""
File: ai-assistant/backend/governance/core/circuit_breaker.py
Purpose: Circuit breaker pattern implementation for resilient service calls
Architecture: Provides fault tolerance and prevents cascading failures in governance system
Dependencies: asyncio, datetime, enum, typing, logging
Owner: Dr. Sarah Chen

@fileoverview Circuit breaker pattern for preventing cascading failures
@author Dr. Sarah Chen v1.0 - Backend Systems Architect
@architecture Backend - Resilience pattern implementation with 3-state model
@business_logic Monitors failures, opens circuit on threshold, auto-recovery with half-open testing
@integration_points Service calls, API requests, database operations
@error_handling CircuitOpenError when circuit open, configurable fallback
@performance O(1) state checks, minimal overhead (<1ms per call)
"""

from enum import Enum
from typing import Callable, Optional, Any, Dict, Awaitable
from datetime import datetime, timedelta
import asyncio
import logging
from dataclasses import dataclass, field
import time

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """
    Circuit breaker states following the standard pattern.
    
    CLOSED: Normal operation, requests pass through
    OPEN: Failures exceeded threshold, requests blocked
    HALF_OPEN: Testing if service recovered
    """
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """
    Configuration for circuit breaker behavior.
    
    Attributes:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before attempting recovery
        expected_exception: Exception type to catch (None = all exceptions)
        success_threshold: Successes needed in half-open to close circuit
        half_open_max_calls: Max concurrent calls in half-open state
    """
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception: Optional[type] = None
    success_threshold: int = 2
    half_open_max_calls: int = 3
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be at least 1")
        if self.recovery_timeout < 0:
            raise ValueError("recovery_timeout must be non-negative")
        if self.success_threshold < 1:
            raise ValueError("success_threshold must be at least 1")


@dataclass
class CircuitBreakerStats:
    """
    Statistics tracking for circuit breaker operation.
    
    Tracks successes, failures, and state transitions for monitoring
    and debugging purposes.
    """
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    state_transitions: list = field(default_factory=list)
    last_failure_time: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    
    def record_success(self):
        """Record a successful call."""
        self.total_calls += 1
        self.successful_calls += 1
        self.consecutive_successes += 1
        self.consecutive_failures = 0
    
    def record_failure(self):
        """Record a failed call."""
        self.total_calls += 1
        self.failed_calls += 1
        self.consecutive_failures += 1
        self.consecutive_successes = 0
        self.last_failure_time = datetime.utcnow()
    
    def record_rejection(self):
        """Record a rejected call (circuit open)."""
        self.rejected_calls += 1
    
    def record_state_transition(self, from_state: CircuitState, to_state: CircuitState):
        """Record a state transition."""
        self.state_transitions.append({
            'from': from_state.value,
            'to': to_state.value,
            'timestamp': datetime.utcnow().isoformat()
        })


class CircuitBreaker:
    """
    Circuit breaker implementation for protecting service calls.
    
    This class implements the circuit breaker pattern to prevent cascading
    failures and provide graceful degradation when services are unavailable.
    It follows the three-state model: CLOSED, OPEN, and HALF_OPEN.
    
    Example:
        breaker = CircuitBreaker(CircuitBreakerConfig(failure_threshold=3))
        
        async def risky_operation():
            return await external_service.call()
        
        try:
            result = await breaker.call(risky_operation)
        except CircuitOpenError:
            # Handle circuit open - use fallback
            result = get_cached_result()
    """
    
    def __init__(self, config: Optional[CircuitBreakerConfig] = None, name: str = "CircuitBreaker"):
        """
        Initialize circuit breaker with configuration.
        
        Args:
            config: Circuit breaker configuration
            name: Name for logging and identification
        """
        self.config = config or CircuitBreakerConfig()
        self.name = name
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats()
        self._last_open_time: Optional[float] = None
        self._half_open_calls = 0
        self._lock = asyncio.Lock()
        
        logger.info(f"Circuit breaker '{name}' initialized with threshold={self.config.failure_threshold}")
    
    async def call(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result from func if successful
            
        Raises:
            CircuitOpenError: If circuit is open
            Exception: Original exception if circuit is closed/half-open
        """
        async with self._lock:
            # Check circuit state and update if necessary
            self._update_state()
            
            if self.state == CircuitState.OPEN:
                self.stats.record_rejection()
                raise CircuitOpenError(f"Circuit breaker '{self.name}' is OPEN")
            
            if self.state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.config.half_open_max_calls:
                    self.stats.record_rejection()
                    raise CircuitOpenError(f"Circuit breaker '{self.name}' half-open limit reached")
                self._half_open_calls += 1
        
        # Execute the function
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure(e)
            raise
    
    async def _on_success(self):
        """Handle successful call."""
        async with self._lock:
            self.stats.record_success()
            
            if self.state == CircuitState.HALF_OPEN:
                if self.stats.consecutive_successes >= self.config.success_threshold:
                    self._transition_to(CircuitState.CLOSED)
                    logger.info(f"Circuit breaker '{self.name}' closed after recovery")
    
    async def _on_failure(self, exception: Exception):
        """Handle failed call."""
        # Check if this exception should trigger the breaker
        if self.config.expected_exception:
            if not isinstance(exception, self.config.expected_exception):
                return
        
        async with self._lock:
            self.stats.record_failure()
            
            if self.state == CircuitState.CLOSED:
                if self.stats.consecutive_failures >= self.config.failure_threshold:
                    self._transition_to(CircuitState.OPEN)
                    logger.warning(f"Circuit breaker '{self.name}' opened after {self.stats.consecutive_failures} failures")
            
            elif self.state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)
                logger.warning(f"Circuit breaker '{self.name}' reopened after failure in half-open state")
    
    def _update_state(self):
        """Update circuit state based on recovery timeout."""
        if self.state == CircuitState.OPEN:
            if self._last_open_time:
                elapsed = time.time() - self._last_open_time
                if elapsed >= self.config.recovery_timeout:
                    self._transition_to(CircuitState.HALF_OPEN)
                    logger.info(f"Circuit breaker '{self.name}' entering half-open state")
    
    def _transition_to(self, new_state: CircuitState):
        """
        Transition to a new state.
        
        Args:
            new_state: Target state
        """
        if new_state != self.state:
            old_state = self.state
            self.state = new_state
            self.stats.record_state_transition(old_state, new_state)
            
            if new_state == CircuitState.OPEN:
                self._last_open_time = time.time()
                self.stats.consecutive_failures = 0
            elif new_state == CircuitState.CLOSED:
                self._last_open_time = None
                self.stats.consecutive_successes = 0
                self._half_open_calls = 0
            elif new_state == CircuitState.HALF_OPEN:
                self._half_open_calls = 0
                self.stats.consecutive_successes = 0
    
    def get_state(self) -> CircuitState:
        """
        Get current circuit state.
        
        Returns:
            Current CircuitState
        """
        return self.state
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get circuit breaker statistics.
        
        Returns:
            Dictionary with statistics including:
                - state: Current state
                - total_calls: Total calls attempted
                - successful_calls: Successful calls
                - failed_calls: Failed calls
                - rejected_calls: Calls rejected due to open circuit
                - success_rate: Percentage of successful calls
                - last_failure: Last failure timestamp
        """
        success_rate = 0
        if self.stats.total_calls > 0:
            success_rate = (self.stats.successful_calls / self.stats.total_calls) * 100
        
        return {
            'name': self.name,
            'state': self.state.value,
            'total_calls': self.stats.total_calls,
            'successful_calls': self.stats.successful_calls,
            'failed_calls': self.stats.failed_calls,
            'rejected_calls': self.stats.rejected_calls,
            'success_rate': round(success_rate, 2),
            'consecutive_failures': self.stats.consecutive_failures,
            'consecutive_successes': self.stats.consecutive_successes,
            'last_failure': self.stats.last_failure_time.isoformat() if self.stats.last_failure_time else None,
            'state_transitions': self.stats.state_transitions[-10:]  # Last 10 transitions
        }
    
    def reset(self):
        """
        Reset circuit breaker to closed state.
        
        Use with caution - this forcibly closes the circuit regardless
        of recent failures.
        """
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats()
        self._last_open_time = None
        self._half_open_calls = 0
        logger.info(f"Circuit breaker '{self.name}' manually reset")


class CircuitOpenError(Exception):
    """
    Exception raised when circuit breaker is open.
    
    This exception indicates that the circuit breaker has detected
    too many failures and is preventing further calls to protect
    the system.
    """
    pass


class CircuitBreakerManager:
    """
    Manager for multiple circuit breakers in the system.
    
    Provides centralized management and monitoring of all circuit
    breakers in the application.
    """
    
    def __init__(self):
        """Initialize circuit breaker manager."""
        self.breakers: Dict[str, CircuitBreaker] = {}
        logger.info("Circuit breaker manager initialized")
    
    def register(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """
        Register a new circuit breaker.
        
        Args:
            name: Unique name for the breaker
            config: Configuration for the breaker
            
        Returns:
            Created CircuitBreaker instance
        """
        if name in self.breakers:
            logger.warning(f"Circuit breaker '{name}' already exists, returning existing instance")
            return self.breakers[name]
        
        breaker = CircuitBreaker(config, name)
        self.breakers[name] = breaker
        logger.info(f"Registered circuit breaker '{name}'")
        return breaker
    
    def get(self, name: str) -> Optional[CircuitBreaker]:
        """
        Get a circuit breaker by name.
        
        Args:
            name: Name of the breaker
            
        Returns:
            CircuitBreaker instance or None if not found
        """
        return self.breakers.get(name)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all circuit breakers.
        
        Returns:
            Dictionary mapping breaker names to their statistics
        """
        return {
            name: breaker.get_stats()
            for name, breaker in self.breakers.items()
        }
    
    def reset_all(self):
        """Reset all circuit breakers to closed state."""
        for name, breaker in self.breakers.items():
            breaker.reset()
        logger.info(f"Reset all {len(self.breakers)} circuit breakers")


# Global circuit breaker manager instance
circuit_breaker_manager = CircuitBreakerManager()