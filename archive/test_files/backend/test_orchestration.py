"""
Orchestrated Test Suite
All three personas collaborate on comprehensive testing
Architecture: Pytest with async support, fixtures, and parametrization
Coverage: Unit, Integration, Performance, and Orchestration tests
"""

import pytest
import asyncio
import asyncpg
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json
import os

# Import modules to test
from config import Config, AIIntegrationConfig, SystemsPerformanceConfig, UXFrontendConfig
from base_patterns import (
    OrchestrationResult,
    orchestrated_error_handler,
    DatabaseOperation,
    MetricsCollectorBase,
    PersonaOperation,
    OrchestrationContext
)
from cache_manager import IntelligentCache, CacheEntry
from persona_manager import PersonaManager, PersonaType
from claude_integration import ClaudeOptimizer
from database_manager import DatabaseManager
from metrics_collector import MetricsCollector

# ============================================================================
# FIXTURES (Shared test infrastructure)
# ============================================================================

@pytest.fixture
def config():
    """Provide test configuration"""
    return Config()

@pytest.fixture
async def db_pool():
    """Provide test database pool with fallback to mock"""
    try:
        # Try real PostgreSQL connection first
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_user = os.getenv('DB_USER', 'postgres')
        db_pass = os.getenv('DB_PASS', 'postgres')
        db_name = os.getenv('TEST_DB_NAME', 'test_ai_assistant')
        pool = await asyncpg.create_pool(
            f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}",
            min_size=1,
            max_size=2
        )
        yield pool
        await pool.close()
    except Exception as e:
        # Fallback to mock if PostgreSQL not available
        import test_db_mock
        test_db_mock.patch_asyncpg()
        pool = await test_db_mock.create_mock_pool()
        yield pool
        await pool.close()

@pytest.fixture
async def cache():
    """Provide test cache instance"""
    return IntelligentCache(hot_size_mb=10, warm_size_mb=50)

@pytest.fixture
def persona_manager():
    """Provide test persona manager"""
    return PersonaManager()

@pytest.fixture
def metrics_collector():
    """Provide test metrics collector"""
    return MetricsCollector(window_size=100)

@pytest.fixture
def claude_optimizer(cache):
    """Provide test Claude optimizer"""
    return ClaudeOptimizer(cache)

# ============================================================================
# DR. SARAH CHEN'S TESTS (AI Integration)
# ============================================================================

class TestAIIntegration:
    """Tests for AI and Claude integration components"""
    
    def test_token_estimation(self, claude_optimizer):
        """Test token estimation accuracy"""
        prompt = "Test prompt with some content"
        response = "Test response with more content"
        
        estimated = claude_optimizer._estimate_tokens(prompt, response)
        
        # Should be approximately (30 + 32) / 4 = 15.5 tokens
        assert 14 <= estimated <= 17
    
    def test_persona_prompt_formatting(self, claude_optimizer):
        """Test persona-specific prompt formatting"""
        base_prompt = "Optimize this code"
        
        formatted = claude_optimizer._format_with_persona(
            base_prompt,
            "ai_integration",
            {"context": "test"}
        )
        
        assert "Dr. Sarah Chen" in formatted
        assert "Claude API optimization" in formatted
        assert base_prompt in formatted
    
    @pytest.mark.parametrize("persona,keywords", [
        ("ai_integration", ["claude", "api", "optimization"]),
        ("systems_performance", ["cache", "database", "performance"]),
        ("ux_frontend", ["ui", "dashboard", "user experience"])
    ])
    def test_persona_keyword_detection(self, persona_manager, persona, keywords):
        """Test persona suggestion based on keywords"""
        for keyword in keywords:
            task = f"Help me with {keyword} issues"
            suggested = persona_manager.suggest_persona(task)
            
            assert len(suggested) > 0
            assert persona in [p.value for p in suggested]
    
    async def test_claude_fallback_mechanism(self, claude_optimizer):
        """Test fallback when Claude is unavailable"""
        with patch.object(claude_optimizer, '_execute_claude_cli', 
                         side_effect=Exception("API Error")):
            
            result = await claude_optimizer.execute_with_persona(
                "Test prompt",
                persona="ai_integration"
            )
            
            assert not result['success']
            assert 'fallback' in result
            assert "Claude Code is currently unavailable" in result['fallback']
    
    def test_confidence_threshold_validation(self, config):
        """Test persona confidence threshold configuration"""
        assert 0 <= config.ai.persona_confidence_threshold <= 1
        
        # Test validation
        config.ai.persona_confidence_threshold = 1.5
        with pytest.raises(AssertionError):
            config.validate()

# ============================================================================
# MARCUS RODRIGUEZ'S TESTS (Systems Performance)
# ============================================================================

class TestSystemsPerformance:
    """Tests for performance, caching, and database components"""
    
    async def test_cache_hot_cold_tiers(self, cache):
        """Test two-tier cache operation"""
        key = "test_key"
        data = {"test": "data", "timestamp": datetime.now().isoformat()}
        
        # Store in hot cache
        await cache.set(key, data, ttl=60)
        assert key in cache.hot_cache
        
        # Simulate hot cache pressure
        for i in range(20):
            await cache.set(f"key_{i}", {"data": i}, ttl=60)
        
        # Original should move to warm
        assert key not in cache.hot_cache
        # Fix: Use correct file extension (.pkl.gz instead of .cache)
        warm_path = cache.warm_cache_dir / f"{key}.pkl.gz"
        assert warm_path.exists()
    
    async def test_cache_hit_rate_calculation(self, metrics_collector):
        """Test cache hit rate metrics"""
        # Record some hits and misses
        for _ in range(90):
            metrics_collector.record_cache_hit()
        for _ in range(10):
            metrics_collector.record_cache_miss()
        
        hit_rate = metrics_collector.get_cache_hit_rate()
        assert hit_rate == 90.0
    
    async def test_database_connection_pooling(self, db_pool):
        """Test connection pool efficiency"""
        # Acquire multiple connections concurrently
        async def query_task(pool):
            async with pool.acquire() as conn:
                return await conn.fetchval("SELECT 1")
        
        tasks = [query_task(db_pool) for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        assert all(r == 1 for r in results)
        assert db_pool.get_size() <= 2  # Max pool size
    
    def test_metrics_window_sliding(self, metrics_collector):
        """Test rolling window for metrics"""
        # Fill window beyond capacity (window_size is 100 in fixture)
        for i in range(150):
            metrics_collector.record_response_time(i)
        
        # Should only keep last 100 (window size from fixture)
        assert len(metrics_collector.response_times) == 100
        assert metrics_collector.response_times[0] == 50  # First kept value
    
    async def test_performance_target_validation(self, config):
        """Test performance target configurations"""
        assert config.systems.target_cache_hit_rate == 0.90
        assert config.systems.target_token_reduction == 0.65
        assert config.systems.target_response_time_ms == 500

# ============================================================================
# EMILY WATSON'S TESTS (UX/Frontend)
# ============================================================================

class TestUXFrontend:
    """Tests for UI, terminal, and user experience components"""
    
    def test_terminal_configuration(self, config):
        """Test terminal default settings"""
        assert config.ux.terminal_default_cols == 120
        assert config.ux.terminal_default_rows == 30
        assert config.ux.terminal_scrollback_lines == 10000
    
    def test_accessibility_configuration(self, config):
        """Test accessibility settings"""
        assert config.ux.accessibility_screen_reader == True
        assert config.ux.accessibility_keyboard_nav == True
        
        # High contrast should be configurable
        config.ux.accessibility_high_contrast = True
        assert config.ux.accessibility_high_contrast == True
    
    def test_dashboard_refresh_intervals(self, config):
        """Test dashboard update frequencies"""
        assert config.ux.dashboard_refresh_interval_ms == 5000
        assert config.ux.ui_debounce_delay_ms == 300
        assert config.ux.ui_auto_save_interval_seconds == 30
    
    def test_theme_validation(self, config):
        """Test theme configuration"""
        assert config.ux.ui_theme in ["dark", "light"]
        
        # Test invalid theme
        config.ux.ui_theme = "invalid"
        with pytest.raises(AssertionError):
            config.validate()
    
    def test_ui_animation_settings(self, config):
        """Test UI animation configuration"""
        assert config.ux.ui_animation_duration_ms == 200
        assert isinstance(config.ux.ui_animation_duration_ms, int)
        assert config.ux.ui_animation_duration_ms > 0

# ============================================================================
# ORCHESTRATION TESTS (All Three Personas)
# ============================================================================

class TestOrchestration:
    """Tests requiring collaboration between all personas"""
    
    async def test_full_request_flow(self, persona_manager, cache, claude_optimizer):
        """Test complete request processing flow"""
        # User request
        task = "Help me optimize my Python code for better performance"
        
        # Sarah: Persona selection
        personas = persona_manager.suggest_persona(task)
        assert len(personas) > 0
        
        # Marcus: Cache check
        cache_key = cache.generate_key(task, personas[0].value)
        cached = await cache.get(cache_key)
        assert cached is None  # First request
        
        # Sarah: Claude execution (mocked)
        with patch.object(claude_optimizer, '_execute_claude_cli', 
                         return_value={'success': True, 'response': 'Test response'}):
            result = await claude_optimizer.execute_with_persona(
                task,
                persona=personas[0].value
            )
        
        assert result['success']
        assert result['response'] == 'Test response'
        
        # Marcus: Cache storage
        await cache.set(cache_key, result, ttl=3600)
        
        # Emily: Response formatting would happen here
        assert 'persona' in result
        assert 'execution_time' in result
    
    async def test_persona_conflict_resolution(self, persona_manager):
        """Test voting mechanism for persona conflicts"""
        responses = {
            'ai_integration': ('Use Claude API', 0.9),
            'systems_performance': ('Optimize database', 0.7),
            'ux_frontend': ('Improve UI', 0.8)
        }
        
        resolved = persona_manager.resolve_conflict(responses)
        
        assert resolved['winner'] == 'ai_integration'  # Highest confidence
        assert resolved['confidence'] == 0.9
        assert 'voting_details' in resolved
    
    async def test_orchestration_result_wrapper(self):
        """Test unified result wrapper"""
        # Success case
        success_result = OrchestrationResult.ok(
            {"data": "test"},
            persona="test_persona",
            execution_time=0.5
        )
        
        assert success_result.success == True
        assert success_result.data == {"data": "test"}
        assert success_result.metadata['persona'] == "test_persona"
        
        # Failure case
        fail_result = OrchestrationResult.fail(
            "Test error",
            technical_error="Stack trace here"
        )
        
        assert fail_result.success == False
        assert fail_result.error == "Test error"
        assert fail_result.metadata['technical_error'] == "Stack trace here"
    
    @pytest.mark.parametrize("error,expected_message", [
        ("Connection refused", "Unable to connect to the service"),
        ("Timeout error", "The operation took too long"),
        ("Permission denied", "You don't have permission"),
        ("Not found", "The requested resource was not found"),
        ("Invalid input", "The provided input is invalid")
    ])
    async def test_error_handler_decorator(self, error, expected_message):
        """Test orchestrated error handling"""
        @orchestrated_error_handler(fallback_value="fallback", persona="test")
        async def failing_function():
            raise Exception(error)
        
        result = await failing_function()
        
        assert not result.success
        assert expected_message in result.error
        assert result.metadata['fallback'] == "fallback"
        assert result.metadata['persona'] == "test"
    
    async def test_cross_persona_validation(self, config):
        """Test configuration validation across all domains"""
        # Each persona validates their domain
        assert config.validate()
        
        # Cross-domain validation
        assert config.systems.cache_hot_size_mb < config.systems.cache_warm_size_mb
        assert config.ai.claude_timeout_seconds < config.systems.metrics_collection_interval
        assert config.ux.dashboard_refresh_interval_ms > config.ux.ui_animation_duration_ms

# ============================================================================
# PERFORMANCE TESTS (Orchestrated)
# ============================================================================

class TestPerformance:
    """Performance benchmarks for orchestrated operations"""
    
    @pytest.mark.benchmark
    async def test_cache_operation_speed(self, cache, benchmark):
        """Benchmark cache operations"""
        data = {"test": "data" * 100}
        
        async def cache_operations():
            key = f"perf_test_{datetime.now().timestamp()}"
            await cache.set(key, data, ttl=60)
            result = await cache.get(key)
            return result
        
        result = await benchmark(cache_operations)
        assert result is not None
    
    @pytest.mark.benchmark
    async def test_persona_selection_speed(self, persona_manager, benchmark):
        """Benchmark persona selection"""
        tasks = [
            "Help with Claude API",
            "Optimize database queries",
            "Improve UI design",
            "Debug performance issues"
        ]
        
        def select_personas():
            results = []
            for task in tasks:
                personas = persona_manager.suggest_persona(task)
                results.append(personas)
            return results
        
        results = benchmark(select_personas)
        assert all(len(r) > 0 for r in results)
    
    @pytest.mark.benchmark
    async def test_metrics_aggregation_speed(self, metrics_collector, benchmark):
        """Benchmark metrics calculation"""
        # Pre-populate metrics
        for i in range(1000):
            metrics_collector.record_response_time(i % 500)
            if i % 2:
                metrics_collector.record_cache_hit()
            else:
                metrics_collector.record_cache_miss()
        
        async def calculate_metrics():
            summary = await metrics_collector.get_performance_summary()
            return summary
        
        summary = await benchmark(calculate_metrics)
        assert 'cache' in summary
        assert 'response_times' in summary

# ============================================================================
# INTEGRATION TESTS (Cross-Component)
# ============================================================================

class TestIntegration:
    """Integration tests between components"""
    
    async def test_cache_database_integration(self, cache, db_pool):
        """Test cache backed by database"""
        # Mock database manager
        db_manager = DatabaseManager()
        db_manager.pool = db_pool
        
        # Store in cache and database
        key = "integration_test"
        data = {"test": "integration"}
        
        await cache.set(key, data, ttl=3600)
        await db_manager.save_cache_entry(
            key,
            data,
            datetime.now() + timedelta(hours=1),
            tier='hot'
        )
        
        # Retrieve from database
        db_result = await db_manager.get_cache_entry(key)
        assert db_result == data
    
    async def test_metrics_database_persistence(self, metrics_collector, db_pool):
        """Test metrics persistence to database"""
        db_manager = DatabaseManager()
        db_manager.pool = db_pool
        
        # Record metrics
        metrics_collector.record_response_time(250)
        metrics_collector.record_cache_hit()
        metrics_collector.record_token_usage(1000, 500)
        
        # Save to database
        await db_manager.log_performance(
            "test_operation",
            250,
            True,
            {"tokens": 1000}
        )
        
        # Verify saved
        summary = await db_manager.get_metrics_summary()
        assert summary is not None

# ============================================================================
# END-TO-END TESTS (Full System)
# ============================================================================

class TestEndToEnd:
    """End-to-end tests simulating real usage"""
    
    @pytest.mark.e2e
    async def test_complete_user_journey(self, persona_manager, cache, claude_optimizer, metrics_collector):
        """Test complete user journey from request to response"""
        
        # 1. User submits request
        user_request = "Help me build a REST API with FastAPI"
        
        # 2. System suggests personas
        suggested_personas = persona_manager.suggest_persona(user_request)
        assert PersonaType.MARCUS_RODRIGUEZ in suggested_personas
        
        # 3. Check cache (miss expected)
        cache_key = cache.generate_key(user_request, suggested_personas[0].value)
        cached_response = await cache.get(cache_key)
        assert cached_response is None
        
        # 4. Execute with Claude (mocked)
        with patch.object(claude_optimizer, '_execute_claude_cli',
                         return_value={'success': True, 'response': 'FastAPI implementation guide...'}):
            
            response = await claude_optimizer.execute_with_persona(
                user_request,
                persona=suggested_personas[0].value
            )
        
        # 5. Record metrics
        metrics_collector.record_response_time(450)
        metrics_collector.record_cache_miss()
        metrics_collector.record_token_usage(500, 0)
        metrics_collector.record_persona_usage(suggested_personas[0].value)
        
        # 6. Cache response
        await cache.set(cache_key, response, ttl=3600)
        
        # 7. Verify second request uses cache
        cached_response = await cache.get(cache_key)
        assert cached_response == response
        
        metrics_collector.record_cache_hit()
        metrics_collector.record_token_usage(0, 500)  # Tokens saved
        
        # 8. Check final metrics
        hit_rate = metrics_collector.get_cache_hit_rate()
        assert hit_rate == 50.0  # 1 hit, 1 miss
        
        token_savings = metrics_collector.get_token_savings_rate()
        assert token_savings == 50.0  # 500 saved out of 1000 total

# ============================================================================
# TEST CONFIGURATION
# ============================================================================

if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=.",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-m", "not benchmark"  # Skip benchmarks in normal run
    ])