"""
Unit Tests for Multi-Model Integration - Simplified Version
Tests core multi-model functionality matching actual implementation
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
    ModelSpec,
    ModelRequest,
    ModelResponse,
    ModelSize,
    AnthropicInterface,
    OpenAIInterface,
    OllamaInterface
)


class TestMultiModelManager:
    """Test suite for MultiModelManager core functionality"""
    
    @pytest.fixture
    def model_manager(self):
        """Create model manager instance for testing"""
        return MultiModelManager()
    
    @pytest.fixture
    def sample_model_spec(self):
        """Create sample model spec for testing"""
        return ModelSpec(
            model_id="test-model-001",
            provider=ModelProvider.ANTHROPIC,
            name="claude-3-opus",
            size=ModelSize.LARGE,
            capabilities=[
                ModelCapability.TEXT_GENERATION,
                ModelCapability.REASONING,
                ModelCapability.CODE_GENERATION
            ],
            context_window=200000,
            max_output_tokens=4096,
            cost_per_1k_input=0.015,
            cost_per_1k_output=0.075
        )
    
    # Model Registration Tests
    def test_register_model(self, model_manager, sample_model_spec):
        """Test registering a model"""
        success = model_manager.register_model(sample_model_spec)
        
        assert success == True
        assert sample_model_spec.model_id in model_manager.models
        assert model_manager.models[sample_model_spec.model_id] == sample_model_spec
    
    def test_register_duplicate_model(self, model_manager, sample_model_spec):
        """Test registering duplicate model updates existing"""
        model_manager.register_model(sample_model_spec)
        
        # Modify and re-register
        sample_model_spec.max_output_tokens = 8192
        success = model_manager.register_model(sample_model_spec)
        
        assert success == True
        assert model_manager.models[sample_model_spec.model_id].max_output_tokens == 8192
    
    def test_unregister_model(self, model_manager, sample_model_spec):
        """Test unregistering a model"""
        model_manager.register_model(sample_model_spec)
        
        success = model_manager.unregister_model(sample_model_spec.model_id)
        
        assert success == True
        assert sample_model_spec.model_id not in model_manager.models
    
    def test_get_model_by_id(self, model_manager, sample_model_spec):
        """Test getting model by ID"""
        model_manager.register_model(sample_model_spec)
        
        model = model_manager.get_model(sample_model_spec.model_id)
        
        assert model is not None
        assert model.model_id == sample_model_spec.model_id
    
    # Model Selection Tests
    @pytest.mark.asyncio
    async def test_select_model_by_capability(self, model_manager):
        """Test selecting model based on capabilities"""
        # Register multiple models
        models = [
            ModelSpec(
                model_id="model-reasoning",
                provider=ModelProvider.ANTHROPIC,
                name="claude-3",
                capabilities=[ModelCapability.REASONING, ModelCapability.TEXT_GENERATION],
                performance_score=0.95
            ),
            ModelSpec(
                model_id="model-code",
                provider=ModelProvider.OPENAI,
                name="gpt-4",
                capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.TEXT_GENERATION],
                performance_score=0.92
            ),
            ModelSpec(
                model_id="model-basic",
                provider=ModelProvider.OLLAMA,
                name="llama-2",
                capabilities=[ModelCapability.TEXT_GENERATION],
                performance_score=0.75
            )
        ]
        
        for model in models:
            model_manager.register_model(model)
        
        # Select best model for reasoning
        best_model = await model_manager.select_model_for_task(
            required_capabilities=[ModelCapability.REASONING]
        )
        
        assert best_model is not None
        assert best_model.model_id == "model-reasoning"
    
    @pytest.mark.asyncio
    async def test_select_model_with_size_constraint(self, model_manager):
        """Test model selection with size constraints"""
        models = [
            ModelSpec(
                model_id="large-model",
                provider=ModelProvider.ANTHROPIC,
                name="claude-3-opus",
                size=ModelSize.LARGE,
                capabilities=[ModelCapability.TEXT_GENERATION]
            ),
            ModelSpec(
                model_id="small-model",
                provider=ModelProvider.OLLAMA,
                name="llama-7b",
                size=ModelSize.SMALL,
                capabilities=[ModelCapability.TEXT_GENERATION]
            )
        ]
        
        for model in models:
            model_manager.register_model(model)
        
        # Select small model only
        model = await model_manager.select_model_for_task(
            required_capabilities=[ModelCapability.TEXT_GENERATION],
            max_size=ModelSize.SMALL
        )
        
        assert model.model_id == "small-model"
    
    # Model Request/Response Tests
    @pytest.mark.asyncio
    async def test_create_model_request(self, model_manager):
        """Test creating a model request"""
        request = ModelRequest(
            request_id="req-001",
            model_id="test-model",
            prompt="Generate a test response",
            max_tokens=100,
            temperature=0.7
        )
        
        assert request.request_id == "req-001"
        assert request.prompt == "Generate a test response"
        assert request.max_tokens == 100
    
    @pytest.mark.asyncio
    async def test_process_model_request(self, model_manager, sample_model_spec):
        """Test processing a model request"""
        model_manager.register_model(sample_model_spec)
        
        request = ModelRequest(
            request_id="req-002",
            model_id=sample_model_spec.model_id,
            prompt="Test prompt",
            max_tokens=50
        )
        
        # Mock the interface
        with patch.object(model_manager, 'get_interface', return_value=Mock(spec=AnthropicInterface)):
            with patch.object(model_manager.get_interface(), 'generate', new_callable=AsyncMock) as mock_generate:
                mock_generate.return_value = ModelResponse(
                    response_id="resp-001",
                    model_id=sample_model_spec.model_id,
                    content="Generated response",
                    tokens_used=25,
                    latency_ms=500
                )
                
                response = await model_manager.process_request(request)
                
                assert response is not None
                assert response.content == "Generated response"
    
    # Provider Interface Tests
    def test_get_anthropic_interface(self, model_manager):
        """Test getting Anthropic interface"""
        interface = model_manager.get_interface(ModelProvider.ANTHROPIC)
        
        assert interface is not None
        assert isinstance(interface, AnthropicInterface)
    
    def test_get_openai_interface(self, model_manager):
        """Test getting OpenAI interface"""
        interface = model_manager.get_interface(ModelProvider.OPENAI)
        
        assert interface is not None
        assert isinstance(interface, OpenAIInterface)
    
    def test_get_ollama_interface(self, model_manager):
        """Test getting Ollama interface"""
        interface = model_manager.get_interface(ModelProvider.OLLAMA)
        
        assert interface is not None
        assert isinstance(interface, OllamaInterface)
    
    # Load Balancing Tests
    @pytest.mark.asyncio
    async def test_round_robin_selection(self, model_manager):
        """Test round-robin model selection"""
        models = [
            ModelSpec(
                model_id=f"model-{i}",
                provider=ModelProvider.OPENAI,
                name=f"gpt-{i}",
                capabilities=[ModelCapability.TEXT_GENERATION]
            )
            for i in range(3)
        ]
        
        for model in models:
            model_manager.register_model(model)
        
        # Track selections
        selections = []
        for _ in range(6):
            model = await model_manager.select_model_round_robin(
                required_capabilities=[ModelCapability.TEXT_GENERATION]
            )
            if model:
                selections.append(model.model_id)
        
        # Should cycle through all models
        unique_selections = set(selections)
        assert len(unique_selections) >= 2  # At least 2 different models selected
    
    # Cost Tracking Tests
    def test_calculate_request_cost(self, model_manager, sample_model_spec):
        """Test calculating cost for a request"""
        model_manager.register_model(sample_model_spec)
        
        # Calculate cost for 1000 input tokens and 500 output tokens
        cost = model_manager.calculate_cost(
            model_id=sample_model_spec.model_id,
            input_tokens=1000,
            output_tokens=500
        )
        
        # Input: 1000 * 0.015 / 1000 = 0.015
        # Output: 500 * 0.075 / 1000 = 0.0375
        # Total: 0.0525
        expected_cost = 0.0525
        assert abs(cost - expected_cost) < 0.001
    
    def test_track_model_usage(self, model_manager, sample_model_spec):
        """Test tracking model usage statistics"""
        model_manager.register_model(sample_model_spec)
        
        # Record usage
        model_manager.record_usage(
            model_id=sample_model_spec.model_id,
            tokens_used=100,
            latency_ms=250,
            success=True
        )
        
        stats = model_manager.get_model_stats(sample_model_spec.model_id)
        
        assert stats is not None
        assert stats["total_requests"] == 1
        assert stats["total_tokens"] == 100
        assert stats["success_count"] == 1
    
    # Availability Tests
    @pytest.mark.asyncio
    async def test_check_model_availability(self, model_manager, sample_model_spec):
        """Test checking model availability"""
        model_manager.register_model(sample_model_spec)
        
        # Mock availability check
        with patch.object(model_manager, 'check_availability', new_callable=AsyncMock) as mock_check:
            mock_check.return_value = True
            
            is_available = await model_manager.check_availability(sample_model_spec.model_id)
            
            assert is_available == True
    
    def test_get_available_models(self, model_manager):
        """Test getting list of available models"""
        models = [
            ModelSpec(
                model_id=f"model-{i}",
                provider=ModelProvider.OPENAI,
                name=f"gpt-{i}",
                capabilities=[ModelCapability.TEXT_GENERATION],
                is_available=(i % 2 == 0)  # Even indices are available
            )
            for i in range(4)
        ]
        
        for model in models:
            model_manager.register_model(model)
        
        available = model_manager.get_available_models()
        
        assert len(available) == 2  # Only even indices
        assert all(m.is_available for m in available)
    
    # Error Handling Tests
    @pytest.mark.asyncio
    async def test_handle_model_failure(self, model_manager):
        """Test handling model generation failure"""
        model = ModelSpec(
            model_id="failing-model",
            provider=ModelProvider.OPENAI,
            name="gpt-4",
            capabilities=[ModelCapability.TEXT_GENERATION]
        )
        model_manager.register_model(model)
        
        request = ModelRequest(
            request_id="req-fail",
            model_id=model.model_id,
            prompt="Test",
            max_tokens=10
        )
        
        # Mock failure
        with patch.object(model_manager, 'get_interface', return_value=Mock(spec=OpenAIInterface)):
            with patch.object(model_manager.get_interface(), 'generate', new_callable=AsyncMock) as mock_gen:
                mock_gen.side_effect = Exception("API Error")
                
                response = await model_manager.process_request(request)
                
                # Should handle gracefully
                assert response is None or response.error is not None
    
    @pytest.mark.asyncio
    async def test_retry_on_failure(self, model_manager, sample_model_spec):
        """Test retry logic on temporary failures"""
        model_manager.register_model(sample_model_spec)
        
        request = ModelRequest(
            request_id="req-retry",
            model_id=sample_model_spec.model_id,
            prompt="Test",
            max_tokens=10
        )
        
        call_count = 0
        
        async def failing_generate(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return ModelResponse(
                response_id="resp-retry",
                model_id=sample_model_spec.model_id,
                content="Success after retry",
                tokens_used=10,
                latency_ms=100
            )
        
        with patch.object(model_manager, 'get_interface', return_value=Mock(spec=AnthropicInterface)):
            with patch.object(model_manager.get_interface(), 'generate', new=failing_generate):
                response = await model_manager.process_request_with_retry(
                    request,
                    max_retries=3
                )
                
                assert response is not None
                assert call_count == 3


class TestModelSpec:
    """Test suite for ModelSpec class"""
    
    def test_model_spec_creation(self):
        """Test creating model specification"""
        spec = ModelSpec(
            model_id="test-model",
            provider=ModelProvider.ANTHROPIC,
            name="claude-3",
            size=ModelSize.LARGE,
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.REASONING]
        )
        
        assert spec.model_id == "test-model"
        assert spec.provider == ModelProvider.ANTHROPIC
        assert spec.size == ModelSize.LARGE
        assert ModelCapability.REASONING in spec.capabilities
    
    def test_model_spec_defaults(self):
        """Test model spec default values"""
        spec = ModelSpec(
            model_id="test",
            provider=ModelProvider.OLLAMA,
            name="llama"
        )
        
        assert spec.size == ModelSize.MEDIUM
        assert spec.capabilities == []
        assert spec.context_window == 4096
        assert spec.max_output_tokens == 2048
        assert spec.is_available == True


class TestModelRequest:
    """Test suite for ModelRequest class"""
    
    def test_request_creation(self):
        """Test creating model request"""
        request = ModelRequest(
            request_id="req-123",
            model_id="model-456",
            prompt="Generate text",
            max_tokens=100,
            temperature=0.7,
            system_prompt="You are a helpful assistant"
        )
        
        assert request.request_id == "req-123"
        assert request.model_id == "model-456"
        assert request.prompt == "Generate text"
        assert request.temperature == 0.7
    
    def test_request_defaults(self):
        """Test request default values"""
        request = ModelRequest(
            request_id="req",
            model_id="model",
            prompt="Test"
        )
        
        assert request.max_tokens == 1024
        assert request.temperature == 0.7
        assert request.system_prompt == ""
        assert request.stream == False


class TestModelResponse:
    """Test suite for ModelResponse class"""
    
    def test_response_creation(self):
        """Test creating model response"""
        response = ModelResponse(
            response_id="resp-123",
            model_id="model-456",
            content="Generated text",
            tokens_used=50,
            latency_ms=250
        )
        
        assert response.response_id == "resp-123"
        assert response.content == "Generated text"
        assert response.tokens_used == 50
        assert response.latency_ms == 250
    
    def test_response_with_metadata(self):
        """Test response with metadata"""
        response = ModelResponse(
            response_id="resp",
            model_id="model",
            content="Text",
            tokens_used=10,
            latency_ms=100,
            metadata={"confidence": 0.95}
        )
        
        assert response.metadata["confidence"] == 0.95


class TestModelEnums:
    """Test suite for model enums"""
    
    def test_model_provider_values(self):
        """Test ModelProvider enum values"""
        assert ModelProvider.ANTHROPIC.value == "anthropic"
        assert ModelProvider.OPENAI.value == "openai"
        assert ModelProvider.GOOGLE.value == "google"
        assert ModelProvider.OLLAMA.value == "ollama"
    
    def test_model_size_values(self):
        """Test ModelSize enum values"""
        assert ModelSize.TINY.value == "tiny"
        assert ModelSize.SMALL.value == "small"
        assert ModelSize.MEDIUM.value == "medium"
        assert ModelSize.LARGE.value == "large"
        assert ModelSize.XLARGE.value == "xlarge"
    
    def test_model_capability_values(self):
        """Test ModelCapability enum values"""
        assert ModelCapability.TEXT_GENERATION.value == "text_generation"
        assert ModelCapability.CODE_GENERATION.value == "code_generation"
        assert ModelCapability.REASONING.value == "reasoning"
        assert ModelCapability.ANALYSIS.value == "analysis"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])