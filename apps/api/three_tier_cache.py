"""
Three-Tier Cache Architecture Implementation
Hot (Memory) / Warm (Disk) / Cold (Database) with Evidence-Based Performance
"""

import asyncio
import json
import gzip
import time
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import OrderedDict
import logging
from enum import Enum

from config import Config
from database_manager import DatabaseManager
from base_patterns import OrchestrationResult

logger = logging.getLogger(__name__)

class CacheTier(Enum):
    """Cache tier levels"""
    HOT = "hot"      # Memory - microseconds
    WARM = "warm"    # Disk - milliseconds  
    COLD = "cold"    # Database - tens of milliseconds

class CacheEntry:
    """Enhanced cache entry with tier tracking"""
    def __init__(self, key: str, data: Any, tier: CacheTier, ttl_hours: int = 24):
        self.key = key
        self.data = data
        self.tier = tier
        self.created = datetime.now()
        self.expires = self.created + timedelta(hours=ttl_hours)
        self.last_accessed = self.created
        self.access_count = 1
        self.size_bytes = len(json.dumps(data).encode('utf-8'))
        
    def is_expired(self) -> bool:
        return datetime.now() > self.expires
    
    def touch(self):
        self.last_accessed = datetime.now()
        self.access_count += 1

class ThreeTierCache:
    """
    Three-tier cache with automatic promotion/demotion
    Marcus: Measured performance at each tier
    Sarah: Intelligent data placement based on access patterns
    Emily: Clear tier boundaries and predictable behavior
    """
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        
        # Hot tier - in memory (LRU)
        self.hot_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.hot_size_bytes = 0
        self.hot_max_bytes = self.config.systems.cache_hot_size_mb * 1024 * 1024
        
        # Warm tier - disk based
        self.warm_dir = Path("./cache/warm")
        self.warm_dir.mkdir(parents=True, exist_ok=True)
        self.warm_index: Dict[str, Dict] = {}
        
        # Cold tier - database
        self.db_manager = DatabaseManager(self.config)
        self.cold_initialized = False
        
        # Metrics
        self.metrics = {
            'hot_hits': 0,
            'warm_hits': 0,
            'cold_hits': 0,
            'misses': 0,
            'promotions': 0,
            'demotions': 0,
            'total_requests': 0
        }
        
        # Promotion thresholds
        self.promotion_threshold = 3  # Access count to promote
        self.demotion_age_hours = 6   # Hours before demotion
        
        logger.info("Three-tier cache initialized")
    
    def generate_key(self, data: str, context: Dict = None) -> str:
        """Generate deterministic cache key"""
        cache_data = {'data': data, 'context': context or {}}
        json_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]
    
    async def get(self, key: str) -> Tuple[Optional[Any], CacheTier]:
        """
        Get from cache with tier information
        Marcus: Returns actual tier hit for performance analysis
        """
        start_time = time.perf_counter()
        self.metrics['total_requests'] += 1
        
        # Check hot tier first (fastest)
        if key in self.hot_cache:
            entry = self.hot_cache[key]
            if not entry.is_expired():
                entry.touch()
                self.hot_cache.move_to_end(key)  # LRU update
                self.metrics['hot_hits'] += 1
                
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.debug(f"Hot hit for {key} in {elapsed_ms:.3f}ms")
                return entry.data, CacheTier.HOT
            else:
                self._evict_from_hot(key)
        
        # Check warm tier (disk)
        warm_path = self.warm_dir / f"{key}.gz"
        if warm_path.exists():
            try:
                with gzip.open(warm_path, 'rb') as f:
                    entry_data = json.loads(f.read())
                
                entry = CacheEntry(
                    key=key,
                    data=entry_data['data'],
                    tier=CacheTier.WARM
                )
                
                if not entry.is_expired():
                    entry.access_count = entry_data.get('access_count', 1) + 1
                    self.metrics['warm_hits'] += 1
                    
                    # Consider promotion to hot
                    if entry.access_count >= self.promotion_threshold:
                        await self._promote_to_hot(key, entry)
                        self.metrics['promotions'] += 1
                    
                    elapsed_ms = (time.perf_counter() - start_time) * 1000
                    logger.debug(f"Warm hit for {key} in {elapsed_ms:.3f}ms")
                    return entry.data, CacheTier.WARM
                else:
                    warm_path.unlink()
                    
            except Exception as e:
                logger.error(f"Error reading warm cache: {e}")
                if warm_path.exists():
                    warm_path.unlink()
        
        # Check cold tier (database)
        if self.cold_initialized and self.db_manager.pool:
            try:
                cold_data = await self._get_from_cold(key)
                if cold_data:
                    self.metrics['cold_hits'] += 1
                    
                    # Promote to warm tier
                    entry = CacheEntry(key, cold_data, CacheTier.COLD)
                    await self._store_warm(key, entry)
                    self.metrics['promotions'] += 1
                    
                    elapsed_ms = (time.perf_counter() - start_time) * 1000
                    logger.debug(f"Cold hit for {key} in {elapsed_ms:.3f}ms")
                    return cold_data, CacheTier.COLD
            except Exception as e:
                logger.error(f"Error accessing cold tier: {e}")
        
        # Cache miss
        self.metrics['misses'] += 1
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.debug(f"Cache miss for {key} in {elapsed_ms:.3f}ms")
        return None, None
    
    async def store(self, key: str, data: Any, ttl_hours: int = 24) -> CacheTier:
        """
        Store in appropriate tier
        Sarah: Intelligent placement based on data characteristics
        """
        entry = CacheEntry(key, data, CacheTier.HOT, ttl_hours)
        
        # Decide initial tier based on size and current load
        if entry.size_bytes > self.hot_max_bytes * 0.1:  # >10% of hot cache
            # Too large for hot, go directly to warm
            await self._store_warm(key, entry)
            return CacheTier.WARM
        
        # Try hot tier first
        if self.hot_size_bytes + entry.size_bytes <= self.hot_max_bytes:
            self._store_hot(key, entry)
            return CacheTier.HOT
        
        # Need to make space in hot tier
        await self._evict_lru_to_warm()
        
        if self.hot_size_bytes + entry.size_bytes <= self.hot_max_bytes:
            self._store_hot(key, entry)
            return CacheTier.HOT
        
        # Store in warm tier
        await self._store_warm(key, entry)
        return CacheTier.WARM
    
    def _store_hot(self, key: str, entry: CacheEntry):
        """Store in hot tier"""
        if key in self.hot_cache:
            # Remove old entry size
            old_entry = self.hot_cache[key]
            self.hot_size_bytes -= old_entry.size_bytes
        
        self.hot_cache[key] = entry
        self.hot_cache.move_to_end(key)  # Most recent at end
        self.hot_size_bytes += entry.size_bytes
        entry.tier = CacheTier.HOT
    
    async def _store_warm(self, key: str, entry: CacheEntry):
        """Store in warm tier (disk)"""
        warm_path = self.warm_dir / f"{key}.gz"
        
        data_to_store = {
            'data': entry.data,
            'created': entry.created.isoformat(),
            'expires': entry.expires.isoformat(),
            'access_count': entry.access_count
        }
        
        with gzip.open(warm_path, 'wb') as f:
            f.write(json.dumps(data_to_store).encode('utf-8'))
        
        self.warm_index[key] = {
            'path': str(warm_path),
            'size': warm_path.stat().st_size,
            'created': entry.created.isoformat()
        }
        entry.tier = CacheTier.WARM
    
    async def _store_cold(self, key: str, data: Any):
        """Store in cold tier (database)"""
        if not self.db_manager.pool:
            return
        
        try:
            async with self.db_manager.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO cache_cold (key, data, created, expires)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (key) DO UPDATE 
                    SET data = $2, created = $3, expires = $4
                """, key, json.dumps(data), datetime.now(), 
                datetime.now() + timedelta(hours=168))  # 7 days for cold
                
        except Exception as e:
            logger.error(f"Error storing to cold tier: {e}")
    
    async def _get_from_cold(self, key: str) -> Optional[Any]:
        """Get from cold tier (database)"""
        try:
            async with self.db_manager.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT data FROM cache_cold WHERE key = $1 AND expires > $2",
                    key, datetime.now()
                )
                if row:
                    return json.loads(row['data'])
        except Exception as e:
            logger.error(f"Error getting from cold tier: {e}")
        return None
    
    async def _promote_to_hot(self, key: str, entry: CacheEntry):
        """Promote entry from warm to hot"""
        if self.hot_size_bytes + entry.size_bytes > self.hot_max_bytes:
            await self._evict_lru_to_warm()
        
        if self.hot_size_bytes + entry.size_bytes <= self.hot_max_bytes:
            self._store_hot(key, entry)
            
            # Remove from warm
            warm_path = self.warm_dir / f"{key}.gz"
            if warm_path.exists():
                warm_path.unlink()
    
    def _evict_from_hot(self, key: str):
        """Remove entry from hot tier"""
        if key in self.hot_cache:
            entry = self.hot_cache[key]
            self.hot_size_bytes -= entry.size_bytes
            del self.hot_cache[key]
    
    async def _evict_lru_to_warm(self):
        """Evict least recently used from hot to warm"""
        if not self.hot_cache:
            return
        
        # Get oldest entry (first in OrderedDict)
        key, entry = self.hot_cache.popitem(last=False)
        self.hot_size_bytes -= entry.size_bytes
        
        # Move to warm tier
        await self._store_warm(key, entry)
        self.metrics['demotions'] += 1
        
        logger.debug(f"Demoted {key} from hot to warm")
    
    async def initialize_cold_tier(self):
        """Initialize cold tier database table"""
        if not self.db_manager.pool:
            await self.db_manager.initialize()
        
        if self.db_manager.pool:
            try:
                async with self.db_manager.pool.acquire() as conn:
                    await conn.execute("""
                        CREATE TABLE IF NOT EXISTS cache_cold (
                            key VARCHAR(64) PRIMARY KEY,
                            data JSONB,
                            created TIMESTAMP,
                            expires TIMESTAMP,
                            access_count INTEGER DEFAULT 1
                        )
                    """)
                    
                    await conn.execute("""
                        CREATE INDEX IF NOT EXISTS idx_cache_cold_expires 
                        ON cache_cold(expires)
                    """)
                    
                self.cold_initialized = True
                logger.info("Cold tier initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize cold tier: {e}")
                self.cold_initialized = False
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get cache metrics
        Marcus: Real measurements from actual operations
        """
        total_hits = (self.metrics['hot_hits'] + 
                     self.metrics['warm_hits'] + 
                     self.metrics['cold_hits'])
        
        hit_rate = 0
        if self.metrics['total_requests'] > 0:
            hit_rate = (total_hits / self.metrics['total_requests']) * 100
        
        return {
            'hit_rate': round(hit_rate, 2),
            'total_requests': self.metrics['total_requests'],
            'hot_hits': self.metrics['hot_hits'],
            'warm_hits': self.metrics['warm_hits'],
            'cold_hits': self.metrics['cold_hits'],
            'misses': self.metrics['misses'],
            'promotions': self.metrics['promotions'],
            'demotions': self.metrics['demotions'],
            'hot_size_mb': round(self.hot_size_bytes / (1024 * 1024), 2),
            'hot_entries': len(self.hot_cache),
            'warm_entries': len(self.warm_index)
        }
    
    async def clear(self):
        """Clear all cache tiers"""
        # Clear hot
        self.hot_cache.clear()
        self.hot_size_bytes = 0
        
        # Clear warm
        for path in self.warm_dir.glob("*.gz"):
            path.unlink()
        self.warm_index.clear()
        
        # Clear cold
        if self.cold_initialized and self.db_manager.pool:
            try:
                async with self.db_manager.pool.acquire() as conn:
                    await conn.execute("TRUNCATE TABLE cache_cold")
            except Exception as e:
                logger.error(f"Error clearing cold tier: {e}")
        
        # Reset metrics
        self.metrics = {
            'hot_hits': 0,
            'warm_hits': 0,
            'cold_hits': 0,
            'misses': 0,
            'promotions': 0,
            'demotions': 0,
            'total_requests': 0
        }
        
        logger.info("All cache tiers cleared")