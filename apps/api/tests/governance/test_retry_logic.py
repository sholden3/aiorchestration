"""
File: ai-assistant/backend/tests/governance/test_retry_logic.py
Purpose: Unit tests for retry logic with exponential backoff
Architecture: Test suite validating retry mechanisms and backoff strategies
Dependencies: pytest, asyncio, unittest.mock
Owner: Maya Patel

@fileoverview Comprehensive unit tests for retry logic patterns
@author Maya Patel v1.0 - QA & Testing Lead
@architecture Testing - Unit test suite for retry mechanisms
@business_logic Validates exponential backoff, jitter, adaptive learning
@testing_strategy Failure simulation, timing validation, statistics verification
@coverage_target 100% for RetryManager and related classes
"""

import pytest
import asyncio
import time
import random
from unittest.mock import AsyncMock, Mock, patch

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from libs.governance.core.retry_logic import (
    RetryConfig,
    RetryError,
    RetryManager,
    RetryStatistics,
    with_retry,
    AdaptiveRetryManager
)


class TestRetryConfig:
    """
    Test suite for RetryConfig validation.
    
    Validates configuration parameters and constraints.
    """
    
    def test_default_config(self):
        """Test default retry configuration."""
        config = RetryConfig()
        assert config.max_attempts == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter == True
        assert config.jitter_range == 0.1
        assert config.retryable_exceptions == (Exception,)
    
    def test_custom_config(self):
        """Test custom retry configuration."""
        config = RetryConfig(
            max_attempts=5,
            initial_delay=0.5,
            max_delay=30.0,
            jitter=False,
            retryable_exceptions=(ValueError, TypeError)
        )
        assert config.max_attempts == 5
        assert config.initial_delay == 0.5
        assert config.max_delay == 30.0
        assert config.jitter == False
        assert config.retryable_exceptions == (ValueError, TypeError)
    
    def test_invalid_config(self):
        """Test configuration validation."""
        with pytest.raises(ValueError, match="max_attempts must be at least 1"):
            RetryConfig(max_attempts=0)
        
        with pytest.raises(ValueError, match="initial_delay must be non-negative"):
            RetryConfig(initial_delay=-1)
        
        with pytest.raises(ValueError, match="max_delay must be >= initial_delay"):
            RetryConfig(initial_delay=10, max_delay=5)
        
        with pytest.raises(ValueError, match="exponential_base must be >= 1"):
            RetryConfig(exponential_base=0.5)
        
        with pytest.raises(ValueError, match="jitter_range must be between 0 and 1"):
            RetryConfig(jitter_range=1.5)


class TestRetryManager:
    """
    Test suite for RetryManager core functionality.
    
    Tests retry behavior, backoff calculation, and error handling.
    """
    
    @pytest.fixture
    def retry_manager(self):
        """Create a retry manager with test configuration."""
        config = RetryConfig(
            max_attempts=3,
            initial_delay=0.1,
            max_delay=1.0,
            jitter=False  # Disable jitter for predictable tests
        )
        return RetryManager(config)
    
    def test_calculate_delay_exponential(self, retry_manager):
        """Test exponential backoff calculation."""
        # First attempt (0-based indexing)
        delay0 = retry_manager.calculate_delay(0)
        assert delay0 == 0.1
        
        # Second attempt
        delay1 = retry_manager.calculate_delay(1)
        assert delay1 == 0.2
        
        # Third attempt
        delay2 = retry_manager.calculate_delay(2)
        assert delay2 == 0.4
        
        # Max delay cap
        delay10 = retry_manager.calculate_delay(10)
        assert delay10 == 1.0  # Capped at max_delay
    
    def test_calculate_delay_with_jitter(self):
        """Test delay calculation with jitter."""
        config = RetryConfig(
            initial_delay=1.0,
            jitter=True,
            jitter_range=0.2
        )
        manager = RetryManager(config)
        
        # Jitter should add randomness
        delays = [manager.calculate_delay(1) for _ in range(10)]
        
        # All delays should be within jitter range
        for delay in delays:
            assert 1.6 <= delay <= 2.4  # 2.0 ± 20%
        
        # Delays should vary (not all the same)
        assert len(set(delays)) > 1
    
    @pytest.mark.asyncio
    async def test_successful_operation(self, retry_manager):
        """Test operation that succeeds on first attempt."""
        async def success_operation():
            return "success"
        
        result = await retry_manager.execute_with_retry(success_operation)
        assert result == "success"
        
        stats = retry_manager.get_statistics()
        assert stats['successful_calls'] == 1
        assert stats['failed_calls'] == 0
        assert stats['total_retries'] == 0
    
    @pytest.mark.asyncio
    async def test_retry_on_failure(self, retry_manager):
        """Test retry on transient failures."""
        attempt_count = 0
        
        async def flaky_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError("Transient failure")
            return f"success after {attempt_count} attempts"
        
        result = await retry_manager.execute_with_retry(flaky_operation)
        assert result == "success after 3 attempts"
        assert attempt_count == 3
        
        stats = retry_manager.get_statistics()
        assert stats['successful_calls'] == 1
        assert stats['total_retries'] == 2  # 2 retries after initial failure
    
    @pytest.mark.asyncio
    async def test_max_attempts_exceeded(self, retry_manager):
        """Test failure when max attempts exceeded."""
        async def always_failing():
            raise ValueError("Persistent failure")
        
        with pytest.raises(RetryError) as exc_info:
            await retry_manager.execute_with_retry(always_failing)
        
        assert "Operation failed after 3 attempts" in str(exc_info.value)
        assert exc_info.value.attempts == 3
        assert isinstance(exc_info.value.last_exception, ValueError)
        
        stats = retry_manager.get_statistics()
        assert stats['failed_calls'] == 1
        assert stats['total_retries'] == 2
    
    @pytest.mark.asyncio
    async def test_non_retryable_exception(self, retry_manager):
        """Test non-retryable exceptions are not retried."""
        config = RetryConfig(
            max_attempts=3,
            retryable_exceptions=(ValueError,)
        )
        manager = RetryManager(config)
        
        async def type_error_operation():
            raise TypeError("Non-retryable error")
        
        with pytest.raises(TypeError, match="Non-retryable error"):
            await manager.execute_with_retry(type_error_operation)
        
        # Should fail immediately without retries
        stats = manager.get_statistics()
        assert stats['failed_calls'] == 1
        assert stats['total_retries'] == 0
    
    @pytest.mark.asyncio
    async def test_retry_delay_timing(self, retry_manager):
        """Test that retry delays are applied correctly."""
        retry_manager.config.initial_delay = 0.05  # 50ms
        
        attempt_times = []
        
        async def timed_operation():
            attempt_times.append(time.time())
            if len(attempt_times) < 3:
                raise ValueError("Retry needed")
            return "success"
        
        start = time.time()
        result = await retry_manager.execute_with_retry(timed_operation)
        duration = time.time() - start
        
        assert result == "success"
        assert len(attempt_times) == 3
        
        # Check delays between attempts
        delay1 = attempt_times[1] - attempt_times[0]
        delay2 = attempt_times[2] - attempt_times[1]
        
        # First retry delay should be ~50ms
        assert 0.04 < delay1 < 0.06
        
        # Second retry delay should be ~100ms (exponential)
        assert 0.09 < delay2 < 0.11
    
    @pytest.mark.asyncio
    async def test_statistics_tracking(self, retry_manager):
        """Test comprehensive statistics tracking."""
        # Mix of successful and failed operations
        async def sometimes_failing():
            if not hasattr(sometimes_failing, 'count'):
                sometimes_failing.count = 0
            sometimes_failing.count += 1
            
            if sometimes_failing.count in [1, 4]:  # Fail on 1st and 4th call
                raise ValueError("Failure")
            return "success"
        
        # First call - fails then succeeds
        await retry_manager.execute_with_retry(sometimes_failing)
        
        # Second call - succeeds immediately
        await retry_manager.execute_with_retry(sometimes_failing)
        
        # Third call - exhausts retries
        with pytest.raises(RetryError):
            await retry_manager.execute_with_retry(sometimes_failing)
        
        stats = retry_manager.get_statistics()
        assert stats['total_calls'] == 3
        assert stats['successful_calls'] == 2
        assert stats['failed_calls'] == 1
        assert stats['success_rate'] == pytest.approx(66.67, 0.01)
        assert 'ValueError' in stats['exceptions_caught']


class TestRetryDecorator:
    """
    Test suite for @with_retry decorator.
    
    Tests decorator functionality and configuration.
    """
    
    @pytest.mark.asyncio
    async def test_decorator_basic(self):
        """Test basic decorator functionality."""
        call_count = 0
        
        @with_retry(RetryConfig(max_attempts=3, initial_delay=0.01))
        async def decorated_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Retry needed")
            return f"success_{call_count}"
        
        result = await decorated_function()
        assert result == "success_2"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_decorator_with_arguments(self):
        """Test decorator with function arguments."""
        @with_retry(RetryConfig(max_attempts=2, initial_delay=0.01))
        async def add_numbers(a, b):
            if not hasattr(add_numbers, 'attempt'):
                add_numbers.attempt = 0
            add_numbers.attempt += 1
            
            if add_numbers.attempt == 1:
                raise ValueError("First attempt fails")
            return a + b
        
        result = await add_numbers(5, 3)
        assert result == 8
    
    @pytest.mark.asyncio
    async def test_decorator_statistics_access(self):
        """Test accessing statistics through decorator."""
        @with_retry(RetryConfig(max_attempts=3, initial_delay=0.01))
        async def tracked_function():
            return "success"
        
        # Function should have retry_manager attached
        assert hasattr(tracked_function, 'retry_manager')
        
        await tracked_function()
        
        stats = tracked_function.retry_manager.get_statistics()
        assert stats['successful_calls'] == 1


class TestAdaptiveRetryManager:
    """
    Test suite for AdaptiveRetryManager with learning capabilities.
    
    Tests adaptive behavior based on success patterns.
    """
    
    @pytest.fixture
    def adaptive_manager(self):
        """Create an adaptive retry manager."""
        config = RetryConfig(
            max_attempts=3,
            initial_delay=1.0,
            jitter=False
        )
        return AdaptiveRetryManager(config)
    
    @pytest.mark.asyncio
    async def test_adaptation_on_high_success(self, adaptive_manager):
        """Test adaptation when success rate is high."""
        async def reliable_operation():
            return "success"
        
        # Simulate many successful operations
        for _ in range(25):
            await adaptive_manager.execute_with_retry(reliable_operation)
        
        # Initial delay should be reduced
        assert adaptive_manager.config.initial_delay < 1.0
    
    @pytest.mark.asyncio
    async def test_adaptation_on_low_success(self, adaptive_manager):
        """Test adaptation when success rate is low."""
        attempt = 0
        
        async def unreliable_operation():
            nonlocal attempt
            attempt += 1
            # Fail most of the time
            if attempt % 3 != 0:
                raise ValueError("Failure")
            return "success"
        
        # Simulate mixed success/failure
        for i in range(15):
            try:
                await adaptive_manager.execute_with_retry(unreliable_operation)
            except RetryError:
                pass
        
        # Initial delay should be increased
        assert adaptive_manager.config.initial_delay > 1.0
        # Max attempts might be increased
        assert adaptive_manager.config.max_attempts >= 3
    
    @pytest.mark.asyncio
    async def test_history_management(self, adaptive_manager):
        """Test success history management."""
        async def simple_operation():
            return "success"
        
        # Fill history beyond limit
        for _ in range(150):
            await adaptive_manager.execute_with_retry(simple_operation)
        
        # History should be trimmed
        assert len(adaptive_manager.success_history) <= 100


class TestRetryIntegration:
    """
    Integration tests for retry logic with real async scenarios.
    
    Tests retry behavior in realistic conditions.
    """
    
    @pytest.mark.asyncio
    async def test_concurrent_retries(self):
        """Test multiple retry managers working concurrently."""
        config = RetryConfig(
            max_attempts=3,
            initial_delay=0.01,
            jitter=True
        )
        
        managers = [RetryManager(config) for _ in range(5)]
        
        async def operation(manager_id):
            if not hasattr(operation, 'attempts'):
                operation.attempts = {}
            
            if manager_id not in operation.attempts:
                operation.attempts[manager_id] = 0
            
            operation.attempts[manager_id] += 1
            
            if operation.attempts[manager_id] < 2:
                raise ValueError(f"Manager {manager_id} retry needed")
            
            return f"Manager {manager_id} success"
        
        # Run concurrent retry operations
        tasks = [
            managers[i].execute_with_retry(operation, i)
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all("success" in r for r in results)
    
    @pytest.mark.asyncio
    async def test_timeout_with_retry(self):
        """Test retry with timeout handling."""
        config = RetryConfig(
            max_attempts=3,
            initial_delay=0.01
        )
        manager = RetryManager(config)
        
        async def slow_operation():
            await asyncio.sleep(10)
            return "success"
        
        async def timeout_wrapper():
            return await asyncio.wait_for(slow_operation(), timeout=0.05)
        
        with pytest.raises(RetryError) as exc_info:
            await manager.execute_with_retry(timeout_wrapper)
        
        assert isinstance(exc_info.value.last_exception, asyncio.TimeoutError)
        assert exc_info.value.attempts == 3
    
    @pytest.mark.asyncio
    async def test_retry_performance(self):
        """Test retry manager performance overhead."""
        config = RetryConfig(
            max_attempts=1,  # No actual retries
            jitter=False
        )
        manager = RetryManager(config)
        
        async def fast_operation():
            return "result"
        
        start = time.perf_counter()
        for _ in range(1000):
            await manager.execute_with_retry(fast_operation)
        duration = time.perf_counter() - start
        
        # Should handle 1000 operations quickly
        assert duration < 0.5
        
        stats = manager.get_statistics()
        assert stats['successful_calls'] == 1000
        assert stats['total_retries'] == 0