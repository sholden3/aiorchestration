"""
Simple test to validate cache implementation
"""

import asyncio
from enhanced_cache_abstraction import EnhancedCacheAbstraction

async def test_simple():
    """Simple test of cache functionality"""
    print("Creating cache...")
    cache = EnhancedCacheAbstraction()
    
    print("Testing cache_data...")
    result = await cache.cache_data("test_key", {"test": "data"})
    print(f"Cache result: {result}")
    print(f"Cache type: {type(cache._cache)}")
    print(f"Cache has store: {hasattr(cache._cache, 'store')}")
    
    if not result:
        print("Using dict fallback...")
        # Force dict fallback
        cache._cache = {}
        result = await cache.cache_data("test_key", {"test": "data"})
        print(f"Fallback result: {result}")
    
    print("Testing get_data...")
    data = await cache.get_data("test_key")
    print(f"Retrieved: {data}")
    
    print("Getting metrics...")
    metrics = cache.get_metrics()
    print(f"Metrics: {metrics}")
    
    print("Getting status...")
    status = cache.get_status()
    print(f"Status: {status}")

if __name__ == "__main__":
    asyncio.run(test_simple())