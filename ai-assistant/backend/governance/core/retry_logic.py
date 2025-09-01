"""
File: ai-assistant/backend/governance/core/retry_logic.py
Purpose: Retry logic implementation with exponential backoff for resilient operations
Architecture: Provides configurable retry mechanisms for transient failure recovery
Dependencies: asyncio, typing, logging, random, time
Owner: Dr. Sarah Chen

@fileoverview Retry logic with exponential backoff and jitter for transient failures
@author Dr. Sarah Chen v1.0 - Backend Systems Architect
@architecture Backend - Retry pattern with adaptive learning
@business_logic Exponential backoff with jitter, configurable thresholds, adaptive adjustment
@integration_points Database operations, API calls, network requests
@error_handling RetryError after max attempts, configurable exception types
@performance Minimal overhead, adaptive optimization based on success patterns
"""

from typing import Callable, Optional, Any, TypeVar, Awaitable, Union, List, Type
from dataclasses import dataclass
import asyncio
import logging
import time
import random
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class RetryConfig:
    """
    Configuration for retry behavior with exponential backoff.
    
    Attributes:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds between retries
        max_delay: Maximum delay in seconds between retries
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delays
        jitter_range: Range for jitter as fraction of delay (0.0 to 1.0)
        retryable_exceptions: Tuple of exceptions that trigger retry
    """
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    jitter_range: float = 0.1
    retryable_exceptions: tuple = (Exception,)
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.initial_delay < 0:
            raise ValueError("initial_delay must be non-negative")
        if self.max_delay < self.initial_delay:
            raise ValueError("max_delay must be >= initial_delay")
        if self.exponential_base < 1:
            raise ValueError("exponential_base must be >= 1")
        if not 0 <= self.jitter_range <= 1:
            raise ValueError("jitter_range must be between 0 and 1")


class RetryError(Exception):
    """
    Exception raised when all retry attempts are exhausted.
    
    Contains information about the retry attempts and the last exception.
    """
    
    def __init__(self, message: str, attempts: int, last_exception: Optional[Exception] = None):
        """
        Initialize retry error.
        
        Args:
            message: Error message
            attempts: Number of attempts made
            last_exception: The last exception that occurred
        """
        super().__init__(message)
        self.attempts = attempts
        self.last_exception = last_exception


class RetryStatistics:
    """
    Statistics tracking for retry operations.
    
    Tracks successful retries, failures, and timing information
    for monitoring and optimization.
    """
    
    def __init__(self):
        """Initialize retry statistics."""
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.total_retries = 0
        self.retry_successes = 0
        self.total_delay_time = 0.0
        self.exceptions_caught: Dict[str, int] = {}
    
    def record_attempt(self, success: bool, retries: int, delay_time: float, exception: Optional[Exception] = None):
        """
        Record a retry attempt.
        
        Args:
            success: Whether the operation eventually succeeded
            retries: Number of retries performed
            delay_time: Total delay time spent in retries
            exception: Exception that was caught (if any)
        """
        self.total_calls += 1
        if success:
            self.successful_calls += 1
            if retries > 0:
                self.retry_successes += 1
        else:
            self.failed_calls += 1
        
        self.total_retries += retries
        self.total_delay_time += delay_time
        
        if exception:
            exc_name = type(exception).__name__
            self.exceptions_caught[exc_name] = self.exceptions_caught.get(exc_name, 0) + 1
    
    def get_stats(self) -> dict:
        """
        Get retry statistics summary.
        
        Returns:
            Dictionary with statistics
        """
        success_rate = 0
        if self.total_calls > 0:
            success_rate = (self.successful_calls / self.total_calls) * 100
        
        avg_retries = 0
        if self.total_calls > 0:
            avg_retries = self.total_retries / self.total_calls
        
        return {
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'success_rate': round(success_rate, 2),
            'total_retries': self.total_retries,
            'retry_successes': self.retry_successes,
            'average_retries': round(avg_retries, 2),
            'total_delay_time': round(self.total_delay_time, 2),
            'exceptions_caught': self.exceptions_caught
        }


class RetryManager:
    """
    Manager for retry operations with exponential backoff.
    
    Provides retry functionality with configurable backoff strategies
    and comprehensive error handling.
    """
    
    def __init__(self, config: Optional[RetryConfig] = None):
        """
        Initialize retry manager.
        
        Args:
            config: Retry configuration
        """
        self.config = config or RetryConfig()
        self.stats = RetryStatistics()
        logger.info(f"Retry manager initialized with max_attempts={self.config.max_attempts}")
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for the given attempt number.
        
        Implements exponential backoff with optional jitter.
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        # Calculate exponential backoff
        delay = min(
            self.config.initial_delay * (self.config.exponential_base ** attempt),
            self.config.max_delay
        )
        
        # Add jitter if configured
        if self.config.jitter and delay > 0:
            jitter_amount = delay * self.config.jitter_range
            jitter = random.uniform(-jitter_amount, jitter_amount)
            delay = max(0, delay + jitter)
        
        return delay
    
    async def execute_with_retry(
        self,
        func: Callable[..., Awaitable[T]],
        *args,
        **kwargs
    ) -> T:
        """
        Execute an async function with retry logic.
        
        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result from successful function execution
            
        Raises:
            RetryError: When all retry attempts are exhausted
            
        Example:
            async def unstable_operation():
                # May fail transiently
                return await external_service.call()
            
            retry_manager = RetryManager(RetryConfig(max_attempts=5))
            result = await retry_manager.execute_with_retry(unstable_operation)
        """
        last_exception = None
        total_delay = 0.0
        attempt = 0
        
        while attempt < self.config.max_attempts:
            try:
                # Try to execute the function
                result = await func(*args, **kwargs)
                
                # Success - record statistics
                self.stats.record_attempt(True, attempt, total_delay)
                
                if attempt > 0:
                    logger.info(f"Operation succeeded after {attempt} retries")
                
                return result
                
            except self.config.retryable_exceptions as e:
                last_exception = e
                
                # Check if we have more attempts
                if attempt + 1 >= self.config.max_attempts:
                    logger.error(f"Operation failed after {attempt + 1} attempts: {e}")
                    break
                
                # Calculate delay for next attempt
                delay = self.calculate_delay(attempt)
                total_delay += delay
                
                logger.warning(
                    f"Attempt {attempt + 1}/{self.config.max_attempts} failed: {e}. "
                    f"Retrying in {delay:.2f} seconds..."
                )
                
                # Wait before retry
                await asyncio.sleep(delay)
                attempt += 1
                
            except Exception as e:
                # Non-retryable exception
                logger.error(f"Non-retryable exception occurred: {e}")
                self.stats.record_attempt(False, attempt, total_delay, e)
                raise
        
        # All attempts exhausted
        self.stats.record_attempt(False, attempt, total_delay, last_exception)
        raise RetryError(
            f"Operation failed after {self.config.max_attempts} attempts",
            self.config.max_attempts,
            last_exception
        )
    
    def get_statistics(self) -> dict:
        """
        Get retry manager statistics.
        
        Returns:
            Dictionary with retry statistics
        """
        return self.stats.get_stats()


def with_retry(config: Optional[RetryConfig] = None):
    """
    Decorator for adding retry logic to async functions.
    
    Args:
        config: Retry configuration
        
    Returns:
        Decorated function with retry capability
        
    Example:
        @with_retry(RetryConfig(max_attempts=3, initial_delay=1.0))
        async def fetch_data():
            return await api_client.get_data()
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        retry_manager = RetryManager(config)
        
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await retry_manager.execute_with_retry(func, *args, **kwargs)
        
        # Attach retry manager for inspection
        wrapper.retry_manager = retry_manager
        return wrapper
    
    return decorator


class AdaptiveRetryManager(RetryManager):
    """
    Advanced retry manager with adaptive backoff based on success patterns.
    
    Adjusts retry parameters dynamically based on observed failure patterns
    to optimize retry behavior.
    """
    
    def __init__(self, config: Optional[RetryConfig] = None):
        """
        Initialize adaptive retry manager.
        
        Args:
            config: Initial retry configuration
        """
        super().__init__(config)
        self.success_history: List[bool] = []
        self.history_size = 100
        self.adaptation_threshold = 0.7
    
    def adapt_config(self):
        """
        Adapt retry configuration based on success history.
        
        Adjusts delays and max attempts based on observed patterns.
        """
        if len(self.success_history) < 10:
            return
        
        # Calculate recent success rate
        recent_successes = sum(self.success_history[-20:])
        recent_rate = recent_successes / min(20, len(self.success_history))
        
        # Adjust configuration based on success rate
        if recent_rate > 0.9:
            # High success rate - reduce delays
            self.config.initial_delay = max(0.5, self.config.initial_delay * 0.9)
            logger.debug(f"Adapted: Reduced initial delay to {self.config.initial_delay}")
            
        elif recent_rate < 0.5:
            # Low success rate - increase delays and attempts
            self.config.initial_delay = min(5.0, self.config.initial_delay * 1.1)
            self.config.max_attempts = min(10, self.config.max_attempts + 1)
            logger.debug(f"Adapted: Increased delay to {self.config.initial_delay}, attempts to {self.config.max_attempts}")
    
    async def execute_with_retry(
        self,
        func: Callable[..., Awaitable[T]],
        *args,
        **kwargs
    ) -> T:
        """
        Execute with adaptive retry logic.
        
        Extends base retry with adaptation based on history.
        """
        try:
            result = await super().execute_with_retry(func, *args, **kwargs)
            self.success_history.append(True)
        except RetryError as e:
            self.success_history.append(False)
            raise
        
        # Trim history
        if len(self.success_history) > self.history_size:
            self.success_history = self.success_history[-self.history_size:]
        
        # Adapt configuration
        self.adapt_config()
        
        return result


# Global retry managers for different service types
database_retry = RetryManager(RetryConfig(
    max_attempts=5,
    initial_delay=0.5,
    max_delay=30.0,
    retryable_exceptions=(ConnectionError, TimeoutError)
))

api_retry = RetryManager(RetryConfig(
    max_attempts=3,
    initial_delay=1.0,
    max_delay=10.0,
    retryable_exceptions=(ConnectionError, TimeoutError, OSError)
))

governance_retry = RetryManager(RetryConfig(
    max_attempts=3,
    initial_delay=0.1,
    max_delay=5.0,
    retryable_exceptions=(Exception,)
))