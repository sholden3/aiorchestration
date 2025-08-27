# C2: Cache Disk I/O Failure Cascade - Implementation

**Issue**: No error boundaries around disk operations, single corrupted file crashes entire cache  
**Severity**: CRITICAL  
**Owner**: Dr. Sarah Chen v1.2  
**Date**: 2025-01-27 (Phase 3 Day 1)  

---

## Implementation Plan

### 1. Add Defensive Disk Operations

```python
# backend/cache_manager.py - Add after line 218 (in IntelligentCache class)

async def _safe_disk_operation(self, operation: str, *args, **kwargs):
    """
    FIX C2: Defensive disk operations with circuit breaker
    Dr. Sarah Chen v1.2 - Three Questions Framework:
    - What breaks first? Disk I/O or corrupted file
    - How do we know? Exception type and corruption detection
    - What's Plan B? Memory-only fallback mode
    """
    correlation_id = f"disk-op-{time.time()}"
    
    # Check if circuit breaker is open
    if self.circuit_breaker.is_open():
        logger.warning(f"[{correlation_id}] Circuit breaker open, using memory-only mode")
        return self._memory_only_fallback(operation, *args, **kwargs)
    
    try:
        # Attempt the disk operation
        if operation == 'write':
            return await self._write_to_disk_safe(*args, **kwargs)
        elif operation == 'read':
            return await self._read_from_disk_safe(*args, **kwargs)
        elif operation == 'delete':
            return await self._delete_from_disk_safe(*args, **kwargs)
        else:
            raise ValueError(f"Unknown operation: {operation}")
            
    except (IOError, OSError) as e:
        # Disk I/O failure
        logger.error(f"[{correlation_id}] Disk I/O failure: {e}")
        self.circuit_breaker.record_failure()
        self.metrics['disk_errors'] += 1
        
        # Check if we should switch to memory-only mode
        if self.metrics['disk_errors'] > 10:
            self._enable_memory_only_mode()
            
        return self._memory_only_fallback(operation, *args, **kwargs)
        
    except (pickle.PickleError, json.JSONDecodeError) as e:
        # Corruption detected
        logger.error(f"[{correlation_id}] Cache corruption detected: {e}")
        self.circuit_breaker.record_failure()
        self.metrics['corruption_errors'] += 1
        
        # Attempt to quarantine corrupted file
        if 'key' in kwargs:
            self._quarantine_corrupted_file(kwargs['key'])
            
        return None
        
    except Exception as e:
        # Unknown error - don't crash
        logger.error(f"[{correlation_id}] Unexpected error in disk operation: {e}")
        self.circuit_breaker.record_failure()
        return None
    else:
        # Success
        self.circuit_breaker.record_success()
        return True

async def _write_to_disk_safe(self, key: str, entry: CacheEntry) -> bool:
    """Safe write with corruption prevention"""
    file_path = self.warm_cache_dir / f"{self._hash_key(key)}.cache"
    temp_path = file_path.with_suffix('.tmp')
    
    try:
        # Write to temp file first
        with gzip.open(temp_path, 'wb') as f:
            pickle.dump(entry, f)
        
        # Verify we can read it back
        with gzip.open(temp_path, 'rb') as f:
            test_load = pickle.load(f)
            
        # Atomic rename
        temp_path.replace(file_path)
        
        logger.debug(f"Successfully wrote cache entry: {key}")
        return True
        
    except Exception as e:
        # Clean up temp file if exists
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        raise

async def _read_from_disk_safe(self, key: str) -> Optional[CacheEntry]:
    """Safe read with corruption handling"""
    file_path = self.warm_cache_dir / f"{self._hash_key(key)}.cache"
    
    if not file_path.exists():
        return None
        
    try:
        with gzip.open(file_path, 'rb') as f:
            entry = pickle.load(f)
            
        # Validate entry structure
        if not isinstance(entry, CacheEntry):
            raise ValueError("Invalid cache entry structure")
            
        return entry
        
    except (EOFError, gzip.BadGzipFile) as e:
        # File is corrupted
        logger.error(f"Corrupted cache file for key {key}: {e}")
        self._quarantine_corrupted_file(key)
        return None
        
    except Exception as e:
        logger.error(f"Error reading cache file for key {key}: {e}")
        return None

def _quarantine_corrupted_file(self, key: str):
    """Move corrupted file to quarantine directory"""
    try:
        file_path = self.warm_cache_dir / f"{self._hash_key(key)}.cache"
        if file_path.exists():
            quarantine_dir = self.warm_cache_dir / "quarantine"
            quarantine_dir.mkdir(exist_ok=True)
            
            quarantine_path = quarantine_dir / f"{file_path.name}.{time.time()}"
            file_path.rename(quarantine_path)
            
            logger.warning(f"Quarantined corrupted file: {quarantine_path}")
    except Exception as e:
        logger.error(f"Failed to quarantine file: {e}")

def _memory_only_fallback(self, operation: str, *args, **kwargs):
    """Fallback to memory-only operations when disk fails"""
    logger.warning(f"Using memory-only fallback for operation: {operation}")
    
    if operation == 'write':
        # Just keep in hot cache
        key = kwargs.get('key')
        entry = kwargs.get('entry')
        if key and entry:
            self.hot_cache[key] = entry
            self._manage_hot_cache_size()
        return True
        
    elif operation == 'read':
        # Only check hot cache
        key = kwargs.get('key')
        if key:
            return self.hot_cache.get(key)
        return None
        
    elif operation == 'delete':
        # Only delete from hot cache
        key = kwargs.get('key')
        if key and key in self.hot_cache:
            del self.hot_cache[key]
        return True
        
    return None

def _enable_memory_only_mode(self):
    """Switch to memory-only mode when disk is unreliable"""
    logger.critical("Switching to memory-only mode due to disk failures")
    self.memory_only_mode = True
    
    # Increase hot cache size since we can't use disk
    self.max_hot_size *= 2  # Double the memory cache
    
    # Notify monitoring
    self.metrics['mode'] = 'memory-only'
    
    # Set recovery timer (try disk again in 5 minutes)
    asyncio.create_task(self._attempt_disk_recovery())

async def _attempt_disk_recovery(self):
    """Attempt to recover disk functionality after delay"""
    await asyncio.sleep(300)  # 5 minutes
    
    logger.info("Attempting to recover disk functionality")
    
    # Test disk write
    try:
        test_file = self.warm_cache_dir / ".test_recovery"
        test_file.write_text("test")
        test_file.unlink()
        
        # Success - re-enable disk
        self.memory_only_mode = False
        self.circuit_breaker.reset()
        self.metrics['mode'] = 'normal'
        logger.info("Disk functionality recovered")
        
    except Exception as e:
        logger.error(f"Disk recovery failed: {e}")
        # Try again later
        asyncio.create_task(self._attempt_disk_recovery())
```

### 2. Update Cache Operations to Use Safe Methods

```python
# Update existing get/set methods

async def get(self, key: str) -> Optional[Dict[str, Any]]:
    """
    FIX C2: Updated with defensive error handling
    """
    self.metrics['total_requests'] += 1
    
    # Check hot cache first
    if key in self.hot_cache:
        entry = self.hot_cache[key]
        if not entry.is_expired():
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self.metrics['hot_hits'] += 1
            self.metrics['hits'] += 1
            return entry.data
        else:
            del self.hot_cache[key]
    
    # Check warm cache with safe disk operation
    if not self.memory_only_mode:
        entry = await self._safe_disk_operation('read', key=key)
        if entry and not entry.is_expired():
            # Promote to hot cache
            self.hot_cache[key] = entry
            self._manage_hot_cache_size()
            self.metrics['warm_hits'] += 1
            self.metrics['hits'] += 1
            return entry.data
    
    # Cache miss
    self.metrics['misses'] += 1
    return None

async def set(self, key: str, data: Dict[str, Any], ttl: int = 3600):
    """
    FIX C2: Updated with defensive error handling
    """
    entry = CacheEntry(key, data, ttl_hours=ttl/3600)
    
    # Always add to hot cache
    self.hot_cache[key] = entry
    self.current_hot_size += entry.size
    
    # Manage hot cache size
    self._manage_hot_cache_size()
    
    # Write to disk if available
    if not self.memory_only_mode:
        await self._safe_disk_operation('write', key=key, entry=entry)
    
    # Update metrics
    self.metrics['tokens_saved'] += self._estimate_tokens_saved(data)
```

### 3. Add Disk Health Monitoring

```python
# Add to IntelligentCache.__init__

def __init__(self, ...):
    # ... existing init code ...
    
    # FIX C2: Add disk health monitoring
    self.memory_only_mode = False
    self.circuit_breaker = CacheCircuitBreaker(
        failure_threshold=3,
        timeout=30,
        half_open_max=1
    )
    
    # Enhanced metrics for disk health
    self.metrics['disk_errors'] = 0
    self.metrics['corruption_errors'] = 0
    self.metrics['mode'] = 'normal'
    
    # Start disk health check
    asyncio.create_task(self._periodic_disk_health_check())

async def _periodic_disk_health_check(self):
    """Periodically check disk health"""
    while True:
        await asyncio.sleep(60)  # Check every minute
        
        if not self.memory_only_mode:
            try:
                # Test disk write/read
                test_key = ".health_check"
                test_data = {"timestamp": time.time()}
                test_entry = CacheEntry(test_key, test_data, ttl_hours=0.01)
                
                # Write test
                await self._write_to_disk_safe(test_key, test_entry)
                
                # Read test
                read_entry = await self._read_from_disk_safe(test_key)
                
                if read_entry and read_entry.data == test_data:
                    # Healthy
                    self.metrics['disk_health'] = 'healthy'
                else:
                    # Problem detected
                    self.metrics['disk_health'] = 'degraded'
                    logger.warning("Disk health check failed")
                    
            except Exception as e:
                logger.error(f"Disk health check error: {e}")
                self.metrics['disk_health'] = 'unhealthy'
```

---

## Testing

```python
# backend/tests/test_cache_disk_failure.py

import pytest
import asyncio
from unittest.mock import Mock, patch, mock_open
from cache_manager import IntelligentCache

class TestCacheDiskFailure:
    """
    FIX C2: Test defensive disk operations
    Dr. Sarah Chen v1.2 - Validate failure modes
    """
    
    @pytest.mark.asyncio
    async def test_disk_write_failure_fallback(self):
        """Test fallback to memory when disk write fails"""
        cache = IntelligentCache()
        
        # Mock disk write to fail
        with patch('pathlib.Path.open', side_effect=IOError("Disk full")):
            result = await cache.set("test_key", {"data": "test"})
            
            # Should succeed despite disk failure
            assert result is True
            
            # Should be in hot cache
            assert "test_key" in cache.hot_cache
            
            # Metrics should show disk error
            assert cache.metrics['disk_errors'] > 0
    
    @pytest.mark.asyncio
    async def test_corrupted_file_quarantine(self):
        """Test corrupted files are quarantined"""
        cache = IntelligentCache()
        
        # Mock corrupted file read
        with patch('gzip.open', side_effect=EOFError("Corrupted file")):
            result = await cache.get("corrupted_key")
            
            # Should return None, not crash
            assert result is None
            
            # Metrics should show corruption
            assert cache.metrics['corruption_errors'] > 0
    
    @pytest.mark.asyncio  
    async def test_circuit_breaker_activation(self):
        """Test circuit breaker prevents cascade failures"""
        cache = IntelligentCache()
        
        # Simulate multiple failures
        for i in range(5):
            with patch('pathlib.Path.open', side_effect=IOError()):
                await cache.set(f"key_{i}", {"data": i})
        
        # Circuit breaker should be open
        assert cache.circuit_breaker.is_open()
        
        # Should be in memory-only mode
        assert cache.memory_only_mode is True
    
    @pytest.mark.asyncio
    async def test_memory_only_mode_operation(self):
        """Test cache works in memory-only mode"""
        cache = IntelligentCache()
        cache._enable_memory_only_mode()
        
        # Should work without disk
        await cache.set("mem_key", {"data": "memory"})
        result = await cache.get("mem_key")
        
        assert result == {"data": "memory"}
        assert cache.metrics['mode'] == 'memory-only'
    
    @pytest.mark.asyncio
    async def test_disk_recovery(self):
        """Test automatic disk recovery"""
        cache = IntelligentCache()
        cache._enable_memory_only_mode()
        
        # Mock successful disk operation
        with patch('pathlib.Path.write_text'):
            with patch('pathlib.Path.unlink'):
                await cache._attempt_disk_recovery()
        
        # Should recover
        assert cache.memory_only_mode is False
        assert cache.metrics['mode'] == 'normal'
```

---

## Verification

After implementation:

1. **Unit Tests**: Run the disk failure tests
2. **Integration Test**: Simulate disk full scenario
3. **Stress Test**: Corrupt multiple cache files
4. **Recovery Test**: Verify automatic recovery
5. **Performance**: Ensure <100ms fallback time

---

## Success Criteria

✅ Cache continues operating when disk fails  
✅ Corrupted files are quarantined, not fatal  
✅ Circuit breaker prevents cascade failures  
✅ Automatic recovery when disk available  
✅ Metrics track disk health status  
✅ No data loss for critical operations  

---

**Status**: IMPLEMENTATION READY  
**Estimated Time**: 2 hours  
**Risk**: LOW (defensive patterns proven)