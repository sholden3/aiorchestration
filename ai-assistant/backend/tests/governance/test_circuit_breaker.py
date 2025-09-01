"""
File: ai-assistant/backend/tests/governance/test_circuit_breaker.py
Purpose: Unit tests for circuit breaker implementation
Architecture: Test suite validating circuit breaker state transitions and fault tolerance
Dependencies: pytest, asyncio, unittest.mock
Owner: Maya Patel

@fileoverview Comprehensive unit tests for circuit breaker pattern
@author Maya Patel v1.0 - QA & Testing Lead
@architecture Testing - Unit test suite for resilience patterns
@business_logic Validates circuit states, thresholds, recovery, and statistics
@testing_strategy State transition testing, failure simulation, recovery validation
@coverage_target 100% for CircuitBreaker class
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from governance.core.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    CircuitOpenError,
    CircuitBreakerManager,
    circuit_breaker_manager
)


class TestCircuitBreakerConfig:
    """
    Test suite for CircuitBreakerConfig validation.
    
    Validates configuration parameter constraints and defaults.
    """
    
    def test_default_config(self):
        """Test default configuration values."""
        config = CircuitBreakerConfig()
        assert config.failure_threshold == 5
        assert config.recovery_timeout == 60.0
        assert config.expected_exception is None
        assert config.success_threshold == 2
        assert config.half_open_max_calls == 3
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30.0,
            success_threshold=1
        )
        assert config.failure_threshold == 3
        assert config.recovery_timeout == 30.0
        assert config.success_threshold == 1
    
    def test_invalid_config(self):
        """Test configuration validation."""
        with pytest.raises(ValueError, match="failure_threshold must be at least 1"):
            CircuitBreakerConfig(failure_threshold=0)
        
        with pytest.raises(ValueError, match="recovery_timeout must be non-negative"):
            CircuitBreakerConfig(recovery_timeout=-1)
        
        with pytest.raises(ValueError, match="success_threshold must be at least 1"):
            CircuitBreakerConfig(success_threshold=0)


class TestCircuitBreaker:
    """
    Test suite for CircuitBreaker core functionality.
    
    Tests state transitions, failure handling, and recovery behavior.
    """
    
    @pytest.fixture
    def breaker(self):
        """Create a circuit breaker with test configuration."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=1.0,
            success_threshold=1
        )
        return CircuitBreaker(config, name="TestBreaker")
    
    @pytest.mark.asyncio
    async def test_initial_state(self, breaker):
        """Test circuit breaker starts in closed state."""
        assert breaker.get_state() == CircuitState.CLOSED
        stats = breaker.get_stats()
        assert stats['state'] == 'closed'
        assert stats['total_calls'] == 0
    
    @pytest.mark.asyncio
    async def test_successful_calls(self, breaker):
        """Test successful calls don't open circuit."""
        async def success_operation():
            return "success"
        
        # Multiple successful calls
        for i in range(5):
            result = await breaker.call(success_operation)
            assert result == "success"
        
        assert breaker.get_state() == CircuitState.CLOSED
        stats = breaker.get_stats()
        assert stats['successful_calls'] == 5
        assert stats['failed_calls'] == 0
    
    @pytest.mark.asyncio
    async def test_circuit_opens_on_failures(self, breaker):
        """Test circuit opens after threshold failures."""
        async def failing_operation():
            raise Exception("Test failure")
        
        # First failure
        with pytest.raises(Exception, match="Test failure"):
            await breaker.call(failing_operation)
        
        assert breaker.get_state() == CircuitState.CLOSED
        
        # Second failure (threshold reached)
        with pytest.raises(Exception, match="Test failure"):
            await breaker.call(failing_operation)
        
        assert breaker.get_state() == CircuitState.OPEN
        stats = breaker.get_stats()
        assert stats['failed_calls'] == 2
    
    @pytest.mark.asyncio
    async def test_circuit_open_rejects_calls(self, breaker):
        """Test open circuit rejects calls immediately."""
        async def failing_operation():
            raise Exception("Test failure")
        
        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await breaker.call(failing_operation)
        
        assert breaker.get_state() == CircuitState.OPEN
        
        # Subsequent calls should be rejected
        with pytest.raises(CircuitOpenError, match="Circuit breaker 'TestBreaker' is OPEN"):
            await breaker.call(failing_operation)
        
        stats = breaker.get_stats()
        assert stats['rejected_calls'] == 1
    
    @pytest.mark.asyncio
    async def test_half_open_recovery(self, breaker):
        """Test circuit recovery through half-open state."""
        async def operation():
            if hasattr(operation, 'should_fail') and operation.should_fail:
                raise Exception("Failure")
            return "success"
        
        # Open the circuit
        operation.should_fail = True
        for _ in range(2):
            with pytest.raises(Exception):
                await breaker.call(operation)
        
        assert breaker.get_state() == CircuitState.OPEN
        
        # Wait for recovery timeout
        await asyncio.sleep(1.1)
        
        # Circuit should transition to half-open
        operation.should_fail = False
        result = await breaker.call(operation)
        assert result == "success"
        
        # After success in half-open, circuit should close
        assert breaker.get_state() == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_half_open_failure_reopens(self, breaker):
        """Test failure in half-open state reopens circuit."""
        async def operation():
            if hasattr(operation, 'call_count'):
                operation.call_count += 1
            else:
                operation.call_count = 1
            
            if operation.call_count <= 3:
                raise Exception("Failure")
            return "success"
        
        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await breaker.call(operation)
        
        # Wait for recovery timeout
        await asyncio.sleep(1.1)
        
        # Failure in half-open should reopen
        with pytest.raises(Exception):
            await breaker.call(operation)
        
        assert breaker.get_state() == CircuitState.OPEN
    
    @pytest.mark.asyncio
    async def test_expected_exception_filter(self, breaker):
        """Test circuit only responds to expected exceptions."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            expected_exception=ValueError
        )
        breaker = CircuitBreaker(config, name="FilteredBreaker")
        
        async def operation():
            if hasattr(operation, 'error_type'):
                raise operation.error_type("Test error")
            return "success"
        
        # Non-expected exception shouldn't trigger circuit
        operation.error_type = TypeError
        for _ in range(3):
            with pytest.raises(TypeError):
                await breaker.call(operation)
        
        assert breaker.get_state() == CircuitState.CLOSED
        
        # Expected exception should trigger circuit
        operation.error_type = ValueError
        for _ in range(2):
            with pytest.raises(ValueError):
                await breaker.call(operation)
        
        assert breaker.get_state() == CircuitState.OPEN
    
    @pytest.mark.asyncio
    async def test_reset_functionality(self, breaker):
        """Test manual reset of circuit breaker."""
        async def failing_operation():
            raise Exception("Failure")
        
        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await breaker.call(failing_operation)
        
        assert breaker.get_state() == CircuitState.OPEN
        
        # Manual reset
        breaker.reset()
        
        assert breaker.get_state() == CircuitState.CLOSED
        stats = breaker.get_stats()
        assert stats['total_calls'] == 0
        assert stats['failed_calls'] == 0
    
    @pytest.mark.asyncio
    async def test_statistics_tracking(self, breaker):
        """Test comprehensive statistics tracking."""
        async def operation():
            if hasattr(operation, 'should_fail') and operation.should_fail:
                raise Exception("Failure")
            return "success"
        
        # Mix of successes and failures
        operation.should_fail = False
        await breaker.call(operation)
        
        operation.should_fail = True
        with pytest.raises(Exception):
            await breaker.call(operation)
        
        operation.should_fail = False
        await breaker.call(operation)
        
        stats = breaker.get_stats()
        assert stats['total_calls'] == 3
        assert stats['successful_calls'] == 2
        assert stats['failed_calls'] == 1
        assert stats['success_rate'] == pytest.approx(66.67, 0.01)
        assert len(stats['state_transitions']) > 0


class TestCircuitBreakerManager:
    """
    Test suite for CircuitBreakerManager.
    
    Tests centralized management of multiple circuit breakers.
    """
    
    @pytest.fixture
    def manager(self):
        """Create a new circuit breaker manager."""
        return CircuitBreakerManager()
    
    def test_register_breaker(self, manager):
        """Test registering new circuit breakers."""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = manager.register("test_service", config)
        
        assert breaker is not None
        assert breaker.name == "test_service"
        assert "test_service" in manager.breakers
    
    def test_get_breaker(self, manager):
        """Test retrieving registered breakers."""
        manager.register("service1")
        manager.register("service2")
        
        breaker1 = manager.get("service1")
        assert breaker1 is not None
        assert breaker1.name == "service1"
        
        breaker_none = manager.get("nonexistent")
        assert breaker_none is None
    
    def test_duplicate_registration(self, manager):
        """Test duplicate registration returns existing breaker."""
        breaker1 = manager.register("duplicate")
        breaker2 = manager.register("duplicate")
        
        assert breaker1 is breaker2
    
    def test_get_all_stats(self, manager):
        """Test getting statistics for all breakers."""
        manager.register("service1")
        manager.register("service2")
        
        stats = manager.get_all_stats()
        
        assert "service1" in stats
        assert "service2" in stats
        assert stats["service1"]["name"] == "service1"
        assert stats["service2"]["name"] == "service2"
    
    def test_reset_all(self, manager):
        """Test resetting all circuit breakers."""
        breaker1 = manager.register("service1", CircuitBreakerConfig(failure_threshold=1))
        breaker2 = manager.register("service2", CircuitBreakerConfig(failure_threshold=1))
        
        # Open both circuits
        async def failing():
            raise Exception("Fail")
        
        asyncio.run(self._open_breaker(breaker1, failing))
        asyncio.run(self._open_breaker(breaker2, failing))
        
        assert breaker1.get_state() == CircuitState.OPEN
        assert breaker2.get_state() == CircuitState.OPEN
        
        # Reset all
        manager.reset_all()
        
        assert breaker1.get_state() == CircuitState.CLOSED
        assert breaker2.get_state() == CircuitState.CLOSED
    
    async def _open_breaker(self, breaker, failing_op):
        """Helper to open a circuit breaker."""
        with pytest.raises(Exception):
            await breaker.call(failing_op)


class TestCircuitBreakerIntegration:
    """
    Integration tests for circuit breaker with real async operations.
    
    Tests circuit breaker behavior with realistic async scenarios.
    """
    
    @pytest.mark.asyncio
    async def test_concurrent_calls(self):
        """Test circuit breaker with concurrent calls."""
        config = CircuitBreakerConfig(
            failure_threshold=5,
            half_open_max_calls=2
        )
        breaker = CircuitBreaker(config, name="ConcurrentBreaker")
        
        call_count = 0
        
        async def operation():
            nonlocal call_count
            call_count += 1
            if call_count <= 5:
                raise Exception("Failure")
            return f"success_{call_count}"
        
        # Concurrent failures
        tasks = []
        for _ in range(5):
            tasks.append(breaker.call(operation))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should fail
        assert all(isinstance(r, Exception) for r in results)
        assert breaker.get_state() == CircuitState.OPEN
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test circuit breaker with operation timeouts."""
        config = CircuitBreakerConfig(failure_threshold=2)
        breaker = CircuitBreaker(config, name="TimeoutBreaker")
        
        async def slow_operation():
            await asyncio.sleep(10)
            return "success"
        
        # Use timeout wrapper
        async def timeout_wrapper():
            return await asyncio.wait_for(slow_operation(), timeout=0.1)
        
        # Timeouts should open circuit
        for _ in range(2):
            with pytest.raises(asyncio.TimeoutError):
                await breaker.call(timeout_wrapper)
        
        assert breaker.get_state() == CircuitState.OPEN
    
    @pytest.mark.asyncio
    async def test_performance_overhead(self):
        """Test circuit breaker performance overhead."""
        breaker = CircuitBreaker(name="PerformanceBreaker")
        
        async def fast_operation():
            return "result"
        
        # Measure overhead
        start = time.perf_counter()
        for _ in range(1000):
            await breaker.call(fast_operation)
        duration = time.perf_counter() - start
        
        # Should complete 1000 calls in under 1 second
        assert duration < 1.0
        
        stats = breaker.get_stats()
        assert stats['successful_calls'] == 1000
        assert stats['failed_calls'] == 0