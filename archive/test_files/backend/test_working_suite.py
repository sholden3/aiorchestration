"""
Working Test Suite - Evidence-Based Testing
Three-Persona Collaborative Test Implementation
"""

import pytest
import time
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import sys
sys.path.append('.')

# Import modules to test
from enhanced_cache_abstraction import EnhancedCacheAbstraction, CacheMonitoring
from config import Config
from persona_manager import PersonaManager, PersonaType

class TestCacheSystem:
    """Marcus: System infrastructure tests"""
    
    def test_cache_initialization(self):
        """Test cache can be initialized"""
        cache = EnhancedCacheAbstraction({'hot_size_mb': 10})
        assert cache is not None
        assert cache.config['hot_size_mb'] == 10
        print("[SYMBOL] Cache initialization successful")
    
    @pytest.mark.asyncio
    async def test_cache_operations(self):
        """Test basic cache operations"""
        cache = EnhancedCacheAbstraction()
        
        # Test storage
        result = await cache.cache_data("test_key", {"data": "test"})
        assert result == True
        
        # Test retrieval
        data = await cache.get_data("test_key")
        assert data == {"data": "test"}
        
        # Test metrics
        metrics = cache.get_metrics()
        assert metrics['total_operations'] == 2
        assert metrics['success_rate'] == 100.0
        print(f"[SYMBOL] Cache operations: {metrics['total_operations']} ops at {metrics['success_rate']:.0f}% success")
    
    def test_cache_monitoring(self):
        """Test monitoring functionality"""
        monitor = CacheMonitoring()
        
        # Record operations
        monitor.record_operation('cache', 'key1', 100, 5.0, True)
        monitor.record_operation('get', 'key1', 100, 2.0, True)
        monitor.record_operation('cache', 'key2', 200, 10.0, False)
        
        metrics = monitor.get_metrics()
        assert metrics['total_operations'] == 3
        assert metrics['success_rate'] == pytest.approx(66.67, 0.1)
        assert metrics['avg_duration_ms'] == pytest.approx(5.67, 0.1)
        print(f"[SYMBOL] Monitoring: {metrics['total_operations']} ops tracked")

class TestConfiguration:
    """Sarah: Configuration and AI setup tests"""
    
    def test_config_initialization(self):
        """Test configuration system"""
        config = Config()
        
        # AI config
        assert config.ai.claude_max_tokens == 4000
        assert config.ai.claude_timeout_seconds == 30
        
        # Systems config
        assert config.systems.cache_hot_size_mb == 512
        assert config.systems.target_cache_hit_rate == 0.90
        
        # UX config
        assert config.ux.terminal_default_cols == 120
        print("[SYMBOL] Configuration loaded successfully")
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = Config()
        
        # Should validate successfully
        assert config.validate() == True
        
        # Test invalid config
        config.systems.cache_hot_size_mb = 3000  # Larger than warm
        config.systems.cache_warm_size_mb = 2000
        
        with pytest.raises(AssertionError):
            config.validate()
        print("[SYMBOL] Configuration validation working")

class TestPersonaSystem:
    """Emily: Persona and user interaction tests"""
    
    def test_persona_manager_initialization(self):
        """Test persona manager setup"""
        manager = PersonaManager()
        
        assert manager is not None
        assert len(manager.personas) == 3
        print(f"[SYMBOL] Persona manager initialized with {len(manager.personas)} personas")
    
    def test_persona_suggestion(self):
        """Test persona suggestion based on keywords"""
        manager = PersonaManager()
        
        # Test database-related task
        task = "Optimize database queries for better performance"
        suggested = manager.suggest_persona(task)
        
        assert len(suggested) > 0
        assert PersonaType.MARCUS_RODRIGUEZ in suggested
        print(f"[SYMBOL] Persona suggestion working: {len(suggested)} personas suggested")
    
    def test_persona_execution(self):
        """Test persona conflict resolution"""
        manager = PersonaManager()
        
        # Test conflict resolution with multiple responses
        responses = {
            'ai_integration': 'AI solution',
            'systems_performance': 'Performance solution',
            'ux_frontend': 'UX solution'
        }
        
        result = manager.resolve_conflict(responses)
        assert 'selected' in result
        assert 'method' in result
        assert result['selected'] is not None
        print("[SYMBOL] Persona conflict resolution working")

class TestIntegration:
    """All personas: Integration tests"""
    
    @pytest.mark.asyncio
    async def test_cache_config_integration(self):
        """Test cache and configuration integration"""
        config_dict = {
            'hot_size_mb': 20,
            'warm_size_mb': 40,
            'ttl_default_hours': 2
        }
        
        cache = EnhancedCacheAbstraction(config_dict)
        
        # Store data
        await cache.cache_data("integration_test", {"test": "data"})
        
        # Verify configuration applied
        assert cache.config['hot_size_mb'] == 20
        assert cache.config['ttl_default_hours'] == 2
        
        # Verify data stored
        data = await cache.get_data("integration_test")
        assert data == {"test": "data"}
        print("[SYMBOL] Cache-config integration working")
    
    def test_system_components_availability(self):
        """Test all system components are available"""
        components = []
        
        try:
            from cache_manager import IntelligentCache
            components.append("IntelligentCache")
        except ImportError:
            pass
        
        try:
            from persona_manager import PersonaManager
            components.append("PersonaManager")
        except ImportError:
            pass
        
        try:
            from config import Config
            components.append("Config")
        except ImportError:
            pass
        
        assert len(components) >= 3
        print(f"[SYMBOL] System components available: {', '.join(components)}")

def measure_test_performance():
    """Measure actual test execution time"""
    start_time = time.perf_counter()
    
    # Run a sample operation
    cache = EnhancedCacheAbstraction()
    asyncio.run(cache.cache_data("perf_test", {"data": "x" * 1000}))
    
    end_time = time.perf_counter()
    execution_time = (end_time - start_time) * 1000
    
    print(f"[SYMBOL] Test performance: {execution_time:.2f}ms")
    assert execution_time < 100  # Should be fast

if __name__ == "__main__":
    print("=" * 60)
    print("WORKING TEST SUITE EXECUTION")
    print("=" * 60)
    
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])