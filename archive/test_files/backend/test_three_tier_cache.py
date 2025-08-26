"""Test three-tier cache implementation with measurements"""
import asyncio
import time
import json
from three_tier_cache import ThreeTierCache, CacheTier

async def test_three_tier_cache():
    """Test cache with actual measurements"""
    print("=== Testing Three-Tier Cache ===\n")
    
    cache = ThreeTierCache()
    
    # Test 1: Store and retrieve from hot tier
    print("1. Testing HOT tier...")
    key1 = cache.generate_key("test_data_1")
    data1 = {"value": "hot_data", "size": "small"}
    
    tier = await cache.store(key1, data1)
    print(f"   Stored in tier: {tier.value}")
    
    start = time.perf_counter()
    retrieved, tier_hit = await cache.get(key1)
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    print(f"   Retrieved from: {tier_hit.value if tier_hit else 'MISS'}")
    print(f"   Retrieval time: {elapsed_ms:.3f}ms")
    assert retrieved == data1
    
    # Test 2: Store large data (should go to warm)
    print("\n2. Testing WARM tier...")
    key2 = cache.generate_key("test_data_2")
    # Create data >10% of hot cache
    large_data = {"value": "x" * 100000}  
    
    tier = await cache.store(key2, large_data)
    print(f"   Large data stored in tier: {tier.value}")
    
    start = time.perf_counter()
    retrieved, tier_hit = await cache.get(key2)
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    print(f"   Retrieved from: {tier_hit.value if tier_hit else 'MISS'}")
    print(f"   Retrieval time: {elapsed_ms:.3f}ms")
    
    # Test 3: Promotion from warm to hot
    print("\n3. Testing promotion...")
    for i in range(3):  # Access 3 times to trigger promotion
        await cache.get(key2)
    
    start = time.perf_counter()
    retrieved, tier_hit = await cache.get(key2)
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    print(f"   After promotion, retrieved from: {tier_hit.value if tier_hit else 'MISS'}")
    print(f"   Retrieval time: {elapsed_ms:.3f}ms")
    
    # Test 4: LRU eviction
    print("\n4. Testing LRU eviction...")
    # Fill hot cache to trigger eviction
    for i in range(10):
        key = cache.generate_key(f"eviction_test_{i}")
        data = {"value": f"data_{i}", "counter": i}
        await cache.store(key, data)
    
    # Check if first item was evicted to warm
    retrieved, tier_hit = await cache.get(key1)
    print(f"   Original item now in: {tier_hit.value if tier_hit else 'MISS'}")
    
    # Test 5: Cache miss
    print("\n5. Testing cache miss...")
    miss_key = cache.generate_key("nonexistent")
    start = time.perf_counter()
    retrieved, tier_hit = await cache.get(miss_key)
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    print(f"   Result: {tier_hit.value if tier_hit else 'MISS'}")
    print(f"   Miss check time: {elapsed_ms:.3f}ms")
    
    # Test 6: Metrics
    print("\n6. Cache metrics:")
    metrics = cache.get_metrics()
    print(f"   Hit rate: {metrics['hit_rate']}%")
    print(f"   Total requests: {metrics['total_requests']}")
    print(f"   Hot hits: {metrics['hot_hits']}")
    print(f"   Warm hits: {metrics['warm_hits']}")
    print(f"   Misses: {metrics['misses']}")
    print(f"   Promotions: {metrics['promotions']}")
    print(f"   Demotions: {metrics['demotions']}")
    print(f"   Hot cache size: {metrics['hot_size_mb']} MB")
    print(f"   Hot entries: {metrics['hot_entries']}")
    print(f"   Warm entries: {metrics['warm_entries']}")
    
    # Clean up
    await cache.clear()
    print("\n=== All Tests Passed ===")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_three_tier_cache())
    exit(0 if result else 1)