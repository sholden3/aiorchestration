"""
Test suite for C2: Cache Disk I/O Failure Cascade Fix
Validates circuit breaker, error boundaries, and graceful degradation
Architecture: Dr. Sarah Chen
"""
import pytest
import asyncio
import gzip
import pickle
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cache_manager import IntelligentCache, CacheEntry
from cache_errors import CacheDiskCorruptionError, CacheDiskIOError, CacheCircuitBreakerOpenError
from cache_circuit_breaker import CacheCircuitBreaker, CircuitState


class TestCacheResilience:
    """Test cache resilience with disk I/O failures"""
    
    @pytest.fixture
    async def cache(self, tmp_path):
        """Create cache instance with temp directory"""
        cache = IntelligentCache(hot_size_mb=1, warm_size_mb=2)
        cache.warm_cache_dir = tmp_path / "warm"
        cache.warm_cache_dir.mkdir(parents=True, exist_ok=True)
        return cache
    
    @pytest.mark.asyncio
    async def test_corrupted_cache_file_handling(self, cache, tmp_path):
        """Test that corrupted cache files don't crash the system"""
        # Store valid entry
        key = "test_key"
        data = {"test": "data"}
        await cache.store(key, data)
        
        # Corrupt the warm cache file
        warm_path = cache.warm_cache_dir / f"{key}.pkl.gz"
        warm_path.write_bytes(b"corrupted data")
        
        # Should handle corruption gracefully
        result = await cache.get(key)
        assert result is None  # Cache miss due to corruption
        assert cache.metrics['warm_corruptions'] > 0
        assert not warm_path.exists()  # Corrupted file should be cleaned up
    
    @pytest.mark.asyncio
    async def test_disk_io_error_handling(self, cache):
        """Test handling of disk I/O errors"""
        key = "test_key"
        cache.warm_index[key] = {"file": f"{key}.pkl.gz"}
        
        # Mock disk read failure
        with patch('gzip.open', side_effect=IOError("Disk read error")):
            result = await cache.get(key)
            assert result is None  # Cache miss due to I/O error
            assert cache.metrics['warm_errors'] > 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_repeated_failures(self, cache):
        """Test circuit breaker opens after threshold failures"""
        # Create multiple entries that will fail
        for i in range(5):
            key = f"bad_key_{i}"
            cache.warm_index[key] = {"file": f"{key}.pkl.gz"}
            warm_path = cache.warm_cache_dir / f"{key}.pkl.gz"
            warm_path.write_bytes(b"corrupted")
        
        # Access entries to trigger failures
        for i in range(3):  # Failure threshold
            await cache.get(f"bad_key_{i}")
        
        # Circuit breaker should be open
        assert cache.warm_circuit_breaker.is_open()
        assert cache.metrics['circuit_breaker_opens'] > 0
        
        # Further requests should bypass warm cache
        result = await cache.get("bad_key_4")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_recovery(self):
        """Test circuit breaker automatic recovery"""
        breaker = CacheCircuitBreaker(
            failure_threshold=2,
            recovery_time=0.1,  # 100ms for fast testing
            test_requests=2
        )
        
        # Cause failures to open circuit
        failing_op = Mock(side_effect=Exception("Test failure"))
        for _ in range(2):
            with pytest.raises(Exception):
                await breaker.execute(failing_op)
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait for recovery time
        await asyncio.sleep(0.15)
        
        # Successful operation should transition to HALF_OPEN then CLOSED
        successful_op = Mock(return_value="success")
        result = await breaker.execute(successful_op)
        assert result == "success"
        assert breaker.state == CircuitState.HALF_OPEN
        
        # Another success should close the circuit
        result = await breaker.execute(successful_op)
        assert breaker.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_index_corruption_recovery(self, cache, tmp_path):
        """Test warm cache index corruption recovery"""
        # Create some cache files
        for i in range(3):
            cache_file = cache.warm_cache_dir / f"key_{i}.pkl.gz"
            with gzip.open(cache_file, 'wb') as f:
                pickle.dump(CacheEntry(f"key_{i}", {"data": i}), f)
        
        # Corrupt the index
        index_path = cache.warm_cache_dir / "index.json"
        index_path.write_text("corrupted json {[}")
        
        # Load index - should rebuild from files
        cache._load_warm_index()
        
        # Index should be rebuilt
        assert len(cache.warm_index) == 3
        assert "key_0" in cache.warm_index
        assert "key_1" in cache.warm_index
        assert "key_2" in cache.warm_index
    
    @pytest.mark.asyncio
    async def test_graceful_degradation_with_fallback(self):
        """Test that cache failures don't break application"""
        breaker = CacheCircuitBreaker()
        
        async def failing_cache_op():
            raise Exception("Cache failure")
        
        async def fallback_op():
            return {"source": "database", "data": "fallback"}
        
        # Execute with fallback
        result = await breaker.execute(failing_cache_op, fallback=fallback_op)
        assert result["source"] == "database"
        assert breaker.failure_count == 1
    
    @pytest.mark.asyncio
    async def test_metrics_tracking(self, cache):
        """Test comprehensive metrics tracking"""
        initial_metrics = cache.metrics.copy()
        
        # Cause various failures
        cache.warm_index["bad_key"] = {"file": "bad.pkl.gz"}
        bad_path = cache.warm_cache_dir / "bad.pkl.gz"
        bad_path.write_bytes(b"corrupted")
        
        await cache.get("bad_key")
        
        # Verify metrics updated
        assert cache.metrics['warm_corruptions'] > initial_metrics['warm_corruptions']
        assert cache.metrics['total_requests'] > initial_metrics['total_requests']
        assert cache.metrics['misses'] > initial_metrics['misses']


class TestCircuitBreaker:
    """Test circuit breaker pattern implementation"""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_states(self):
        """Test circuit breaker state transitions"""
        breaker = CacheCircuitBreaker(failure_threshold=2)
        
        # Initial state is CLOSED
        assert breaker.state == CircuitState.CLOSED
        
        # Single failure doesn't open circuit
        try:
            await breaker.execute(Mock(side_effect=Exception()))
        except:
            pass
        assert breaker.state == CircuitState.CLOSED
        
        # Second failure opens circuit
        try:
            await breaker.execute(Mock(side_effect=Exception()))
        except:
            pass
        assert breaker.state == CircuitState.OPEN
        
        # Open circuit rejects requests
        with pytest.raises(CacheCircuitBreakerOpenError):
            await breaker.execute(Mock())
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_monitoring(self):
        """Test circuit breaker monitoring capabilities"""
        breaker = CacheCircuitBreaker()
        
        # Get initial state
        state = breaker.get_state()
        assert state['state'] == 'closed'
        assert state['failure_count'] == 0
        assert state['is_healthy'] == True
        
        # Cause failures
        for _ in range(5):
            try:
                await breaker.execute(Mock(side_effect=Exception()))
            except:
                pass
        
        # Check updated state
        state = breaker.get_state()
        assert state['state'] == 'open'
        assert state['failure_count'] == 5
        assert state['is_healthy'] == False
        assert state['total_opens'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])