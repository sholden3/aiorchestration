"""
Unit Tests for Multi-Model Integration Manager
Tests model selection, load balancing, and multi-model coordination
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List, Any
import uuid

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from multi_model_integration import (
    MultiModelManager,
    ModelCapability,
    ModelProvider,
    ModelEndpoint,
    ModelPerformanceMetrics,
    ModelSelectionCriteria,
    ModelPoolManager,
    ModelResponse
)


class TestMultiModelManager:
    """Test suite for MultiModelManager"""
    
    @pytest.fixture
    def model_manager(self):
        """Create model manager instance for testing"""
        return MultiModelManager()
    
    @pytest.fixture
    def sample_endpoint(self):
        """Create sample model endpoint for testing"""
        return ModelEndpoint(
            endpoint_id="endpoint_001",
            provider=ModelProvider.OPENAI,
            model_name="gpt-4",
            api_url="https://api.openai.com/v1",
            api_key="test_key",
            capabilities=[
                ModelCapability.TEXT_GENERATION,
                ModelCapability.REASONING
            ],
            max_tokens=4000,
            rate_limit=60,
            cost_per_1k_tokens=0.03
        )
    
    # Model Registration Tests
    def test_register_model_endpoint(self, model_manager, sample_endpoint):
        """Test registering a model endpoint"""
        success = model_manager.register_endpoint(sample_endpoint)
        
        assert success == True
        assert sample_endpoint.endpoint_id in model_manager.endpoints
        assert model_manager.endpoints[sample_endpoint.endpoint_id] == sample_endpoint
    
    def test_register_duplicate_endpoint(self, model_manager, sample_endpoint):
        """Test registering duplicate endpoint updates existing"""
        model_manager.register_endpoint(sample_endpoint)
        
        # Modify and re-register
        sample_endpoint.max_tokens = 8000
        success = model_manager.register_endpoint(sample_endpoint)
        
        assert success == True
        assert model_manager.endpoints[sample_endpoint.endpoint_id].max_tokens == 8000
    
    def test_unregister_endpoint(self, model_manager, sample_endpoint):
        """Test unregistering an endpoint"""
        model_manager.register_endpoint(sample_endpoint)
        
        success = model_manager.unregister_endpoint(sample_endpoint.endpoint_id)
        
        assert success == True
        assert sample_endpoint.endpoint_id not in model_manager.endpoints
    
    # Model Selection Tests
    @pytest.mark.asyncio
    async def test_select_best_model_by_capability(self, model_manager):
        """Test selecting best model based on capabilities"""
        # Register multiple endpoints
        endpoints = [
            ModelEndpoint(
                endpoint_id="gpt4",
                provider=ModelProvider.OPENAI,
                model_name="gpt-4",
                api_url="https://api.openai.com/v1",
                api_key="key1",
                capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.REASONING],
                performance_score=0.95
            ),
            ModelEndpoint(
                endpoint_id="claude",
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-3",
                api_url="https://api.anthropic.com/v1",
                api_key="key2",
                capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CODE_GENERATION],
                performance_score=0.92
            ),
            ModelEndpoint(
                endpoint_id="llama",
                provider=ModelProvider.LOCAL,
                model_name="llama-2",
                api_url="http://localhost:8000",
                api_key="",
                capabilities=[ModelCapability.TEXT_GENERATION],
                performance_score=0.75
            )
        ]
        
        for endpoint in endpoints:
            model_manager.register_endpoint(endpoint)
        
        # Select best model for reasoning
        best_model = await model_manager.select_best_model(
            task_type="reasoning",
            required_capabilities=[ModelCapability.REASONING]
        )
        
        assert best_model is not None
        assert best_model.endpoint_id == "gpt4"
    
    @pytest.mark.asyncio
    async def test_select_model_with_quality_threshold(self, model_manager):
        """Test model selection with quality threshold"""
        endpoints = [
            ModelEndpoint(
                endpoint_id="high_quality",
                provider=ModelProvider.OPENAI,
                model_name="gpt-4",
                capabilities=[ModelCapability.TEXT_GENERATION],
                performance_score=0.95
            ),
            ModelEndpoint(
                endpoint_id="low_quality",
                provider=ModelProvider.LOCAL,
                model_name="small-model",
                capabilities=[ModelCapability.TEXT_GENERATION],
                performance_score=0.60
            )
        ]
        
        for endpoint in endpoints:
            model_manager.register_endpoint(endpoint)
        
        # Select with high quality threshold
        best_model = await model_manager.select_best_model(
            task_type="generation",
            required_capabilities=[ModelCapability.TEXT_GENERATION],
            quality_threshold=0.9
        )
        
        assert best_model.endpoint_id == "high_quality"
    
    @pytest.mark.asyncio
    async def test_select_model_by_cost(self, model_manager):
        """Test selecting model based on cost constraints"""
        endpoints = [
            ModelEndpoint(
                endpoint_id="expensive",
                provider=ModelProvider.OPENAI,
                model_name="gpt-4",
                capabilities=[ModelCapability.TEXT_GENERATION],
                cost_per_1k_tokens=0.06,
                performance_score=0.95
            ),
            ModelEndpoint(
                endpoint_id="cheap",
                provider=ModelProvider.LOCAL,
                model_name="llama",
                capabilities=[ModelCapability.TEXT_GENERATION],
                cost_per_1k_tokens=0.0,
                performance_score=0.80
            )
        ]
        
        for endpoint in endpoints:
            model_manager.register_endpoint(endpoint)
        
        # Select cheapest model
        best_model = await model_manager.select_best_model(
            task_type="generation",
            required_capabilities=[ModelCapability.TEXT_GENERATION],
            optimize_for="cost"
        )
        
        assert best_model.endpoint_id == "cheap"
    
    # Model Availability Tests
    @pytest.mark.asyncio
    async def test_check_model_availability(self, model_manager, sample_endpoint):
        """Test checking model availability"""
        model_manager.register_endpoint(sample_endpoint)
        
        availability = await model_manager.check_model_availability()
        
        assert isinstance(availability, dict)
        assert sample_endpoint.endpoint_id in availability
    
    @pytest.mark.asyncio
    async def test_get_available_models(self, model_manager):
        """Test getting list of available models"""
        endpoints = [
            ModelEndpoint(
                endpoint_id=f"model_{i}",
                provider=ModelProvider.OPENAI,
                model_name=f"model-{i}",
                is_available=i % 2 == 0  # Even indices are available
            )
            for i in range(4)
        ]
        
        for endpoint in endpoints:
            model_manager.register_endpoint(endpoint)
        
        available = model_manager.get_available_models()
        
        assert len(available) == 2  # Only even indices
        assert all(m.is_available for m in available)
    
    # Load Balancing Tests
    @pytest.mark.asyncio
    async def test_load_balancing_round_robin(self, model_manager):
        """Test round-robin load balancing"""
        endpoints = [
            ModelEndpoint(
                endpoint_id=f"model_{i}",
                provider=ModelProvider.OPENAI,
                model_name=f"model-{i}",
                capabilities=[ModelCapability.TEXT_GENERATION]
            )
            for i in range(3)
        ]
        
        for endpoint in endpoints:
            model_manager.register_endpoint(endpoint)
        
        # Get models multiple times
        selections = []
        for _ in range(6):
            model = await model_manager.select_model_with_load_balancing(
                required_capabilities=[ModelCapability.TEXT_GENERATION]
            )
            selections.append(model.endpoint_id)
        
        # Should cycle through all models
        assert "model_0" in selections
        assert "model_1" in selections
        assert "model_2" in selections
    
    @pytest.mark.asyncio
    async def test_load_balancing_least_loaded(self, model_manager):
        """Test least-loaded balancing strategy"""
        endpoints = [
            ModelEndpoint(
                endpoint_id=f"model_{i}",
                provider=ModelProvider.OPENAI,
                model_name=f"model-{i}",
                capabilities=[ModelCapability.TEXT_GENERATION],
                current_load=i * 10  # Different load levels
            )
            for i in range(3)
        ]
        
        for endpoint in endpoints:
            model_manager.register_endpoint(endpoint)
        
        # Should select least loaded
        model = await model_manager.select_model_with_load_balancing(
            required_capabilities=[ModelCapability.TEXT_GENERATION],
            strategy="least_loaded"
        )
        
        assert model.endpoint_id == "model_0"  # Has load of 0
    
    # Multi-Model Execution Tests
    @pytest.mark.asyncio
    async def test_execute_with_multiple_models(self, model_manager):
        """Test executing task with multiple models"""
        endpoints = [
            ModelEndpoint(
                endpoint_id=f"model_{i}",
                provider=ModelProvider.OPENAI,
                model_name=f"model-{i}",
                capabilities=[ModelCapability.TEXT_GENERATION]
            )
            for i in range(2)
        ]
        
        for endpoint in endpoints:
            model_manager.register_endpoint(endpoint)
        
        # Mock execution
        with patch.object(model_manager, '_execute_on_model', new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = ModelResponse(
                model_id="model_0",
                content="Test response",
                tokens_used=100,
                latency=0.5
            )
            
            results = await model_manager.execute_multi_model(
                prompt="Test prompt",
                model_count=2,
                strategy="parallel"
            )
            
            assert len(results) <= 2
            assert mock_exec.called
    
    @pytest.mark.asyncio
    async def test_ensemble_execution(self, model_manager):
        """Test ensemble execution with voting"""
        endpoints = [
            ModelEndpoint(
                endpoint_id=f"model_{i}",
                provider=ModelProvider.OPENAI,
                model_name=f"model-{i}",
                capabilities=[ModelCapability.TEXT_GENERATION]
            )
            for i in range(3)
        ]
        
        for endpoint in endpoints:
            model_manager.register_endpoint(endpoint)
        
        # Mock responses
        responses = [
            ModelResponse("model_0", "Answer A", 100, 0.5),
            ModelResponse("model_1", "Answer A", 100, 0.6),
            ModelResponse("model_2", "Answer B", 100, 0.4)
        ]
        
        with patch.object(model_manager, '_execute_on_model', new_callable=AsyncMock) as mock_exec:
            mock_exec.side_effect = responses
            
            result = await model_manager.execute_ensemble(
                prompt="Test prompt",
                models=endpoints,
                aggregation="majority_vote"
            )
            
            assert result is not None
            # Majority should win (Answer A appears twice)
    
    # Performance Tracking Tests
    def test_track_model_performance(self, model_manager, sample_endpoint):
        """Test tracking model performance metrics"""
        model_manager.register_endpoint(sample_endpoint)
        
        # Record performance
        model_manager.record_performance(
            endpoint_id=sample_endpoint.endpoint_id,
            latency=0.5,
            tokens_used=150,
            success=True
        )
        
        metrics = model_manager.get_model_metrics(sample_endpoint.endpoint_id)
        
        assert metrics is not None
        assert metrics["total_requests"] == 1
        assert metrics["success_count"] == 1
        assert metrics["average_latency"] == 0.5
    
    def test_calculate_success_rate(self, model_manager, sample_endpoint):
        """Test calculating model success rate"""
        model_manager.register_endpoint(sample_endpoint)
        
        # Record mixed results
        for i in range(10):
            model_manager.record_performance(
                endpoint_id=sample_endpoint.endpoint_id,
                latency=0.5,
                tokens_used=100,
                success=(i < 8)  # 80% success rate
            )
        
        metrics = model_manager.get_model_metrics(sample_endpoint.endpoint_id)
        
        assert metrics["success_rate"] == 0.8
    
    # Fallback and Retry Tests
    @pytest.mark.asyncio
    async def test_fallback_on_failure(self, model_manager):
        """Test fallback to secondary model on failure"""
        primary = ModelEndpoint(
            endpoint_id="primary",
            provider=ModelProvider.OPENAI,
            model_name="gpt-4",
            capabilities=[ModelCapability.TEXT_GENERATION],
            is_available=False  # Not available
        )
        
        fallback = ModelEndpoint(
            endpoint_id="fallback",
            provider=ModelProvider.LOCAL,
            model_name="llama",
            capabilities=[ModelCapability.TEXT_GENERATION],
            is_available=True
        )
        
        model_manager.register_endpoint(primary)
        model_manager.register_endpoint(fallback)
        
        # Should use fallback
        model = await model_manager.select_best_model(
            task_type="generation",
            required_capabilities=[ModelCapability.TEXT_GENERATION]
        )
        
        assert model.endpoint_id == "fallback"
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff(self, model_manager, sample_endpoint):
        """Test retry logic with exponential backoff"""
        model_manager.register_endpoint(sample_endpoint)
        
        call_count = 0
        
        async def failing_execute(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return ModelResponse("test", "Success", 100, 0.5)
        
        with patch.object(model_manager, '_execute_on_model', new=failing_execute):
            result = await model_manager.execute_with_retry(
                endpoint_id=sample_endpoint.endpoint_id,
                prompt="Test",
                max_retries=3
            )
            
            assert result is not None
            assert call_count == 3
    
    # Cost Optimization Tests
    def test_calculate_request_cost(self, model_manager, sample_endpoint):
        """Test calculating cost for a request"""
        model_manager.register_endpoint(sample_endpoint)
        
        cost = model_manager.calculate_cost(
            endpoint_id=sample_endpoint.endpoint_id,
            tokens=2000
        )
        
        # 2000 tokens at 0.03 per 1k = 0.06
        assert cost == 0.06
    
    def test_get_cost_effective_model(self, model_manager):
        """Test getting most cost-effective model"""
        endpoints = [
            ModelEndpoint(
                endpoint_id="expensive",
                provider=ModelProvider.OPENAI,
                model_name="gpt-4",
                capabilities=[ModelCapability.TEXT_GENERATION],
                cost_per_1k_tokens=0.06,
                performance_score=0.95
            ),
            ModelEndpoint(
                endpoint_id="balanced",
                provider=ModelProvider.ANTHROPIC,
                model_name="claude",
                capabilities=[ModelCapability.TEXT_GENERATION],
                cost_per_1k_tokens=0.03,
                performance_score=0.90
            ),
            ModelEndpoint(
                endpoint_id="cheap",
                provider=ModelProvider.LOCAL,
                model_name="llama",
                capabilities=[ModelCapability.TEXT_GENERATION],
                cost_per_1k_tokens=0.0,
                performance_score=0.75
            )
        ]
        
        for endpoint in endpoints:
            model_manager.register_endpoint(endpoint)
        
        # Get best value (performance per dollar)
        best_value = model_manager.get_best_value_model(
            required_capabilities=[ModelCapability.TEXT_GENERATION],
            min_performance=0.8
        )
        
        # Should select balanced option
        assert best_value.endpoint_id == "balanced"


class TestModelEndpoint:
    """Test suite for ModelEndpoint class"""
    
    def test_endpoint_creation(self):
        """Test creating model endpoint"""
        endpoint = ModelEndpoint(
            endpoint_id="test_endpoint",
            provider=ModelProvider.OPENAI,
            model_name="gpt-4",
            api_url="https://api.openai.com/v1",
            api_key="test_key",
            capabilities=[ModelCapability.TEXT_GENERATION],
            max_tokens=4000
        )
        
        assert endpoint.endpoint_id == "test_endpoint"
        assert endpoint.provider == ModelProvider.OPENAI
        assert endpoint.model_name == "gpt-4"
        assert ModelCapability.TEXT_GENERATION in endpoint.capabilities
    
    def test_endpoint_defaults(self):
        """Test endpoint default values"""
        endpoint = ModelEndpoint(
            endpoint_id="test",
            provider=ModelProvider.LOCAL,
            model_name="test_model"
        )
        
        assert endpoint.api_url == ""
        assert endpoint.api_key == ""
        assert endpoint.capabilities == []
        assert endpoint.max_tokens == 2048
        assert endpoint.is_available == True
        assert endpoint.performance_score == 1.0
    
    def test_endpoint_rate_limiting(self):
        """Test endpoint rate limit settings"""
        endpoint = ModelEndpoint(
            endpoint_id="test",
            provider=ModelProvider.OPENAI,
            model_name="gpt-4",
            rate_limit=60,
            rate_window=60
        )
        
        assert endpoint.rate_limit == 60
        assert endpoint.rate_window == 60


class TestModelCapability:
    """Test suite for ModelCapability enum"""
    
    def test_capability_values(self):
        """Test ModelCapability enum values"""
        assert ModelCapability.TEXT_GENERATION.value == "text_generation"
        assert ModelCapability.CODE_GENERATION.value == "code_generation"
        assert ModelCapability.IMAGE_GENERATION.value == "image_generation"
        assert ModelCapability.REASONING.value == "reasoning"
        assert ModelCapability.ANALYSIS.value == "analysis"
        assert ModelCapability.TRANSLATION.value == "translation"
        assert ModelCapability.SUMMARIZATION.value == "summarization"


class TestModelProvider:
    """Test suite for ModelProvider enum"""
    
    def test_provider_values(self):
        """Test ModelProvider enum values"""
        assert ModelProvider.OPENAI.value == "openai"
        assert ModelProvider.ANTHROPIC.value == "anthropic"
        assert ModelProvider.GOOGLE.value == "google"
        assert ModelProvider.LOCAL.value == "local"
        assert ModelProvider.HUGGINGFACE.value == "huggingface"
        assert ModelProvider.CUSTOM.value == "custom"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])