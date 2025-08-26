"""
Realistic Tests for Enhanced Cache Abstraction
Evidence-Based Testing with Actual Execution
"""

import asyncio
import time
import json
import sys
sys.path.append('.')

from enhanced_cache_abstraction import EnhancedCacheAbstraction, CacheMonitoring

def test_basic_functionality():
    """Test actual cache functionality with measurable criteria"""
    print("\n=== Testing Basic Functionality ===")
    
    # Setup with real configuration
    config = {
        'hot_size_mb': 10,  # Small size for testing
        'warm_size_mb': 20,
        'cache_dir': './test_cache',
        'ttl_default_hours': 1
    }
    
    cache = EnhancedCacheAbstraction(config)
    
    # Use asyncio.run for async operations
    async def run_tests():
        # Test 1: Basic storage and retrieval
        print("Test 1: Basic storage and retrieval")
        test_data = {"test": "data", "size": 1024}
        result = await cache.cache_data("test_key", test_data, "generic")
        assert result == True, "Failed to cache data"
        print(f"  [SYMBOL] Cached data successfully: {result}")
        
        retrieved = await cache.get_data("test_key", "generic")
        assert retrieved == test_data, f"Data mismatch: {retrieved} != {test_data}"
        print(f"  [SYMBOL] Retrieved data matches: {retrieved == test_data}")
        
        # Test 2: Type-aware prefixing
        print("\nTest 2: Type-aware prefixing")
        ast_data = {"ast": "tree", "nodes": 100}
        result = await cache.cache_data("file1", ast_data, "ast")
        assert result == True, "Failed to cache AST data"
        print(f"  [SYMBOL] Cached AST data: {result}")
        
        # Verify different types don't collide
        doc_data = {"doc": "content", "pages": 5}
        result = await cache.cache_data("file1", doc_data, "document")  # Same key, different type
        assert result == True, "Failed to cache document data"
        print(f"  [SYMBOL] Cached document data with same key: {result}")
        
        # Retrieve both
        ast_retrieved = await cache.get_data("file1", "ast")
        doc_retrieved = await cache.get_data("file1", "document")
        assert ast_retrieved == ast_data, "AST data corrupted"
        assert doc_retrieved == doc_data, "Document data corrupted"
        print(f"  [SYMBOL] Different data types isolated correctly")
        
        # Test 3: Error handling
        print("\nTest 3: Error handling")
        try:
            await cache.cache_data("", test_data)  # Empty key should fail
            assert False, "Should have raised ValueError for empty key"
        except ValueError as e:
            print(f"  [SYMBOL] Correct error handling for empty key: {e}")
        
        try:
            await cache.cache_data("test", test_data, "invalid_type")  # Invalid type
            assert False, "Should have raised ValueError for invalid type"
        except ValueError as e:
            print(f"  [SYMBOL] Correct error handling for invalid type: {e}")
    
    asyncio.run(run_tests())
    print("\n[SYMBOL] All basic functionality tests passed")

def test_performance_monitoring():
    """Test that monitoring reports accurate, measurable data"""
    print("\n=== Testing Performance Monitoring ===")
    
    cache = EnhancedCacheAbstraction({'hot_size_mb': 10, 'warm_size_mb': 20})
    
    async def run_tests():
        # Perform some operations
        operations = [
            ("key1", {"data": "x" * 100}),  # 100 bytes
            ("key2", {"data": "x" * 1000}), # 1000 bytes
            ("key3", {"data": "x" * 500}),  # 500 bytes
        ]
        
        for key, data in operations:
            await cache.cache_data(key, data)
            await cache.get_data(key)
        
        # Get metrics
        metrics = cache.get_metrics()
        
        print(f"Metrics collected:")
        print(f"  Total operations: {metrics['total_operations']}")
        print(f"  Success rate: {metrics['success_rate']:.1f}%")
        print(f"  Average duration: {metrics['avg_duration_ms']:.2f}ms")
        print(f"  Total data size: {metrics['total_data_size']} bytes")
        
        # Verify metrics are reasonable
        assert metrics['total_operations'] == 6, f"Expected 6 operations, got {metrics['total_operations']}"
        assert metrics['success_rate'] == 100.0, f"Expected 100% success, got {metrics['success_rate']}"
        assert metrics['avg_duration_ms'] >= 0, "Duration should be positive"
        assert metrics['total_data_size'] > 0, "Data size should be positive"
        
        # Test user-friendly status
        status = cache.get_status()
        print(f"\nUser-friendly status:")
        print(f"  Operational: {status['operational']}")
        print(f"  Success rate: {status['success_rate']}")
        print(f"  Average response: {status['average_response_ms']}")
        print(f"  Recommendation: {status['recommendation']}")
        
        assert status['operational'] == True, "Cache should be operational"
        assert 'recommendation' in status, "Should provide recommendation"
    
    asyncio.run(run_tests())
    print("\n[SYMBOL] Performance monitoring tests passed")

def test_configuration_validation():
    """Test configuration validation with actual error scenarios"""
    print("\n=== Testing Configuration Validation ===")
    
    # Test 1: Valid configuration
    print("Test 1: Valid configuration")
    valid_config = {'hot_size_mb': 100, 'warm_size_mb': 200}
    try:
        cache = EnhancedCacheAbstraction(valid_config)
        print("  [SYMBOL] Valid configuration accepted")
    except Exception as e:
        assert False, f"Valid config rejected: {e}"
    
    # Test 2: Invalid hot size
    print("\nTest 2: Invalid hot cache size")
    try:
        invalid_config = {'hot_size_mb': -10, 'warm_size_mb': 200}
        cache = EnhancedCacheAbstraction(invalid_config)
        assert False, "Should have rejected negative hot_size_mb"
    except ValueError as e:
        print(f"  [SYMBOL] Correctly rejected negative size: {e}")
    
    # Test 3: Warm smaller than hot
    print("\nTest 3: Warm cache smaller than hot")
    try:
        invalid_config = {'hot_size_mb': 200, 'warm_size_mb': 100}
        cache = EnhancedCacheAbstraction(invalid_config)
        assert False, "Should have rejected warm < hot"
    except ValueError as e:
        print(f"  [SYMBOL] Correctly rejected invalid sizes: {e}")
    
    print("\n[SYMBOL] Configuration validation tests passed")

def test_data_type_isolation():
    """Test that different data types are properly isolated"""
    print("\n=== Testing Data Type Isolation ===")
    
    cache = EnhancedCacheAbstraction()
    
    async def run_tests():
        # Store same key with different types
        key = "shared_key"
        
        generic_data = {"type": "generic", "value": 1}
        ast_data = {"type": "ast", "value": 2}
        doc_data = {"type": "document", "value": 3}
        meta_data = {"type": "metadata", "value": 4}
        
        # Cache all types
        await cache.cache_data(key, generic_data, "generic")
        await cache.cache_data(key, ast_data, "ast")
        await cache.cache_data(key, doc_data, "document")
        await cache.cache_data(key, meta_data, "metadata")
        
        # Retrieve and verify isolation
        retrieved_generic = await cache.get_data(key, "generic")
        retrieved_ast = await cache.get_data(key, "ast")
        retrieved_doc = await cache.get_data(key, "document")
        retrieved_meta = await cache.get_data(key, "metadata")
        
        assert retrieved_generic == generic_data, "Generic data corrupted"
        assert retrieved_ast == ast_data, "AST data corrupted"
        assert retrieved_doc == doc_data, "Document data corrupted"
        assert retrieved_meta == meta_data, "Metadata corrupted"
        
        print(f"  [SYMBOL] All data types properly isolated")
        print(f"    Generic: {retrieved_generic['value']} == 1")
        print(f"    AST: {retrieved_ast['value']} == 2")
        print(f"    Document: {retrieved_doc['value']} == 3")
        print(f"    Metadata: {retrieved_meta['value']} == 4")
    
    asyncio.run(run_tests())
    print("\n[SYMBOL] Data type isolation tests passed")

def measure_actual_performance():
    """Measure actual cache performance with real operations"""
    print("\n=== Measuring Actual Performance ===")
    
    cache = EnhancedCacheAbstraction()
    
    async def run_benchmarks():
        # Benchmark different data sizes
        sizes = [100, 1000, 10000, 100000]  # bytes
        
        for size in sizes:
            data = {"data": "x" * size}
            
            # Measure cache operation
            start = time.perf_counter()
            await cache.cache_data(f"perf_test_{size}", data)
            cache_time = (time.perf_counter() - start) * 1000
            
            # Measure retrieval
            start = time.perf_counter()
            retrieved = await cache.get_data(f"perf_test_{size}")
            get_time = (time.perf_counter() - start) * 1000
            
            print(f"  Size {size:6} bytes: Cache={cache_time:6.2f}ms, Get={get_time:6.2f}ms")
            
            # Verify data integrity
            assert retrieved == data, f"Data corrupted for size {size}"
    
    asyncio.run(run_benchmarks())
    print("\n[SYMBOL] Performance measurements completed")

if __name__ == "__main__":
    print("=" * 60)
    print("ENHANCED CACHE ABSTRACTION - REALISTIC TESTING")
    print("=" * 60)
    
    # Run all tests
    test_basic_functionality()
    test_performance_monitoring()
    test_configuration_validation()
    test_data_type_isolation()
    measure_actual_performance()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED - IMPLEMENTATION VALIDATED")
    print("=" * 60)