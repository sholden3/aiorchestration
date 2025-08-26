"""
Business Context: Intelligent caching system to reduce token usage by 65%
Architecture Pattern: Two-tier cache (hot memory, warm disk) with TTL
Performance Requirements: 90% cache hit rate, <10ms hot access, <100ms warm access
Business Assumptions: Local storage, persistent cache across restarts
"""

import os
import pickle
import hashlib
import json
import gzip
import time
import asyncio
from pathlib import Path
from typing import Optional, Any, Dict, List, Tuple
from datetime import datetime, timedelta
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

class CacheEntry:
    """Represents a single cache entry with metadata"""
    
    def __init__(self, key: str, data: Any, ttl_hours: int = 24):
        self.key = key
        self.data = data
        self.created = datetime.now()
        self.expires = self.created + timedelta(hours=ttl_hours)
        self.last_accessed = self.created
        self.access_count = 1
        self.size = len(pickle.dumps(data))
        
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        return datetime.now() > self.expires
    
    def touch(self):
        """Update last access time and count"""
        self.last_accessed = datetime.now()
        self.access_count += 1

class IntelligentCache:
    """
    Two-tier intelligent cache system for token optimization
    Hot: In-memory for <1ms access
    Warm: Disk-based for <100ms access
    """
    
    def __init__(self, hot_size_mb: int = 512, warm_size_mb: int = 2048, target_hit_rate: float = 0.9):
        """
        Initialize cache with size limits and target metrics
        """
        self.hot_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.warm_cache_dir = Path("./cache/warm")
        self.warm_cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_hot_size = hot_size_mb * 1024 * 1024  # Convert to bytes
        self.max_warm_size = warm_size_mb * 1024 * 1024
        self.current_hot_size = 0
        self.target_hit_rate = target_hit_rate
        
        # Metrics tracking
        self.metrics = {
            'hits': 0,
            'misses': 0,
            'hot_hits': 0,
            'warm_hits': 0,
            'tokens_saved': 0,
            'total_requests': 0,
            'evictions': 0
        }
        
        # Cache index for warm storage
        self.warm_index = {}
        self._load_warm_index()
        
        logger.info(f"Cache initialized: {hot_size_mb}MB hot, {warm_size_mb}MB warm")
    
    def generate_key(self, prompt: str, context: Dict = None) -> str:
        """
        Generate deterministic cache key from prompt and context
        """
        cache_data = {
            'prompt': prompt,
            'context': context or {}
        }
        
        # Create deterministic hash
        json_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get from cache with automatic tier management
        Performance: <1ms for hot, <100ms for warm
        """
        self.metrics['total_requests'] += 1
        
        # Check hot cache first (fastest)
        if key in self.hot_cache:
            entry = self.hot_cache[key]
            
            if not entry.is_expired():
                entry.touch()
                # Move to end for LRU
                self.hot_cache.move_to_end(key)
                
                self.metrics['hits'] += 1
                self.metrics['hot_hits'] += 1
                
                logger.debug(f"Cache hit (hot): {key}")
                return entry.data
            else:
                # Remove expired entry
                del self.hot_cache[key]
                self.current_hot_size -= entry.size
        
        # Check warm cache (disk)
        if key in self.warm_index:
            warm_path = self.warm_cache_dir / f"{key}.pkl.gz"
            
            if warm_path.exists():
                try:
                    # Load from disk
                    with gzip.open(warm_path, 'rb') as f:
                        entry = pickle.load(f)
                    
                    if not entry.is_expired():
                        entry.touch()
                        
                        self.metrics['hits'] += 1
                        self.metrics['warm_hits'] += 1
                        
                        # Promote to hot cache if frequently accessed
                        if entry.access_count > 3:
                            await self._promote_to_hot(key, entry)
                        
                        logger.debug(f"Cache hit (warm): {key}")
                        return entry.data
                    else:
                        # Remove expired entry
                        warm_path.unlink()
                        del self.warm_index[key]
                        
                except Exception as e:
                    logger.error(f"Failed to load warm cache entry {key}: {e}")
                    # Remove corrupted entry
                    if warm_path.exists():
                        warm_path.unlink()
                    if key in self.warm_index:
                        del self.warm_index[key]
        
        self.metrics['misses'] += 1
        logger.debug(f"Cache miss: {key}")
        return None
    
    async def set(self, key: str, data: Dict[str, Any], ttl: int = 3600):
        """
        Set method for test compatibility (alias to store)
        Converts ttl from seconds to hours for store method
        """
        ttl_hours = max(1, ttl // 3600)  # Convert seconds to hours, minimum 1 hour
        return await self.store(key, data, ttl_hours)
    
    async def store(self, key: str, data: Dict[str, Any], ttl_hours: int = 24):
        """
        Store in cache with automatic tier placement
        Business Logic: Optimize for token savings and access patterns
        """
        try:
            entry = CacheEntry(key, data, ttl_hours)
            
            # Calculate token savings
            if 'tokens_saved' in data:
                self.metrics['tokens_saved'] += data['tokens_saved']
            
            # Check if we have space in hot cache
            # Check size and count limits (configurable max items)
            max_hot_items = int(os.getenv('MAX_HOT_CACHE_ITEMS', '100'))
            if (self.current_hot_size + entry.size <= self.max_hot_size and 
                len(self.hot_cache) < max_hot_items):
                # Add to hot cache
                self.hot_cache[key] = entry
                self.current_hot_size += entry.size
                logger.debug(f"Stored in hot cache: {key}")
            else:
                # Need to evict to make space
                await self._evict_lru()
                
                # Try again
                max_hot_items = int(os.getenv('MAX_HOT_CACHE_ITEMS', '100'))
                if (self.current_hot_size + entry.size <= self.max_hot_size and
                    len(self.hot_cache) < max_hot_items):
                    self.hot_cache[key] = entry
                    self.current_hot_size += entry.size
                else:
                    # Store directly in warm cache
                    await self._store_warm(key, entry)
            
        except Exception as e:
            logger.error(f"Failed to store cache entry {key}: {e}")
    
    async def _promote_to_hot(self, key: str, entry: CacheEntry):
        """
        Promote frequently accessed entry from warm to hot cache
        """
        try:
            # Make space if needed
            while self.current_hot_size + entry.size > self.max_hot_size:
                await self._evict_lru()
            
            # Add to hot cache
            self.hot_cache[key] = entry
            self.current_hot_size += entry.size
            
            # Remove from warm cache
            warm_path = self.warm_cache_dir / f"{key}.pkl.gz"
            if warm_path.exists():
                warm_path.unlink()
            if key in self.warm_index:
                del self.warm_index[key]
            
            logger.debug(f"Promoted to hot cache: {key}")
            
        except Exception as e:
            logger.error(f"Failed to promote entry {key}: {e}")
    
    async def _evict_lru(self):
        """
        Evict least recently used items to warm cache
        Performance: Maintain 80% hot cache utilization
        """
        target_size = int(self.max_hot_size * 0.8)
        evicted_count = 0
        
        # Also evict if we have too many items (configurable limit)
        max_hot_items = int(os.getenv('MAX_HOT_CACHE_ITEMS', '100'))
        while (self.current_hot_size > target_size or len(self.hot_cache) >= max_hot_items) and self.hot_cache:
            # Get least recently used item
            key, entry = self.hot_cache.popitem(last=False)
            self.current_hot_size -= entry.size
            evicted_count += 1
            
            # Move to warm cache
            await self._store_warm(key, entry)
        
        if evicted_count > 0:
            self.metrics['evictions'] += evicted_count
            logger.debug(f"Evicted {evicted_count} entries to warm cache")
    
    async def _store_warm(self, key: str, entry: CacheEntry):
        """
        Store entry in warm cache (disk)
        """
        try:
            warm_path = self.warm_cache_dir / f"{key}.pkl.gz"
            
            # Compress and save
            with gzip.open(warm_path, 'wb', compresslevel=6) as f:
                pickle.dump(entry, f)
            
            # Update index
            self.warm_index[key] = {
                'path': str(warm_path),
                'size': warm_path.stat().st_size,
                'created': entry.created.isoformat()
            }
            
            self._save_warm_index()
            logger.debug(f"Stored in warm cache: {key}")
            
        except Exception as e:
            logger.error(f"Failed to store warm cache entry {key}: {e}")
    
    def _load_warm_index(self):
        """Load warm cache index from disk"""
        index_path = self.warm_cache_dir / "index.json"
        if index_path.exists():
            try:
                with open(index_path, 'r') as f:
                    self.warm_index = json.load(f)
                logger.info(f"Loaded warm cache index with {len(self.warm_index)} entries")
            except Exception as e:
                logger.error(f"Failed to load warm cache index: {e}")
                self.warm_index = {}
    
    def _save_warm_index(self):
        """Save warm cache index to disk"""
        try:
            index_path = self.warm_cache_dir / "index.json"
            with open(index_path, 'w') as f:
                json.dump(self.warm_index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save warm cache index: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Return cache performance metrics
        Business Value: Track token savings and cache effectiveness
        """
        total = self.metrics['total_requests']
        hits = self.metrics['hits']
        
        hit_rate = (hits / total) if total > 0 else 0
        
        return {
            'hit_rate': round(hit_rate, 2),
            'tokens_saved': self.metrics['tokens_saved'],
            'hot_cache_size_mb': round(self.current_hot_size / (1024 * 1024), 2),
            'warm_cache_files': len(self.warm_index),
            'total_requests': total,
            'hits': hits,
            'misses': self.metrics['misses'],
            'hot_hits': self.metrics['hot_hits'],
            'warm_hits': self.metrics['warm_hits'],
            'evictions': self.metrics['evictions'],
            'target_hit_rate': self.target_hit_rate * 100
        }
    
    async def clear(self):
        """Clear all cache entries"""
        self.hot_cache.clear()
        self.current_hot_size = 0
        
        # Clear warm cache
        for path in self.warm_cache_dir.glob("*.pkl.gz"):
            path.unlink()
        
        self.warm_index = {}
        self._save_warm_index()
        
        # Reset metrics
        self.metrics = {
            'hits': 0,
            'misses': 0,
            'hot_hits': 0,
            'warm_hits': 0,
            'tokens_saved': 0,
            'total_requests': 0,
            'evictions': 0
        }
        
        logger.info("Cache cleared")
    
    async def load_from_database(self, db_manager):
        """Load persisted cache from database on startup"""
        try:
            if hasattr(db_manager, 'pool') and db_manager.pool:
                async with db_manager.pool.acquire() as conn:
                    rows = await conn.fetch(
                        "SELECT key, value, metadata FROM cache_entries WHERE active = true"
                    )
                    for row in rows:
                        self.hot_cache[row['key']] = {
                            'value': row['value'],
                            'metadata': row['metadata'],
                            'timestamp': datetime.now()
                        }
        except Exception as e:
            # Log but don't fail - cache can work without persistence
            print(f"[INFO] Could not load cache from database: {e}")
    
    async def save_to_database(self, db_manager):
        """Save cache to database for persistence"""
        try:
            if hasattr(db_manager, 'pool') and db_manager.pool:
                async with db_manager.pool.acquire() as conn:
                    # Clear existing entries
                    await conn.execute("DELETE FROM cache_entries")
                    # Save current cache
                    for key, entry in self.hot_cache.items():
                        await conn.execute(
                            "INSERT INTO cache_entries (key, value, metadata, active) VALUES ($1, $2, $3, true)",
                            key, entry.get('value'), entry.get('metadata', {})
                        )
        except Exception as e:
            # Log but don't fail - cache can work without persistence
            print(f"[INFO] Could not save cache to database: {e}")