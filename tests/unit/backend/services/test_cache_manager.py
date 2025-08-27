"""
@fileoverview Unit tests for CacheManager with comprehensive resilience and observability validation
@author Dr. Sarah Chen v1.2 & Sam Martinez v3.2.0 - 2025-01-27
@architecture Testing Layer 1 - Unit Test for Cache Manager Service
@responsibility Validates two-tier cache system with circuit breakers and defensive patterns
@dependencies pytest, asyncio, unittest.mock, aioredis, custom test framework
@integration_points Test observability system, performance monitoring, circuit breaker validation
@testing_strategy Comprehensive unit testing with failure mode validation and recovery testing
@governance Validates service against backend-architecture.md and cache failure scenarios

Business Logic Summary:
- Tests two-tier cache system (hot/warm) with automatic fallback mechanisms
- Validates circuit breaker patterns for cache layer failures
- Ensures cache eviction policies and memory management work correctly

Architecture Integration:
- References backend-architecture.md#cache-manager-critical-c2
- Validates security-boundaries.md cache access controls
- Tests failure modes identified in system resilience analysis

SPECIALIST DECISION: Dr. Sarah Chen v1.2 - 2025-01-27
DECISION REFERENCE: DECISIONS.md#cache-architecture-resilience
RATIONALE: Cache failures cascade quickly - comprehensive defensive testing required
CONSTRAINTS: Two-tier fallback must work, circuit breakers must protect system
VALIDATION: All cache operations monitored, failure modes tested, recovery verified
"""

import pytest
import asyncio
import time
import json
from unittest.mock import AsyncMock, MagicMock, patch, call
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
import psutil
import gc

from services.cache_manager import CacheManager, CacheTier, CacheError, CircuitBreakerOpenError
from utils.test_framework.observability_framework import TestObservabilityFramework
from utils.test_framework.performance_monitor import PerformanceTestMonitor
from utils.test_framework.security_validator import SecurityTestValidator
from utils.test_framework.chaos_simulator import ChaosSimulator
from utils.exceptions import CacheBackendError, CircuitBreakerError, ResourceExhaustionError


class TestCacheManager:
    """
    @class TestCacheManager
    @description Comprehensive unit tests for CacheManager with resilience patterns
    @architecture_role Validates two-tier cache system with circuit breaker and fallback patterns
    @business_logic Tests cache operations, eviction policies, circuit breaker activation, fallback mechanisms
    @failure_modes Hot cache failure, warm cache disk I/O failure, memory exhaustion, Redis unavailability
    @debugging_info Detailed cache operation logging with performance metrics and failure analysis
    
    Defensive Programming Patterns:
    - Two-tier cache fallback validation (hot -> warm -> source)
    - Circuit breaker behavior under various failure conditions
    - Memory management and eviction policy testing
    - Performance baseline enforcement under load
    
    Integration Boundaries:
    - Redis integration with connection failure simulation
    - Disk I/O operations with failure injection
    - Memory management with resource exhaustion testing
    - Performance monitoring with comprehensive metrics
    
    SARAH'S FRAMEWORK Integration:
    - What breaks first: Tests all identified cache failure modes
    - How we know: Comprehensive monitoring and alerting validation
    - Plan B: Validates all fallback mechanisms work correctly
    """
    
    @pytest.fixture
    async def observability_framework(self):
        """Setup comprehensive test observability framework"""
        framework = TestObservabilityFramework()
        await framework.initialize_for_cache_testing()
        return framework
    
    @pytest.fixture
    async def performance_monitor(self):
        """Setup cache-specific performance monitoring"""
        monitor = PerformanceTestMonitor()
        await monitor.initialize_cache_metrics()
        return monitor
    
    @pytest.fixture 
    async def chaos_simulator(self):
        """Setup chaos simulation for failure mode testing"""
        simulator = ChaosSimulator()
        await simulator.initialize_cache_chaos()
        return simulator
    
    @pytest.fixture
    async def cache_manager(self, observability_framework):
        """Create cache manager with comprehensive mocking and observability"""
        # BUSINESS RULE: Cache manager must be testable in complete isolation
        # VALIDATION: All external dependencies mocked, observability enabled
        # ERROR HANDLING: Cache initialization failures must be handled gracefully
        # AUDIT TRAIL: All cache operations logged with correlation IDs
        
        correlation_id = observability_framework.generate_correlation_id()
        
        # SARAH'S FRAMEWORK: Setup cache manager with defensive patterns
        mock_redis_client = AsyncMock()
        mock_disk_cache = AsyncMock()
        mock_metrics_collector = AsyncMock()
        
        # Configure Redis mock for testing
        mock_redis_client.ping.return_value = True
        mock_redis_client.get.return_value = None
        mock_redis_client.set.return_value = True
        mock_redis_client.delete.return_value = 1
        mock_redis_client.flushdb.return_value = True
        
        # Configure disk cache mock
        mock_disk_cache.get.return_value = None
        mock_disk_cache.set.return_value = True
        mock_disk_cache.delete.return_value = True
        mock_disk_cache.clear.return_value = True
        
        # Create cache manager with mocked dependencies
        with patch('services.cache_manager.Redis', return_value=mock_redis_client), \
             patch('services.cache_manager.DiskCache', return_value=mock_disk_cache):
            
            cache_manager = CacheManager(
                hot_cache_size_mb=100,
                warm_cache_size_mb=500,
                redis_url="redis://localhost:6379",
                disk_cache_path="/tmp/test_cache",
                correlation_id=correlation_id
            )
            
            await cache_manager.initialize()
            
            # Store mocks for test access
            cache_manager._test_redis_mock = mock_redis_client
            cache_manager._test_disk_mock = mock_disk_cache
            
        # SARAH'S FRAMEWORK: Validate cache manager initialization
        assert cache_manager.is_initialized
        assert cache_manager.correlation_id == correlation_id
        assert cache_manager.hot_cache_circuit_breaker.is_closed()
        assert cache_manager.warm_cache_circuit_breaker.is_closed()
        
        return cache_manager
    
    @pytest.mark.asyncio
    async def test_cache_manager_initialization_success(
        self,
        cache_manager: CacheManager,
        observability_framework: TestObservabilityFramework
    ):
        """Test successful cache manager initialization with all tiers operational"""
        # BUSINESS RULE: Cache manager must initialize with all tiers functional
        start_time = time.perf_counter()
        
        assert cache_manager is not None
        assert isinstance(cache_manager, CacheManager)
        assert cache_manager.is_initialized
        
        # Performance validation - initialization should be fast
        init_time = (time.perf_counter() - start_time) * 1000
        assert init_time < 100  # <100ms initialization
        
        # SARAH'S FRAMEWORK: Validate both cache tiers are operational
        assert cache_manager.is_hot_cache_available()
        assert cache_manager.is_warm_cache_available()
        assert cache_manager.get_hot_cache_size() == 0
        assert cache_manager.get_warm_cache_size() == 0
        
        # Validate circuit breaker states
        assert cache_manager.hot_cache_circuit_breaker.is_closed()
        assert cache_manager.warm_cache_circuit_breaker.is_closed()
        assert cache_manager.get_circuit_breaker_failure_count() == 0
        
        # SECURITY BOUNDARY: Validate cache access controls
        assert cache_manager.access_control.is_enabled()
        assert cache_manager.access_control.default_policy == "DENY"
        
        # AUDIT TRAIL: Log successful initialization
        await observability_framework.log_service_event({
            'event_type': 'CACHE_MANAGER_INITIALIZATION',
            'status': 'SUCCESS',
            'initialization_time_ms': init_time,
            'hot_cache_size_mb': cache_manager.hot_cache_max_size_mb,
            'warm_cache_size_mb': cache_manager.warm_cache_max_size_mb,
            'correlation_id': cache_manager.correlation_id
        })
    
    @pytest.mark.asyncio
    async def test_hot_cache_operations_with_observability(
        self,
        cache_manager: CacheManager,
        performance_monitor: PerformanceTestMonitor
    ):
        """Test hot cache operations with comprehensive performance monitoring"""
        # BUSINESS RULE: Hot cache must provide sub-millisecond access times
        test_key = "user:123:profile"
        test_data = {
            "user_id": 123,
            "username": "test_user",
            "preferences": {"theme": "dark", "language": "en"},
            "last_active": "2025-01-27T10:30:00Z"
        }
        
        # Test hot cache SET operation
        set_start_time = time.perf_counter()
        await cache_manager.set(test_key, test_data, ttl_seconds=3600, tier=CacheTier.HOT)
        set_time_ms = (time.perf_counter() - set_start_time) * 1000
        
        # Performance validation for SET
        assert set_time_ms < 1.0  # <1ms for hot cache SET
        
        # Verify data was stored in hot cache
        assert cache_manager.get_hot_cache_size() == 1
        assert await cache_manager.exists(test_key)
        
        # Test hot cache GET operation
        get_start_time = time.perf_counter()
        retrieved_data = await cache_manager.get(test_key)
        get_time_ms = (time.perf_counter() - get_start_time) * 1000
        
        # Performance validation for GET
        assert get_time_ms < 1.0  # <1ms for hot cache GET
        
        # Data validation
        assert retrieved_data == test_data
        assert cache_manager.get_last_access_tier() == CacheTier.HOT
        
        # BUSINESS LOGIC: Hot cache hit should increment metrics
        cache_stats = await cache_manager.get_cache_statistics()
        assert cache_stats['hot_cache']['hit_count'] == 1
        assert cache_stats['hot_cache']['miss_count'] == 0
        assert cache_stats['hot_cache']['hit_rate'] == 1.0
        
        # Record performance metrics
        await performance_monitor.record_cache_operation_metrics({
            'operation': 'hot_cache_set_get',
            'key': test_key,
            'data_size_bytes': len(json.dumps(test_data)),
            'set_time_ms': set_time_ms,
            'get_time_ms': get_time_ms,
            'cache_tier': 'HOT',
            'operation_successful': True
        })
        
        # SARAH'S FRAMEWORK: Validate hot cache performance baseline
        assert set_time_ms < 0.5  # Stricter requirement: <0.5ms
        assert get_time_ms < 0.5  # Hot cache should be extremely fast
    
    @pytest.mark.asyncio 
    async def test_two_tier_cache_fallback_mechanism(
        self,
        cache_manager: CacheManager,
        observability_framework: TestObservabilityFramework,
        chaos_simulator: ChaosSimulator
    ):
        """Test automatic fallback from hot cache to warm cache"""
        # SARAH'S FRAMEWORK: Test Plan B - warm cache fallback when hot cache fails
        test_key = "session:abc123:data"
        test_data = {"session_id": "abc123", "user_id": 456, "expires_at": "2025-01-27T11:00:00Z"}
        
        # First, store data in warm cache (simulating previous storage)
        warm_cache_data = json.dumps(test_data).encode('utf-8')
        cache_manager._test_disk_mock.get.return_value = warm_cache_data
        
        # CHAOS ENGINEERING: Simulate hot cache failure
        await chaos_simulator.inject_hot_cache_failure(cache_manager)
        
        # Verify hot cache is unavailable
        assert not cache_manager.is_hot_cache_available()
        assert cache_manager.hot_cache_circuit_breaker.is_open()
        
        # BUSINESS RULE: Cache GET should automatically fallback to warm cache
        fallback_start_time = time.perf_counter()
        retrieved_data = await cache_manager.get(test_key)
        fallback_time_ms = (time.perf_counter() - fallback_start_time) * 1000
        
        # Verify fallback success
        assert retrieved_data == test_data
        assert cache_manager.get_last_access_tier() == CacheTier.WARM
        
        # Performance validation - warm cache should still be fast
        assert fallback_time_ms < 50  # <50ms for warm cache fallback
        
        # AUDIT TRAIL: Log fallback operation
        cache_stats = await cache_manager.get_cache_statistics()
        assert cache_stats['hot_cache']['circuit_breaker_open'] is True
        assert cache_stats['warm_cache']['fallback_activations'] == 1
        
        await observability_framework.log_cache_event({
            'event_type': 'CACHE_TIER_FALLBACK',
            'primary_tier': 'HOT',
            'fallback_tier': 'WARM',
            'fallback_time_ms': fallback_time_ms,
            'fallback_successful': True,
            'key': test_key,
            'correlation_id': cache_manager.correlation_id
        })
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_activation_on_cache_failures(
        self,
        cache_manager: CacheManager,
        chaos_simulator: ChaosSimulator,
        observability_framework: TestObservabilityFramework
    ):
        """Test circuit breaker activation under repeated cache failures"""
        # SARAH'S FRAMEWORK: Test what breaks first - repeated cache backend failures
        test_key = "circuit_breaker_test"
        test_data = {"test": "data"}
        
        # Configure Redis mock to simulate repeated failures
        cache_manager._test_redis_mock.set.side_effect = ConnectionError("Redis connection lost")
        cache_manager._test_redis_mock.get.side_effect = ConnectionError("Redis connection lost")
        
        # Execute operations to trigger circuit breaker
        failure_threshold = cache_manager.hot_cache_circuit_breaker.failure_threshold
        failure_count = 0
        
        for i in range(failure_threshold + 2):
            try:
                await cache_manager.set(f"{test_key}_{i}", test_data, tier=CacheTier.HOT)
            except (CacheError, CircuitBreakerOpenError) as e:
                failure_count += 1
                if isinstance(e, CircuitBreakerOpenError):
                    # Circuit breaker activated
                    break
        
        # Verify circuit breaker activation
        assert cache_manager.hot_cache_circuit_breaker.is_open()
        assert failure_count >= failure_threshold
        
        # BUSINESS RULE: Further operations should be blocked by circuit breaker
        with pytest.raises(CircuitBreakerOpenError) as exc_info:
            await cache_manager.set("blocked_operation", {"data": "test"}, tier=CacheTier.HOT)
        
        assert "Hot cache circuit breaker is open" in str(exc_info.value)
        
        # ALEX'S 3AM TEST: Ensure circuit breaker state is debuggable
        circuit_breaker_status = cache_manager.get_circuit_breaker_status()
        assert circuit_breaker_status['hot_cache']['state'] == 'OPEN'
        assert circuit_breaker_status['hot_cache']['failure_count'] == failure_threshold
        assert circuit_breaker_status['hot_cache']['last_failure_time'] is not None
        
        # AUDIT TRAIL: Log circuit breaker activation
        await observability_framework.log_service_event({
            'event_type': 'CACHE_CIRCUIT_BREAKER_ACTIVATED',
            'cache_tier': 'HOT',
            'failure_count': failure_count,
            'failure_threshold': failure_threshold,
            'circuit_breaker_state': 'OPEN',
            'correlation_id': cache_manager.correlation_id
        })
    
    @pytest.mark.asyncio
    async def test_cache_eviction_under_memory_pressure(
        self,
        cache_manager: CacheManager,
        performance_monitor: PerformanceTestMonitor
    ):
        """Test cache eviction policies under memory pressure"""
        # BUSINESS RULE: Cache must evict entries when approaching memory limits
        hot_cache_limit_mb = cache_manager.hot_cache_max_size_mb  # 100MB
        
        # Calculate data size to approach cache limit
        single_entry_kb = 50  # 50KB per entry
        entries_to_fill_cache = int((hot_cache_limit_mb * 1024) / single_entry_kb * 0.95)  # 95% full
        
        # Fill cache to near capacity
        large_data = "x" * (single_entry_kb * 1024)  # 50KB string
        stored_keys = []
        
        fill_start_time = time.perf_counter()
        for i in range(entries_to_fill_cache):
            key = f"memory_test:{i}"
            await cache_manager.set(key, {"id": i, "data": large_data})
            stored_keys.append(key)
        fill_time_ms = (time.perf_counter() - fill_start_time) * 1000
        
        # Verify cache is near capacity
        cache_size_mb = cache_manager.get_hot_cache_size_mb()
        assert cache_size_mb >= hot_cache_limit_mb * 0.9  # At least 90% full
        
        # Add more data to trigger eviction
        eviction_trigger_entries = 20
        eviction_start_time = time.perf_counter()
        
        for i in range(eviction_trigger_entries):
            key = f"eviction_trigger:{i}"
            await cache_manager.set(key, {"trigger": i, "data": large_data})
        
        eviction_time_ms = (time.perf_counter() - eviction_start_time) * 1000
        
        # BUSINESS LOGIC: Cache should have evicted entries to stay within limits
        final_cache_size_mb = cache_manager.get_hot_cache_size_mb()
        assert final_cache_size_mb <= hot_cache_limit_mb  # Must not exceed limit
        
        # Verify eviction statistics
        eviction_stats = await cache_manager.get_eviction_statistics()
        assert eviction_stats['total_evictions'] > 0
        assert eviction_stats['eviction_policy'] == 'LRU'  # Least Recently Used
        
        # Performance validation - eviction should be efficient
        avg_eviction_time_per_entry = eviction_time_ms / eviction_trigger_entries
        assert avg_eviction_time_per_entry < 5  # <5ms per eviction on average
        
        # Record memory pressure test metrics
        await performance_monitor.record_memory_pressure_metrics({
            'test_type': 'cache_eviction_under_pressure',
            'cache_fill_time_ms': fill_time_ms,
            'entries_stored': entries_to_fill_cache,
            'cache_size_before_eviction_mb': cache_size_mb,
            'cache_size_after_eviction_mb': final_cache_size_mb,
            'eviction_time_ms': eviction_time_ms,
            'entries_evicted': eviction_stats['total_evictions'],
            'eviction_efficiency': eviction_stats['total_evictions'] / eviction_time_ms
        })
        
        # SARAH'S FRAMEWORK: Memory management must be predictable and efficient
        assert eviction_stats['total_evictions'] >= eviction_trigger_entries * 0.8  # At least 80% evicted
    
    @pytest.mark.asyncio
    async def test_concurrent_cache_operations_thread_safety(
        self,
        cache_manager: CacheManager,
        performance_monitor: PerformanceTestMonitor
    ):
        """Test thread safety and performance under concurrent cache operations"""
        # BUSINESS RULE: Cache must handle concurrent operations safely and efficiently
        concurrent_operations = 100
        operation_types = ['set', 'get', 'delete']
        
        # Prepare test data
        test_data = {"concurrent": True, "timestamp": time.time()}
        
        # Create concurrent operation tasks
        async def cache_operation_task(operation_id: int):
            op_type = operation_types[operation_id % len(operation_types)]
            key = f"concurrent_test:{operation_id}"
            
            try:
                if op_type == 'set':
                    await cache_manager.set(key, {**test_data, "id": operation_id})
                    return {'operation': 'set', 'success': True, 'key': key}
                elif op_type == 'get':
                    # Ensure key exists for GET operations
                    await cache_manager.set(key, {**test_data, "id": operation_id})
                    result = await cache_manager.get(key)
                    return {'operation': 'get', 'success': result is not None, 'key': key}
                else:  # delete
                    await cache_manager.set(key, {**test_data, "id": operation_id})
                    await cache_manager.delete(key)
                    return {'operation': 'delete', 'success': True, 'key': key}
            except Exception as e:
                return {'operation': op_type, 'success': False, 'error': str(e), 'key': key}
        
        # Execute concurrent operations
        concurrency_start_time = time.perf_counter()
        
        tasks = [cache_operation_task(i) for i in range(concurrent_operations)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        concurrency_time_ms = (time.perf_counter() - concurrency_start_time) * 1000
        
        # Analyze results
        successful_operations = [r for r in results if not isinstance(r, Exception) and r.get('success', False)]
        failed_operations = [r for r in results if isinstance(r, Exception) or not r.get('success', False)]
        
        # Validate concurrent operation results
        success_rate = len(successful_operations) / len(results)
        assert success_rate >= 0.95  # At least 95% success rate
        
        # Performance validation under concurrency
        avg_time_per_operation = concurrency_time_ms / concurrent_operations
        assert avg_time_per_operation < 10  # <10ms per operation on average
        
        # Thread safety validation - cache state should be consistent
        final_cache_size = cache_manager.get_hot_cache_size()
        assert final_cache_size >= 0  # Cache size should be non-negative
        
        # Memory usage validation during concurrency
        cache_size_mb = cache_manager.get_hot_cache_size_mb()
        assert cache_size_mb < cache_manager.hot_cache_max_size_mb  # Should not exceed limit
        
        # Record concurrency performance metrics
        await performance_monitor.record_concurrency_metrics({
            'test_type': 'cache_concurrent_operations',
            'concurrent_operations': concurrent_operations,
            'total_execution_time_ms': concurrency_time_ms,
            'average_time_per_operation_ms': avg_time_per_operation,
            'success_rate': success_rate,
            'failed_operations': len(failed_operations),
            'final_cache_size': final_cache_size,
            'cache_memory_usage_mb': cache_size_mb
        })
        
        # BUSINESS RULE: Concurrent operations must maintain data consistency
        assert len(failed_operations) <= concurrent_operations * 0.05  # Max 5% failures allowed
    
    @pytest.mark.asyncio
    async def test_cache_recovery_after_backend_restoration(
        self,
        cache_manager: CacheManager,
        chaos_simulator: ChaosSimulator,
        observability_framework: TestObservabilityFramework
    ):
        """Test cache recovery mechanisms after backend service restoration"""
        # SARAH'S FRAMEWORK: Test Plan B recovery - cache service restoration
        test_key = "recovery_test"
        test_data = {"recovery": True, "timestamp": time.time()}
        
        # Initially store data successfully
        await cache_manager.set(test_key, test_data)
        assert await cache_manager.get(test_key) == test_data
        
        # Inject Redis backend failure
        await chaos_simulator.inject_redis_failure(cache_manager)
        
        # Verify circuit breaker opened
        assert cache_manager.hot_cache_circuit_breaker.is_open()
        
        # Operations should fail with circuit breaker
        with pytest.raises(CircuitBreakerOpenError):
            await cache_manager.set("should_fail", {"data": "test"}, tier=CacheTier.HOT)
        
        # Simulate backend restoration
        cache_manager._test_redis_mock.set.side_effect = None  # Remove failure
        cache_manager._test_redis_mock.get.side_effect = None
        cache_manager._test_redis_mock.set.return_value = True
        cache_manager._test_redis_mock.get.return_value = json.dumps(test_data).encode('utf-8')
        
        # Manually trigger circuit breaker recovery (in real system, this would be automatic)
        recovery_start_time = time.perf_counter()
        await cache_manager.attempt_circuit_breaker_recovery()
        recovery_time_ms = (time.perf_counter() - recovery_start_time) * 1000
        
        # Verify recovery
        assert cache_manager.hot_cache_circuit_breaker.is_closed()
        assert cache_manager.is_hot_cache_available()
        
        # Test normal operations after recovery
        recovery_test_data = {"post_recovery": True, "test_id": "recovery_validation"}
        await cache_manager.set("post_recovery_test", recovery_test_data, tier=CacheTier.HOT)
        retrieved_data = await cache_manager.get("post_recovery_test")
        assert retrieved_data == recovery_test_data
        
        # Validate recovery metrics
        recovery_stats = await cache_manager.get_recovery_statistics()
        assert recovery_stats['total_recoveries'] == 1
        assert recovery_stats['last_recovery_time'] is not None
        assert recovery_stats['recovery_success_rate'] == 1.0
        
        # AUDIT TRAIL: Log cache recovery
        await observability_framework.log_service_event({
            'event_type': 'CACHE_BACKEND_RECOVERY',
            'recovery_time_ms': recovery_time_ms,
            'circuit_breaker_state': 'CLOSED',
            'post_recovery_operation_successful': True,
            'total_recoveries': recovery_stats['total_recoveries'],
            'correlation_id': cache_manager.correlation_id
        })
        
        # ALEX'S 3AM TEST: Ensure recovery is well-documented for debugging
        recovery_context = cache_manager.get_last_recovery_context()
        assert recovery_context['trigger'] == 'MANUAL_RECOVERY_ATTEMPT'
        assert recovery_context['recovery_duration_ms'] == recovery_time_ms
        assert recovery_context['backend_health_check_passed'] is True
    
    @pytest.mark.asyncio
    async def test_cache_performance_under_varied_data_sizes(
        self,
        cache_manager: CacheManager,
        performance_monitor: PerformanceTestMonitor
    ):
        """Test cache performance with various data sizes from small to large"""
        # PERFORMANCE BASELINE: Cache must handle various data sizes efficiently
        data_sizes = [
            ("small", 1024),      # 1KB
            ("medium", 64 * 1024), # 64KB  
            ("large", 512 * 1024), # 512KB
            ("xlarge", 1024 * 1024) # 1MB
        ]
        
        performance_results = {}
        
        for size_name, size_bytes in data_sizes:
            # Generate test data of specified size
            test_data = {
                "size_category": size_name,
                "size_bytes": size_bytes,
                "data": "x" * (size_bytes - 100),  # Account for metadata overhead
                "timestamp": time.time()
            }
            
            test_key = f"perf_test:{size_name}"
            operations_per_size = 50
            
            # Measure SET operations
            set_times = []
            for i in range(operations_per_size):
                set_start = time.perf_counter()
                await cache_manager.set(f"{test_key}:{i}", test_data)
                set_time_ms = (time.perf_counter() - set_start) * 1000
                set_times.append(set_time_ms)
            
            # Measure GET operations
            get_times = []
            for i in range(operations_per_size):
                get_start = time.perf_counter()
                retrieved_data = await cache_manager.get(f"{test_key}:{i}")
                get_time_ms = (time.perf_counter() - get_start) * 1000
                get_times.append(get_time_ms)
                
                # Verify data integrity
                assert retrieved_data["size_category"] == size_name
                assert len(retrieved_data["data"]) == size_bytes - 100
            
            # Calculate performance statistics
            avg_set_time = sum(set_times) / len(set_times)
            avg_get_time = sum(get_times) / len(get_times)
            p95_set_time = sorted(set_times)[int(len(set_times) * 0.95)]
            p95_get_time = sorted(get_times)[int(len(get_times) * 0.95)]
            
            # Performance validation based on data size
            if size_name == "small":
                assert avg_set_time < 2.0  # <2ms for small data
                assert avg_get_time < 1.0  # <1ms for small data
            elif size_name == "medium":
                assert avg_set_time < 10.0  # <10ms for medium data
                assert avg_get_time < 5.0   # <5ms for medium data  
            elif size_name == "large":
                assert avg_set_time < 50.0  # <50ms for large data
                assert avg_get_time < 20.0  # <20ms for large data
            else:  # xlarge
                assert avg_set_time < 200.0  # <200ms for extra large data
                assert avg_get_time < 100.0  # <100ms for extra large data
            
            performance_results[size_name] = {
                'size_bytes': size_bytes,
                'avg_set_time_ms': avg_set_time,
                'avg_get_time_ms': avg_get_time,
                'p95_set_time_ms': p95_set_time,
                'p95_get_time_ms': p95_get_time,
                'operations_count': operations_per_size
            }
        
        # Record comprehensive performance metrics
        await performance_monitor.record_variable_size_performance_metrics({
            'test_type': 'cache_variable_data_sizes',
            'performance_results': performance_results,
            'total_operations': sum(r['operations_count'] * 2 for r in performance_results.values()),  # SET + GET
            'cache_tier': 'HOT'
        })
        
        # BUSINESS RULE: Performance should scale predictably with data size
        small_throughput = 1000 / performance_results['small']['avg_set_time_ms']  # ops/sec
        large_throughput = 1000 / performance_results['large']['avg_set_time_ms']   # ops/sec
        
        # Large data throughput should not be disproportionately slower
        throughput_ratio = small_throughput / large_throughput
        assert throughput_ratio < 100  # Large data should not be >100x slower than small data
    
    @pytest.mark.asyncio
    async def test_cache_memory_cleanup_and_resource_management(
        self,
        cache_manager: CacheManager,
        observability_framework: TestObservabilityFramework
    ):
        """Test proper cache memory cleanup and resource management"""
        # BUSINESS RULE: Cache must properly manage memory and clean up resources
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Create significant cache load
        cache_load_operations = 1000
        large_data_per_entry = "x" * 10240  # 10KB per entry
        
        stored_keys = []
        for i in range(cache_load_operations):
            key = f"memory_cleanup_test:{i}"
            data = {
                "index": i,
                "large_data": large_data_per_entry,
                "timestamp": time.time()
            }
            await cache_manager.set(key, data)
            stored_keys.append(key)
        
        # Measure memory after cache loading
        memory_after_loading = process.memory_info().rss
        memory_increase_mb = (memory_after_loading - initial_memory) / (1024 * 1024)
        
        # Verify cache contains expected data
        cache_size = cache_manager.get_hot_cache_size()
        assert cache_size == cache_load_operations
        
        # Clear cache and force cleanup
        await cache_manager.clear_all_caches()
        
        # Force Python garbage collection
        gc.collect()
        await asyncio.sleep(0.1)  # Allow cleanup to complete
        
        # Measure memory after cleanup
        memory_after_cleanup = process.memory_info().rss
        memory_retained_mb = (memory_after_cleanup - initial_memory) / (1024 * 1024)
        
        # Validate cache is empty
        assert cache_manager.get_hot_cache_size() == 0
        assert cache_manager.get_warm_cache_size() == 0
        
        # Memory cleanup validation (allow some overhead but should be minimal)
        memory_cleanup_efficiency = 1 - (memory_retained_mb / memory_increase_mb) if memory_increase_mb > 0 else 1
        assert memory_cleanup_efficiency > 0.8  # At least 80% memory recovered
        
        # Validate no keys remain in cache
        for key in stored_keys[:10]:  # Check first 10 keys
            assert await cache_manager.get(key) is None
        
        # AUDIT TRAIL: Log memory management test results
        await observability_framework.log_service_event({
            'event_type': 'CACHE_MEMORY_CLEANUP_TEST',
            'operations_performed': cache_load_operations,
            'initial_memory_mb': initial_memory / (1024 * 1024),
            'memory_after_loading_mb': memory_after_loading / (1024 * 1024),
            'memory_after_cleanup_mb': memory_after_cleanup / (1024 * 1024),
            'memory_increase_mb': memory_increase_mb,
            'memory_retained_mb': memory_retained_mb,
            'cleanup_efficiency': memory_cleanup_efficiency,
            'cache_fully_cleared': cache_manager.get_hot_cache_size() == 0
        })
        
        # SARAH'S FRAMEWORK: Memory management must be reliable and predictable
        assert memory_retained_mb < 50  # Should not retain more than 50MB after cleanup
    
    @pytest.mark.asyncio
    async def test_cache_service_graceful_shutdown(
        self,
        cache_manager: CacheManager,
        observability_framework: TestObservabilityFramework
    ):
        """Test graceful cache service shutdown with proper resource cleanup"""
        # BUSINESS RULE: Cache service shutdown must clean up all resources without data loss
        
        # Setup active cache state
        active_keys = []
        for i in range(50):
            key = f"shutdown_test:{i}"
            data = {"id": i, "important": True, "timestamp": time.time()}
            await cache_manager.set(key, data, ttl_seconds=3600)
            active_keys.append(key)
        
        # Verify cache has active data
        assert cache_manager.get_hot_cache_size() == 50
        assert cache_manager.is_initialized
        
        # Initiate graceful shutdown
        shutdown_start_time = time.perf_counter()
        await cache_manager.shutdown()
        shutdown_duration_ms = (time.perf_counter() - shutdown_start_time) * 1000
        
        # Verify shutdown state
        assert cache_manager.is_shutdown()
        assert not cache_manager.is_initialized
        
        # Verify connections are closed
        assert not cache_manager.is_hot_cache_available()
        assert not cache_manager.is_warm_cache_available()
        
        # Verify circuit breakers are in safe state
        assert cache_manager.hot_cache_circuit_breaker.is_closed()  # Reset to safe state
        assert cache_manager.warm_cache_circuit_breaker.is_closed()
        
        # Verify operations are rejected after shutdown
        with pytest.raises(RuntimeError, match="Cache manager has been shut down"):
            await cache_manager.get("test_key")
        
        with pytest.raises(RuntimeError, match="Cache manager has been shut down"):
            await cache_manager.set("test_key", {"data": "test"})
        
        # ALEX'S 3AM TEST: Ensure shutdown state is clear for debugging
        shutdown_status = cache_manager.get_shutdown_status()
        assert shutdown_status['shutdown_initiated'] is True
        assert shutdown_status['resources_cleaned_up'] is True
        assert shutdown_status['shutdown_duration_ms'] == shutdown_duration_ms
        assert shutdown_status['data_persisted'] is True  # Important data should be persisted
        
        # Performance validation - shutdown should be reasonably fast
        assert shutdown_duration_ms < 5000  # <5 seconds for graceful shutdown
        
        # AUDIT TRAIL: Log graceful shutdown
        await observability_framework.log_service_event({
            'event_type': 'CACHE_GRACEFUL_SHUTDOWN',
            'active_keys_at_shutdown': len(active_keys),
            'shutdown_duration_ms': shutdown_duration_ms,
            'resources_cleaned_up': True,
            'data_persisted': True,
            'shutdown_successful': cache_manager.is_shutdown()
        })
        
        # BUSINESS RULE: Shutdown must be complete and final
        assert shutdown_duration_ms > 0  # Shutdown should take some time for proper cleanup
        assert cache_manager.get_total_shutdown_count() == 1