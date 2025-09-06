"""
@fileoverview Retry mechanism with exponential backoff
@author Dr. Sarah Chen - Backend Architect
@architecture Shared Utils Library
@description Resilient retry patterns for network operations
"""

import asyncio
import time
from typing import TypeVar, Callable, Optional, Union, Any
from functools import wraps
from dataclasses import dataclass

T = TypeVar('T')


@dataclass
class RetryOptions:
    """Retry configuration options"""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 10.0
    backoff_multiplier: float = 2.0
    retry_condition: Optional[Callable[[Exception], bool]] = None
    on_retry: Optional[Callable[[int, Exception], None]] = None
    

class RetryError(Exception):
    """Exception raised when all retry attempts fail"""
    
    def __init__(self, message: str, attempts: int, last_error: Exception):
        super().__init__(message)
        self.attempts = attempts
        self.last_error = last_error


def retry_sync(
    func: Callable[..., T],
    *args,
    options: Optional[RetryOptions] = None,
    **kwargs
) -> T:
    """
    Retry a synchronous function with exponential backoff
    
    Sarah's Framework Check:
    - What breaks first: Network timeout
    - How we know: Connection exceptions
    - Plan B: Circuit breaker fallback
    """
    if options is None:
        options = RetryOptions()
    
    last_error: Optional[Exception] = None
    delay = options.initial_delay
    
    for attempt in range(1, options.max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            
            # Check if we should retry
            if attempt == options.max_attempts:
                break
                
            if options.retry_condition and not options.retry_condition(e):
                break
            
            # Notify retry listener
            if options.on_retry:
                options.on_retry(attempt, e)
            
            # Sleep with backoff
            time.sleep(delay)
            delay = min(delay * options.backoff_multiplier, options.max_delay)
    
    raise RetryError(
        f"Failed after {attempt} attempts: {str(last_error)}",
        attempt,
        last_error
    )


async def retry_async(
    func: Callable[..., T],
    *args,
    options: Optional[RetryOptions] = None,
    **kwargs
) -> T:
    """
    Retry an asynchronous function with exponential backoff
    """
    if options is None:
        options = RetryOptions()
    
    last_error: Optional[Exception] = None
    delay = options.initial_delay
    
    for attempt in range(1, options.max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_error = e
            
            # Check if we should retry
            if attempt == options.max_attempts:
                break
                
            if options.retry_condition and not options.retry_condition(e):
                break
            
            # Notify retry listener
            if options.on_retry:
                options.on_retry(attempt, e)
            
            # Sleep with backoff
            await asyncio.sleep(delay)
            delay = min(delay * options.backoff_multiplier, options.max_delay)
    
    raise RetryError(
        f"Failed after {attempt} attempts: {str(last_error)}",
        attempt,
        last_error
    )


def retryable(options: Optional[RetryOptions] = None):
    """
    Decorator for retrying functions
    
    Usage:
        @retryable(RetryOptions(max_attempts=5))
        def flaky_function():
            # Function that might fail
            pass
    """
    if options is None:
        options = RetryOptions()
    
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await retry_async(func, *args, options=options, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return retry_sync(func, *args, options=options, **kwargs)
            return sync_wrapper
    
    return decorator


class RetryPolicy:
    """
    Retry policy with circuit breaker integration
    """
    
    def __init__(
        self,
        max_attempts: int = 3,
        circuit_breaker_threshold: int = 10,
        circuit_breaker_timeout: float = 60.0
    ):
        self.max_attempts = max_attempts
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        self.failure_count = 0
        self.circuit_open_until: Optional[float] = None
    
    def is_circuit_open(self) -> bool:
        """Check if circuit breaker is open"""
        if self.circuit_open_until is None:
            return False
        
        if time.time() < self.circuit_open_until:
            return True
        
        # Circuit timeout expired, reset
        self.circuit_open_until = None
        self.failure_count = 0
        return False
    
    def record_success(self):
        """Record successful operation"""
        self.failure_count = 0
        self.circuit_open_until = None
    
    def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        
        if self.failure_count >= self.circuit_breaker_threshold:
            self.circuit_open_until = time.time() + self.circuit_breaker_timeout
    
    def should_retry(self, attempt: int) -> bool:
        """Determine if retry should be attempted"""
        if self.is_circuit_open():
            return False
        
        return attempt < self.max_attempts