#!/usr/bin/env python3
"""
Multi-Model AI Integration v8.2
Unified interface for multiple AI models and providers
Supports Claude, GPT, local models, and specialized tools
"""

import asyncio
import json
import time
import aiohttp
import logging
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Protocol
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import hashlib
import base64
from urllib.parse import urljoin
import subprocess
import os
import requests

# Import our orchestration components
from ai_orchestration_engine import AgentType, AgentCapability, AIAgent, AgentStatus


class ModelProvider(Enum):
    """AI model providers"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    LOCAL_OLLAMA = "local_ollama"
    HUGGINGFACE = "huggingface"
    GOOGLE = "google"
    CUSTOM = "custom"


class ModelSize(Enum):
    """Model size categories"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "xl"


class ModelCapability(Enum):
    """AI model capabilities"""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    ANALYSIS = "analysis"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CLASSIFICATION = "classification"
    EMBEDDINGS = "embeddings"
    IMAGE_ANALYSIS = "image_analysis"
    FUNCTION_CALLING = "function_calling"
    IMAGE_GENERATION = "image_generation"
    EMBEDDING = "embedding"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    QUESTION_ANSWERING = "question_answering"


@dataclass
class ModelEndpoint:
    """Represents a model API endpoint"""
    url: str
    api_key: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    max_retries: int = 3
    rate_limit: Optional[int] = None  # requests per minute


@dataclass
class ModelPerformanceMetrics:
    """Metrics tracking model performance"""
    model_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens_used: int = 0
    total_cost: float = 0.0
    average_response_time: float = 0.0
    last_used: Optional[datetime] = None
    error_rate: float = 0.0
    success_rate: float = 0.0


@dataclass
class ModelSelectionCriteria:
    """Criteria for selecting the best model for a task"""
    required_capabilities: List[ModelCapability] = field(default_factory=list)
    preferred_provider: Optional[ModelProvider] = None
    max_cost_per_token: Optional[float] = None
    min_quality_score: float = 0.7
    max_response_time: Optional[float] = None
    context_window_required: int = 0
    prefer_local: bool = False


@dataclass
class ModelResponse:
    """Response from a model"""
    model_id: str
    content: str
    tokens_used: int
    cost: float
    response_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class ModelPoolManager:
    """Manages pools of models for load balancing"""
    def __init__(self):
        self.model_pools: Dict[str, List[str]] = defaultdict(list)
        self.pool_weights: Dict[str, float] = {}
        
    def add_to_pool(self, pool_name: str, model_id: str, weight: float = 1.0):
        """Add a model to a pool"""
        self.model_pools[pool_name].append(model_id)
        self.pool_weights[f"{pool_name}:{model_id}"] = weight
    
    def get_pool_models(self, pool_name: str) -> List[str]:
        """Get all models in a pool"""
        return self.model_pools.get(pool_name, [])
    
    def select_from_pool(self, pool_name: str) -> Optional[str]:
        """Select a model from a pool based on weights"""
        models = self.get_pool_models(pool_name)
        if not models:
            return None
        # Simple selection - in real implementation would use weighted random
        return models[0]


@dataclass
class ModelSpec:
    """Specification for an AI model"""
    model_id: str
    provider: ModelProvider
    name: str
    version: str
    size: ModelSize
    capabilities: List[ModelCapability]
    context_window: int
    max_tokens: int
    cost_per_input_token: float
    cost_per_output_token: float
    speed_rating: float  # tokens per second
    quality_rating: float  # 0-1 quality score
    api_endpoint: Optional[str] = None
    api_key_required: bool = True
    supports_streaming: bool = False
    supports_function_calling: bool = False
    specialty_domains: List[str] = field(default_factory=list)


@dataclass
class ModelRequest:
    """Request to an AI model"""
    request_id: str
    model_spec: ModelSpec
    prompt: str
    system_prompt: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_p: float = 0.9
    stop_sequences: List[str] = field(default_factory=list)
    function_definitions: List[Dict[str, Any]] = field(default_factory=list)
    images: List[str] = field(default_factory=list)  # Base64 encoded images
    metadata: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 300
    streaming: bool = False


@dataclass
class ModelResponse:
    """Response from an AI model"""
    request_id: str
    model_spec: ModelSpec
    content: str
    finish_reason: str
    usage: Dict[str, int]
    response_time: float
    cost: float
    quality_score: float = 0.0
    confidence_score: float = 0.0
    function_calls: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class ModelInterface(ABC):
    """Abstract interface for AI model implementations"""
    
    @abstractmethod
    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate response from model"""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if model is available"""
        pass
    
    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for texts (if supported)"""
        pass


class AnthropicInterface(ModelInterface):
    """Interface for Anthropic Claude models"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Anthropic interface"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = "https://api.anthropic.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session:
            headers = {
                "anthropic-version": "2023-06-01",
                "x-api-key": self.api_key,
                "content-type": "application/json"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate response using Claude"""
        start_time = time.time()
        
        try:
            session = await self._get_session()
            
            # Prepare messages
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            
            # Handle images if present
            content = request.prompt
            if request.images:
                content = [
                    {"type": "text", "text": request.prompt}
                ]
                for image_b64 in request.images:
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_b64
                        }
                    })
            
            messages.append({"role": "user", "content": content})
            
            # Prepare request payload
            payload = {
                "model": request.model_spec.model_id,
                "messages": messages,
                "max_tokens": request.max_tokens or request.model_spec.max_tokens,
                "temperature": request.temperature,
                "top_p": request.top_p
            }
            
            if request.stop_sequences:
                payload["stop_sequences"] = request.stop_sequences
            
            # Make request
            async with session.post(f"{self.base_url}/messages", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract response
                    content_text = ""
                    if data.get("content"):
                        for content_block in data["content"]:
                            if content_block.get("type") == "text":
                                content_text += content_block.get("text", "")
                    
                    # Calculate usage and cost
                    usage = data.get("usage", {})
                    input_tokens = usage.get("input_tokens", 0)
                    output_tokens = usage.get("output_tokens", 0)
                    
                    cost = (
                        input_tokens * request.model_spec.cost_per_input_token +
                        output_tokens * request.model_spec.cost_per_output_token
                    )
                    
                    response_time = time.time() - start_time
                    
                    return ModelResponse(
                        request_id=request.request_id,
                        model_spec=request.model_spec,
                        content=content_text,
                        finish_reason=data.get("stop_reason", "unknown"),
                        usage={"input_tokens": input_tokens, "output_tokens": output_tokens},
                        response_time=response_time,
                        cost=cost,
                        quality_score=request.model_spec.quality_rating,
                        confidence_score=0.9  # Claude typically high confidence
                    )
                else:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API error {response.status}: {error_text}")
        
        except Exception as e:
            return ModelResponse(
                request_id=request.request_id,
                model_spec=request.model_spec,
                content="",
                finish_reason="error",
                usage={},
                response_time=time.time() - start_time,
                cost=0.0,
                error=str(e)
            )
    
    async def is_available(self) -> bool:
        """Check if Anthropic API is available"""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/messages", 
                                 headers={"anthropic-version": "2023-06-01"}) as response:
                return response.status in [200, 400, 401]  # Any valid response means API is up
        except:
            return False
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Anthropic doesn't provide embeddings API"""
        raise NotImplementedError("Anthropic doesn't support embeddings")


class OpenAIInterface(ModelInterface):
    """Interface for OpenAI GPT models"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI interface"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate response using GPT"""
        start_time = time.time()
        
        try:
            session = await self._get_session()
            
            # Prepare messages
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            
            # Handle images if present (GPT-4 Vision)
            content = request.prompt
            if request.images and "vision" in request.model_spec.model_id.lower():
                content = [
                    {"type": "text", "text": request.prompt}
                ]
                for image_b64 in request.images:
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
                        }
                    })
            
            messages.append({"role": "user", "content": content})
            
            # Prepare request payload
            payload = {
                "model": request.model_spec.model_id,
                "messages": messages,
                "max_tokens": request.max_tokens or min(request.model_spec.max_tokens, 4096),
                "temperature": request.temperature,
                "top_p": request.top_p
            }
            
            if request.stop_sequences:
                payload["stop"] = request.stop_sequences
            
            if request.function_definitions:
                payload["functions"] = request.function_definitions
                payload["function_call"] = "auto"
            
            # Make request
            async with session.post(f"{self.base_url}/chat/completions", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract response
                    choice = data["choices"][0]
                    message = choice["message"]
                    content_text = message.get("content", "")
                    
                    # Handle function calls
                    function_calls = []
                    if "function_call" in message:
                        function_calls.append(message["function_call"])
                    
                    # Calculate usage and cost
                    usage = data.get("usage", {})
                    prompt_tokens = usage.get("prompt_tokens", 0)
                    completion_tokens = usage.get("completion_tokens", 0)
                    
                    cost = (
                        prompt_tokens * request.model_spec.cost_per_input_token +
                        completion_tokens * request.model_spec.cost_per_output_token
                    )
                    
                    response_time = time.time() - start_time
                    
                    return ModelResponse(
                        request_id=request.request_id,
                        model_spec=request.model_spec,
                        content=content_text,
                        finish_reason=choice.get("finish_reason", "unknown"),
                        usage={"input_tokens": prompt_tokens, "output_tokens": completion_tokens},
                        response_time=response_time,
                        cost=cost,
                        quality_score=request.model_spec.quality_rating,
                        confidence_score=0.85,
                        function_calls=function_calls
                    )
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error {response.status}: {error_text}")
        
        except Exception as e:
            return ModelResponse(
                request_id=request.request_id,
                model_spec=request.model_spec,
                content="",
                finish_reason="error",
                usage={},
                response_time=time.time() - start_time,
                cost=0.0,
                error=str(e)
            )
    
    async def is_available(self) -> bool:
        """Check if OpenAI API is available"""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/models") as response:
                return response.status == 200
        except:
            return False
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings using OpenAI"""
        try:
            session = await self._get_session()
            payload = {
                "model": "text-embedding-ada-002",
                "input": texts
            }
            
            async with session.post(f"{self.base_url}/embeddings", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return [item["embedding"] for item in data["data"]]
                else:
                    raise Exception(f"OpenAI embeddings error: {response.status}")
        except Exception as e:
            logging.error(f"Failed to get OpenAI embeddings: {e}")
            return []


class OllamaInterface(ModelInterface):
    """Interface for local Ollama models"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize Ollama interface"""
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate response using Ollama"""
        start_time = time.time()
        
        try:
            session = await self._get_session()
            
            # Prepare prompt (Ollama uses simple prompt format)
            full_prompt = request.prompt
            if request.system_prompt:
                full_prompt = f"System: {request.system_prompt}\n\nUser: {request.prompt}"
            
            payload = {
                "model": request.model_spec.model_id,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": request.temperature,
                    "top_p": request.top_p,
                    "num_predict": request.max_tokens or request.model_spec.max_tokens
                }
            }
            
            if request.stop_sequences:
                payload["options"]["stop"] = request.stop_sequences
            
            # Make request
            async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    content_text = data.get("response", "")
                    
                    # Estimate tokens (Ollama doesn't always provide exact counts)
                    estimated_input_tokens = len(full_prompt.split()) * 1.3  # Rough estimate
                    estimated_output_tokens = len(content_text.split()) * 1.3
                    
                    # Local models have no cost
                    cost = 0.0
                    
                    response_time = time.time() - start_time
                    
                    return ModelResponse(
                        request_id=request.request_id,
                        model_spec=request.model_spec,
                        content=content_text,
                        finish_reason=data.get("done_reason", "stop"),
                        usage={
                            "input_tokens": int(estimated_input_tokens),
                            "output_tokens": int(estimated_output_tokens)
                        },
                        response_time=response_time,
                        cost=cost,
                        quality_score=request.model_spec.quality_rating,
                        confidence_score=0.7  # Local models typically lower confidence
                    )
                else:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error {response.status}: {error_text}")
        
        except Exception as e:
            return ModelResponse(
                request_id=request.request_id,
                model_spec=request.model_spec,
                content="",
                finish_reason="error",
                usage={},
                response_time=time.time() - start_time,
                cost=0.0,
                error=str(e)
            )
    
    async def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/tags") as response:
                return response.status == 200
        except:
            return False
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings using Ollama (if model supports it)"""
        try:
            session = await self._get_session()
            embeddings = []
            
            for text in texts:
                payload = {
                    "model": "nomic-embed-text",  # Default embedding model
                    "prompt": text
                }
                
                async with session.post(f"{self.base_url}/api/embeddings", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        embeddings.append(data.get("embedding", []))
                    else:
                        embeddings.append([])
            
            return embeddings
        except Exception as e:
            logging.error(f"Failed to get Ollama embeddings: {e}")
            return []


class MultiModelManager:
    """Manager for multiple AI models and providers"""
    
    def __init__(self):
        """Initialize multi-model manager"""
        self.model_specs: Dict[str, ModelSpec] = {}
        self.model_interfaces: Dict[ModelProvider, ModelInterface] = {}
        self.available_models: Set[str] = set()
        
        # Performance tracking
        self.model_metrics: Dict[str, Dict[str, Any]] = {}
        self.load_balancing_weights: Dict[str, float] = {}
        
        # Configuration
        self.cost_threshold_per_hour = 100.0
        self.performance_threshold = 5.0  # seconds
        
        self._initialize_models()
        self._initialize_interfaces()
    
    def _initialize_models(self):
        """Initialize available model specifications"""
        
        # For testing: assume models are available if no API keys present
        test_mode = not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY"))
        
        # Claude models
        claude_sonnet = ModelSpec(
            model_id="claude-3-sonnet-20240229",
            provider=ModelProvider.ANTHROPIC,
            name="Claude 3 Sonnet",
            version="3.0",
            size=ModelSize.LARGE,
            capabilities=[
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CODE_GENERATION,
                ModelCapability.REASONING,
                ModelCapability.ANALYSIS,
                ModelCapability.IMAGE_ANALYSIS
            ],
            context_window=200000,
            max_tokens=4096,
            cost_per_input_token=0.003,
            cost_per_output_token=0.015,
            speed_rating=2000.0,
            quality_rating=0.95,
            supports_streaming=True,
            specialty_domains=["coding", "analysis", "reasoning"]
        )
        
        claude_haiku = ModelSpec(
            model_id="claude-3-haiku-20240307",
            provider=ModelProvider.ANTHROPIC,
            name="Claude 3 Haiku",
            version="3.0",
            size=ModelSize.MEDIUM,
            capabilities=[
                ModelCapability.TEXT_GENERATION,
                ModelCapability.SUMMARIZATION,
                ModelCapability.CLASSIFICATION
            ],
            context_window=200000,
            max_tokens=4096,
            cost_per_input_token=0.00025,
            cost_per_output_token=0.00125,
            speed_rating=5000.0,
            quality_rating=0.85,
            supports_streaming=True,
            specialty_domains=["summarization", "quick_tasks"]
        )
        
        # GPT models
        gpt4_turbo = ModelSpec(
            model_id="gpt-4-turbo-preview",
            provider=ModelProvider.OPENAI,
            name="GPT-4 Turbo",
            version="4.0",
            size=ModelSize.LARGE,
            capabilities=[
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CODE_GENERATION,
                ModelCapability.REASONING,
                ModelCapability.FUNCTION_CALLING
            ],
            context_window=128000,
            max_tokens=4096,
            cost_per_input_token=0.01,
            cost_per_output_token=0.03,
            speed_rating=1500.0,
            quality_rating=0.93,
            supports_streaming=True,
            supports_function_calling=True,
            specialty_domains=["reasoning", "complex_tasks"]
        )
        
        gpt35_turbo = ModelSpec(
            model_id="gpt-3.5-turbo",
            provider=ModelProvider.OPENAI,
            name="GPT-3.5 Turbo",
            version="3.5",
            size=ModelSize.MEDIUM,
            capabilities=[
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CODE_GENERATION,
                ModelCapability.FUNCTION_CALLING
            ],
            context_window=16385,
            max_tokens=4096,
            cost_per_input_token=0.0005,
            cost_per_output_token=0.0015,
            speed_rating=3000.0,
            quality_rating=0.80,
            supports_streaming=True,
            supports_function_calling=True,
            specialty_domains=["general_tasks", "cost_efficient"]
        )
        
        # Local models (Ollama)
        llama2_local = ModelSpec(
            model_id="llama2:13b",
            provider=ModelProvider.LOCAL_OLLAMA,
            name="Llama 2 13B",
            version="2.0",
            size=ModelSize.LARGE,
            capabilities=[
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CODE_GENERATION
            ],
            context_window=4096,
            max_tokens=2048,
            cost_per_input_token=0.0,  # Local, no cost
            cost_per_output_token=0.0,
            speed_rating=500.0,  # Slower on local hardware
            quality_rating=0.75,
            api_key_required=False,
            specialty_domains=["privacy", "local_processing"]
        )
        
        # Register models
        models = [claude_sonnet, claude_haiku, gpt4_turbo, gpt35_turbo, llama2_local]
        for model in models:
            self.model_specs[model.model_id] = model
            self.load_balancing_weights[model.model_id] = 1.0
            # In test mode, mark models as available
            if test_mode:
                self.available_models.add(model.model_id)
    
    def _initialize_interfaces(self):
        """Initialize model interfaces"""
        self.model_interfaces[ModelProvider.ANTHROPIC] = AnthropicInterface()
        self.model_interfaces[ModelProvider.OPENAI] = OpenAIInterface()
        self.model_interfaces[ModelProvider.LOCAL_OLLAMA] = OllamaInterface()
    
    async def check_model_availability(self) -> Dict[str, bool]:
        """Check availability of all models"""
        availability = {}
        
        for model_id, model_spec in self.model_specs.items():
            interface = self.model_interfaces.get(model_spec.provider)
            if interface:
                try:
                    is_available = await interface.is_available()
                    availability[model_id] = is_available
                    
                    if is_available:
                        self.available_models.add(model_id)
                    else:
                        self.available_models.discard(model_id)
                except:
                    availability[model_id] = False
                    self.available_models.discard(model_id)
            else:
                availability[model_id] = False
        
        return availability
    
    async def select_best_model(
        self,
        task_type: str,
        required_capabilities: List[ModelCapability],
        max_cost: Optional[float] = None,
        max_response_time: Optional[float] = None,
        quality_threshold: float = 0.7,
        preferred_provider: Optional[ModelProvider] = None
    ) -> Optional[str]:
        """Select the best model for a given task"""
        
        # Filter available models by requirements
        candidate_models = []
        
        for model_id in self.available_models:
            model_spec = self.model_specs[model_id]
            
            # Check capabilities
            if not all(cap in model_spec.capabilities for cap in required_capabilities):
                continue
            
            # Check quality threshold
            if model_spec.quality_rating < quality_threshold:
                continue
            
            # Check provider preference
            if preferred_provider and model_spec.provider != preferred_provider:
                continue
            
            # Check cost constraints
            if max_cost:
                estimated_cost = self._estimate_task_cost(model_spec, task_type)
                if estimated_cost > max_cost:
                    continue
            
            # Check performance constraints
            if max_response_time:
                estimated_time = self._estimate_response_time(model_spec, task_type)
                if estimated_time > max_response_time:
                    continue
            
            candidate_models.append(model_id)
        
        if not candidate_models:
            return None
        
        # Score and rank candidates
        scored_models = []
        for model_id in candidate_models:
            score = self._calculate_model_score(model_id, task_type, required_capabilities)
            scored_models.append((score, model_id))
        
        # Sort by score (higher is better)
        scored_models.sort(reverse=True)
        
        return scored_models[0][1] if scored_models else None
    
    def _calculate_model_score(
        self,
        model_id: str,
        task_type: str,
        required_capabilities: List[ModelCapability]
    ) -> float:
        """Calculate suitability score for a model"""
        model_spec = self.model_specs[model_id]
        score = 0.0
        
        # Base quality score (40% weight)
        score += model_spec.quality_rating * 40
        
        # Speed score (20% weight)
        speed_score = min(20, model_spec.speed_rating / 1000)
        score += speed_score
        
        # Cost efficiency (15% weight)
        cost_score = max(0, 15 - (model_spec.cost_per_output_token * 1000))
        score += cost_score
        
        # Capability match (15% weight)
        capability_score = len(set(required_capabilities) & set(model_spec.capabilities))
        score += capability_score * 3
        
        # Load balancing weight (10% weight)
        load_weight = self.load_balancing_weights.get(model_id, 1.0)
        score += load_weight * 10
        
        return score
    
    def _estimate_task_cost(self, model_spec: ModelSpec, task_type: str) -> float:
        """Estimate cost for a task"""
        # Simple estimation based on task type
        token_estimates = {
            "simple": 1000,
            "medium": 3000,
            "complex": 8000,
            "analysis": 5000,
            "generation": 4000
        }
        
        estimated_tokens = token_estimates.get(task_type, 3000)
        input_tokens = estimated_tokens * 0.7
        output_tokens = estimated_tokens * 0.3
        
        return (
            input_tokens * model_spec.cost_per_input_token +
            output_tokens * model_spec.cost_per_output_token
        )
    
    def _estimate_response_time(self, model_spec: ModelSpec, task_type: str) -> float:
        """Estimate response time for a task"""
        # Base time from speed rating
        base_time = 2000 / model_spec.speed_rating  # Assume 2000 tokens
        
        # Adjust for task complexity
        complexity_multipliers = {
            "simple": 0.5,
            "medium": 1.0,
            "complex": 2.0,
            "analysis": 1.5,
            "generation": 1.2
        }
        
        multiplier = complexity_multipliers.get(task_type, 1.0)
        return base_time * multiplier
    
    async def generate_response(
        self,
        prompt: str,
        task_type: str = "general",
        required_capabilities: Optional[List[ModelCapability]] = None,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        preferred_model: Optional[str] = None,
        fallback_models: Optional[List[str]] = None,
        **kwargs
    ) -> ModelResponse:
        """Generate response using the best available model"""
        
        required_capabilities = required_capabilities or [ModelCapability.TEXT_GENERATION]
        
        # Select model
        if preferred_model and preferred_model in self.available_models:
            selected_model = preferred_model
        else:
            selected_model = await self.select_best_model(
                task_type=task_type,
                required_capabilities=required_capabilities,
                max_cost=kwargs.get("max_cost"),
                max_response_time=kwargs.get("max_response_time"),
                quality_threshold=kwargs.get("quality_threshold", 0.7)
            )
        
        if not selected_model:
            # Try fallback models
            if fallback_models:
                for fallback_model in fallback_models:
                    if fallback_model in self.available_models:
                        selected_model = fallback_model
                        break
        
        if not selected_model:
            raise Exception("No suitable model available for the task")
        
        # Create request
        model_spec = self.model_specs[selected_model]
        request = ModelRequest(
            request_id=f"req_{int(time.time() * 1000)}",
            model_spec=model_spec,
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            **{k: v for k, v in kwargs.items() if k in ['top_p', 'stop_sequences', 'images']}
        )
        
        # Get interface and generate
        interface = self.model_interfaces[model_spec.provider]
        response = await interface.generate(request)
        
        # Update metrics and load balancing
        await self._update_model_metrics(selected_model, response)
        
        return response
    
    async def _update_model_metrics(self, model_id: str, response: ModelResponse):
        """Update model performance metrics"""
        if model_id not in self.model_metrics:
            self.model_metrics[model_id] = {
                "total_requests": 0,
                "successful_requests": 0,
                "total_cost": 0.0,
                "total_response_time": 0.0,
                "average_quality": 0.0,
                "last_updated": datetime.now()
            }
        
        metrics = self.model_metrics[model_id]
        metrics["total_requests"] += 1
        
        if not response.error:
            metrics["successful_requests"] += 1
            metrics["total_cost"] += response.cost
            metrics["total_response_time"] += response.response_time
            
            # Update running average quality
            if response.quality_score > 0:
                current_avg = metrics.get("average_quality", 0)
                metrics["average_quality"] = (
                    (current_avg * (metrics["successful_requests"] - 1) + response.quality_score) /
                    metrics["successful_requests"]
                )
        
        # Update load balancing weights based on performance
        success_rate = metrics["successful_requests"] / metrics["total_requests"]
        avg_response_time = (
            metrics["total_response_time"] / metrics["successful_requests"]
            if metrics["successful_requests"] > 0 else 10.0
        )
        
        # Weight based on success rate and response time
        performance_weight = success_rate * (5.0 / max(avg_response_time, 1.0))
        self.load_balancing_weights[model_id] = max(0.1, performance_weight)
        
        metrics["last_updated"] = datetime.now()
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models"""
        availability = await self.check_model_availability()
        
        status = {
            "total_models": len(self.model_specs),
            "available_models": len(self.available_models),
            "providers": {},
            "models": {}
        }
        
        # Provider summary
        provider_stats = {}
        for model_spec in self.model_specs.values():
            provider = model_spec.provider.value
            if provider not in provider_stats:
                provider_stats[provider] = {"total": 0, "available": 0}
            
            provider_stats[provider]["total"] += 1
            if model_spec.model_id in self.available_models:
                provider_stats[provider]["available"] += 1
        
        status["providers"] = provider_stats
        
        # Model details
        for model_id, model_spec in self.model_specs.items():
            metrics = self.model_metrics.get(model_id, {})
            
            status["models"][model_id] = {
                "name": model_spec.name,
                "provider": model_spec.provider.value,
                "available": availability.get(model_id, False),
                "quality_rating": model_spec.quality_rating,
                "speed_rating": model_spec.speed_rating,
                "cost_per_token": model_spec.cost_per_output_token,
                "load_weight": self.load_balancing_weights.get(model_id, 1.0),
                "metrics": {
                    "total_requests": metrics.get("total_requests", 0),
                    "success_rate": (
                        metrics.get("successful_requests", 0) / 
                        max(metrics.get("total_requests", 1), 1)
                    ),
                    "total_cost": metrics.get("total_cost", 0.0),
                    "average_quality": metrics.get("average_quality", 0.0)
                }
            }
        
        return status


async def demonstrate_multi_model_integration():
    """Demonstrate multi-model integration capabilities"""
    print("="*80)
    print("MULTI-MODEL AI INTEGRATION v8.2 DEMONSTRATION")
    print("Unified Interface for Multiple AI Providers")
    print("="*80)
    
    # Create multi-model manager
    manager = MultiModelManager()
    
    print("\n1. MODEL AVAILABILITY CHECK")
    print("-" * 50)
    
    availability = await manager.check_model_availability()
    
    print("Model Availability:")
    for model_id, available in availability.items():
        model_spec = manager.model_specs[model_id]
        status = "✓ Available" if available else "✗ Unavailable"
        print(f"  {model_spec.name} ({model_spec.provider.value}): {status}")
    
    print(f"\nTotal available models: {len(manager.available_models)}")
    
    print("\n2. MODEL SELECTION AND SCORING")
    print("-" * 50)
    
    # Test model selection for different tasks
    test_scenarios = [
        {
            "task": "Code Analysis",
            "type": "analysis",
            "capabilities": [ModelCapability.CODE_GENERATION, ModelCapability.ANALYSIS],
            "quality_threshold": 0.9
        },
        {
            "task": "Quick Summarization",
            "type": "simple",
            "capabilities": [ModelCapability.SUMMARIZATION],
            "max_cost": 0.01,
            "max_response_time": 2.0
        },
        {
            "task": "Complex Reasoning",
            "type": "complex",
            "capabilities": [ModelCapability.REASONING],
            "quality_threshold": 0.85
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\nScenario: {scenario['task']}")
        
        best_model = await manager.select_best_model(
            task_type=scenario["type"],
            required_capabilities=scenario["capabilities"],
            max_cost=scenario.get("max_cost"),
            max_response_time=scenario.get("max_response_time"),
            quality_threshold=scenario.get("quality_threshold", 0.7)
        )
        
        if best_model:
            model_spec = manager.model_specs[best_model]
            print(f"  Selected: {model_spec.name} ({model_spec.provider.value})")
            print(f"  Quality: {model_spec.quality_rating:.2f}, Speed: {model_spec.speed_rating}")
            print(f"  Cost per token: ${model_spec.cost_per_output_token:.4f}")
        else:
            print("  No suitable model found")
    
    print("\n3. RESPONSE GENERATION")
    print("-" * 50)
    
    # Test actual response generation (if models are available)
    if manager.available_models:
        test_prompts = [
            {
                "prompt": "Explain the concept of machine learning in simple terms",
                "task_type": "explanation",
                "capabilities": [ModelCapability.TEXT_GENERATION]
            },
            {
                "prompt": "Write a Python function to calculate fibonacci numbers",
                "task_type": "code_generation",
                "capabilities": [ModelCapability.CODE_GENERATION]
            }
        ]
        
        for i, test in enumerate(test_prompts, 1):
            print(f"\nTest {i}: {test['task_type']}")
            print(f"Prompt: {test['prompt'][:60]}...")
            
            try:
                response = await manager.generate_response(
                    prompt=test["prompt"],
                    task_type=test["task_type"],
                    required_capabilities=test["capabilities"],
                    max_tokens=500
                )
                
                print(f"Model used: {response.model_spec.name}")
                print(f"Response time: {response.response_time:.3f}s")
                print(f"Cost: ${response.cost:.4f}")
                print(f"Tokens: {response.usage.get('input_tokens', 0)} in, {response.usage.get('output_tokens', 0)} out")
                print(f"Quality score: {response.quality_score:.2f}")
                print(f"Response preview: {response.content[:100]}...")
                
                if response.error:
                    print(f"Error: {response.error}")
                
            except Exception as e:
                print(f"Failed to generate response: {e}")
    else:
        print("No models available for testing")
    
    print("\n4. MODEL PERFORMANCE METRICS")
    print("-" * 50)
    
    status = await manager.get_model_status()
    
    print("Provider Summary:")
    for provider, stats in status["providers"].items():
        print(f"  {provider}: {stats['available']}/{stats['total']} available")
    
    print("\nModel Performance:")
    for model_id, model_info in status["models"].items():
        if model_info["metrics"]["total_requests"] > 0:
            print(f"\n  {model_info['name']}:")
            print(f"    Requests: {model_info['metrics']['total_requests']}")
            print(f"    Success rate: {model_info['metrics']['success_rate']:.2%}")
            print(f"    Total cost: ${model_info['metrics']['total_cost']:.4f}")
            print(f"    Load weight: {model_info['load_weight']:.2f}")
    
    print("\n5. LOAD BALANCING AND OPTIMIZATION")
    print("-" * 50)
    
    print("Load Balancing Weights:")
    for model_id, weight in manager.load_balancing_weights.items():
        model_spec = manager.model_specs[model_id]
        print(f"  {model_spec.name}: {weight:.2f}")
    
    print("\nCost Optimization:")
    cheapest_models = sorted(
        manager.model_specs.items(),
        key=lambda x: x[1].cost_per_output_token
    )
    
    print("Most cost-effective models:")
    for model_id, spec in cheapest_models[:3]:
        print(f"  {spec.name}: ${spec.cost_per_output_token:.4f}/token")
    
    print("\nSpeed Optimization:")
    fastest_models = sorted(
        manager.model_specs.items(),
        key=lambda x: x[1].speed_rating,
        reverse=True
    )
    
    print("Fastest models:")
    for model_id, spec in fastest_models[:3]:
        print(f"  {spec.name}: {spec.speed_rating:.0f} tokens/second")
    
    print("\n" + "="*80)
    print("MULTI-MODEL INTEGRATION DEMONSTRATION COMPLETE")
    print("="*80)
    
    # Summary of capabilities
    print("\nCapabilities Demonstrated:")
    print("• Multiple AI provider integration (Anthropic, OpenAI, Local)")
    print("• Intelligent model selection based on requirements")
    print("• Cost and performance optimization")
    print("• Load balancing and failover")
    print("• Real-time model availability checking")
    print("• Performance metrics and monitoring")
    print("• Unified API across different providers")
    print("• Automatic model scoring and ranking")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run demonstration
    asyncio.run(demonstrate_multi_model_integration())