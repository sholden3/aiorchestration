#!/usr/bin/env python3
"""
Token Optimization Engine v8.3
Advanced token usage optimization and cost management
Implements intelligent context compression, caching, and budget controls
"""

import asyncio
import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import logging
from collections import defaultdict, deque
import tiktoken
import zlib
import pickle
import re
from abc import ABC, abstractmethod

# Import dependencies
from multi_model_integration import MultiModelManager, ModelResponse, ModelSpec


class OptimizationStrategy(Enum):
    """Token optimization strategies"""
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    CONSERVATIVE = "conservative"
    CUSTOM = "custom"


class CompressionMethod(Enum):
    """Context compression methods"""
    TRUNCATION = "truncation"
    SUMMARIZATION = "summarization"
    KEYWORD_EXTRACTION = "keyword_extraction"
    SEMANTIC_COMPRESSION = "semantic_compression"
    HYBRID = "hybrid"


class CacheStrategy(Enum):
    """Caching strategies for optimization"""
    EXACT_MATCH = "exact_match"
    FUZZY_MATCH = "fuzzy_match"
    SEMANTIC_MATCH = "semantic_match"
    PATTERN_MATCH = "pattern_match"


@dataclass
class TokenBudget:
    """Token budget configuration"""
    daily_limit: int
    hourly_limit: int
    per_request_limit: int
    cost_limit_daily: float
    cost_limit_hourly: float
    emergency_reserve: int
    priority_allocation: Dict[str, float]  # Priority -> percentage
    
    def get_remaining_budget(self, current_usage: Dict[str, int]) -> Dict[str, int]:
        """Calculate remaining budget"""
        return {
            "daily": max(0, self.daily_limit - current_usage.get("daily", 0)),
            "hourly": max(0, self.hourly_limit - current_usage.get("hourly", 0)),
            "per_request": self.per_request_limit
        }


@dataclass
class OptimizationRule:
    """Rule for token optimization"""
    rule_id: str
    name: str
    description: str
    condition: str  # Python expression to evaluate
    action: str  # Action to take when condition is met
    parameters: Dict[str, Any]
    priority: int
    enabled: bool = True


@dataclass
class TokenUsageMetrics:
    """Token usage tracking metrics"""
    timestamp: datetime
    model_id: str
    task_type: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    compressed_tokens: int
    original_tokens: int
    cost: float
    optimization_applied: List[str]
    compression_ratio: float
    cache_hit: bool


@dataclass
class OptimizationResult:
    """Result of optimization process"""
    original_content: str
    optimized_content: str
    tokens_saved: int
    compression_ratio: float
    methods_applied: List[str]
    quality_score: float
    processing_time: float


class ContextCompressor(ABC):
    """Abstract base class for context compression methods"""
    
    @abstractmethod
    async def compress(self, content: str, target_tokens: int, context: Dict[str, Any]) -> str:
        """Compress content to target token count"""
        pass
    
    @abstractmethod
    def estimate_quality_loss(self, original: str, compressed: str) -> float:
        """Estimate quality loss from compression (0-1)"""
        pass


class TruncationCompressor(ContextCompressor):
    """Simple truncation-based compression"""
    
    def __init__(self, encoder: tiktoken.Encoding):
        self.encoder = encoder
    
    async def compress(self, content: str, target_tokens: int, context: Dict[str, Any]) -> str:
        """Compress by truncating content"""
        tokens = self.encoder.encode(content)
        
        if len(tokens) <= target_tokens:
            return content
        
        # Smart truncation - prefer keeping the end for conversations
        strategy = context.get("truncation_strategy", "end")
        
        if strategy == "end":
            truncated_tokens = tokens[-target_tokens:]
        elif strategy == "beginning":
            truncated_tokens = tokens[:target_tokens]
        else:  # middle
            half = target_tokens // 2
            truncated_tokens = tokens[:half] + tokens[-half:]
        
        return self.encoder.decode(truncated_tokens)
    
    def estimate_quality_loss(self, original: str, compressed: str) -> float:
        """Estimate quality loss from truncation"""
        original_len = len(original)
        compressed_len = len(compressed)
        
        if original_len == 0:
            return 0.0
        
        # Simple ratio-based estimation
        ratio = compressed_len / original_len
        return max(0.0, 1.0 - ratio)


class SummarizationCompressor(ContextCompressor):
    """AI-powered summarization compression"""
    
    def __init__(self, encoder: tiktoken.Encoding, model_manager: MultiModelManager):
        self.encoder = encoder
        self.model_manager = model_manager
    
    async def compress(self, content: str, target_tokens: int, context: Dict[str, Any]) -> str:
        """Compress using AI summarization"""
        current_tokens = len(self.encoder.encode(content))
        
        if current_tokens <= target_tokens:
            return content
        
        # Calculate compression ratio needed
        compression_ratio = target_tokens / current_tokens
        
        # Create summarization prompt
        prompt = f"""
Please summarize the following content to approximately {target_tokens} tokens.
Maintain the key information and context. Aim for a compression ratio of {compression_ratio:.1%}.

Content to summarize:
{content}

Summary:"""
        
        try:
            response = await self.model_manager.generate_response(
                prompt=prompt,
                task_type="summarization",
                max_tokens=target_tokens,
                temperature=0.3,
                fallback_models=["claude-3-haiku-20240307", "gpt-3.5-turbo"]
            )
            
            return response.content.strip()
            
        except Exception as e:
            logging.warning(f"Summarization compression failed: {e}")
            # Fallback to truncation
            truncator = TruncationCompressor(self.encoder)
            return await truncator.compress(content, target_tokens, context)
    
    def estimate_quality_loss(self, original: str, compressed: str) -> float:
        """Estimate quality loss from summarization"""
        # Summarization typically preserves more semantic meaning
        # but loses specific details
        original_tokens = len(self.encoder.encode(original))
        compressed_tokens = len(self.encoder.encode(compressed))
        
        if original_tokens == 0:
            return 0.0
        
        ratio = compressed_tokens / original_tokens
        
        # Quality loss is less severe than truncation for same compression
        quality_factor = 0.7  # Summarization preserves 70% of semantic value per token
        return max(0.0, 1.0 - (ratio * quality_factor))


class SemanticCompressor(ContextCompressor):
    """Semantic-aware compression using keyword extraction"""
    
    def __init__(self, encoder: tiktoken.Encoding):
        self.encoder = encoder
        # Common words to potentially remove
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'throughout',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'must', 'can'
        }
    
    async def compress(self, content: str, target_tokens: int, context: Dict[str, Any]) -> str:
        """Compress using semantic analysis"""
        current_tokens = len(self.encoder.encode(content))
        
        if current_tokens <= target_tokens:
            return content
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Score sentences by importance
        sentence_scores = []
        for sentence in sentences:
            score = self._score_sentence(sentence)
            tokens = len(self.encoder.encode(sentence))
            sentence_scores.append((score / max(tokens, 1), sentence, tokens))
        
        # Sort by score per token (efficiency)
        sentence_scores.sort(reverse=True)
        
        # Select sentences to keep
        selected_sentences = []
        total_tokens = 0
        
        for score, sentence, tokens in sentence_scores:
            if total_tokens + tokens <= target_tokens:
                selected_sentences.append(sentence)
                total_tokens += tokens
            
            if total_tokens >= target_tokens * 0.95:  # 95% of target
                break
        
        # Reconstruct in original order
        result_sentences = []
        for sentence in sentences:
            if sentence in selected_sentences:
                result_sentences.append(sentence)
        
        return '. '.join(result_sentences) + '.'
    
    def _score_sentence(self, sentence: str) -> float:
        """Score sentence importance"""
        words = sentence.lower().split()
        
        # Remove stop words for scoring
        content_words = [w for w in words if w not in self.stop_words]
        
        score = 0.0
        
        # Length bonus (moderate length preferred)
        word_count = len(content_words)
        if 5 <= word_count <= 20:
            score += 2.0
        elif word_count > 20:
            score += 1.0
        
        # Technical terms bonus
        technical_indicators = ['function', 'class', 'method', 'algorithm', 'system', 
                              'implementation', 'architecture', 'performance', 'security']
        for indicator in technical_indicators:
            if indicator in sentence.lower():
                score += 1.5
        
        # Question bonus (often important)
        if '?' in sentence:
            score += 1.0
        
        # Code reference bonus
        if any(char in sentence for char in ['()', '{}', '[]', '`']):
            score += 1.0
        
        return score
    
    def estimate_quality_loss(self, original: str, compressed: str) -> float:
        """Estimate quality loss from semantic compression"""
        original_sentences = len(re.split(r'[.!?]+', original))
        compressed_sentences = len(re.split(r'[.!?]+', compressed))
        
        if original_sentences == 0:
            return 0.0
        
        # Semantic compression preserves sentence structure
        ratio = compressed_sentences / original_sentences
        quality_factor = 0.8  # Better preservation than simple truncation
        
        return max(0.0, 1.0 - (ratio * quality_factor))


class TokenOptimizationEngine:
    """Advanced token optimization and cost management engine"""
    
    def __init__(self, model_manager: Optional[MultiModelManager] = None):
        """Initialize optimization engine"""
        self.model_manager = model_manager or MultiModelManager()
        
        # Token tracking
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.usage_metrics: List[TokenUsageMetrics] = []
        self.cache: Dict[str, Any] = {}
        
        # Budget management
        self.budgets: Dict[str, TokenBudget] = {}
        self.current_usage: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Optimization rules
        self.optimization_rules: Dict[str, OptimizationRule] = {}
        self.optimization_strategies: Dict[str, Dict[str, Any]] = {}
        
        # Compressors
        self.compressors: Dict[CompressionMethod, ContextCompressor] = {
            CompressionMethod.TRUNCATION: TruncationCompressor(self.encoder),
            CompressionMethod.SUMMARIZATION: SummarizationCompressor(self.encoder, self.model_manager),
            CompressionMethod.SEMANTIC_COMPRESSION: SemanticCompressor(self.encoder)
        }
        
        # Configuration
        self.cache_ttl = 3600  # 1 hour
        self.max_cache_size = 10000
        
        self._initialize_default_strategies()
        self._initialize_default_rules()
    
    def _initialize_default_strategies(self):
        """Initialize default optimization strategies"""
        self.optimization_strategies = {
            OptimizationStrategy.AGGRESSIVE.value: {
                "max_compression_ratio": 0.3,
                "cache_enabled": True,
                "compression_methods": [
                    CompressionMethod.SUMMARIZATION,
                    CompressionMethod.SEMANTIC_COMPRESSION,
                    CompressionMethod.TRUNCATION
                ],
                "quality_threshold": 0.6,
                "cost_priority": 0.8
            },
            OptimizationStrategy.BALANCED.value: {
                "max_compression_ratio": 0.5,
                "cache_enabled": True,
                "compression_methods": [
                    CompressionMethod.SEMANTIC_COMPRESSION,
                    CompressionMethod.SUMMARIZATION
                ],
                "quality_threshold": 0.75,
                "cost_priority": 0.5
            },
            OptimizationStrategy.CONSERVATIVE.value: {
                "max_compression_ratio": 0.8,
                "cache_enabled": True,
                "compression_methods": [
                    CompressionMethod.SEMANTIC_COMPRESSION
                ],
                "quality_threshold": 0.9,
                "cost_priority": 0.2
            }
        }
    
    def _initialize_default_rules(self):
        """Initialize default optimization rules"""
        rules = [
            OptimizationRule(
                rule_id="budget_warning",
                name="Budget Warning",
                description="Warn when approaching budget limits",
                condition="hourly_usage > budget.hourly_limit * 0.8",
                action="log_warning",
                parameters={"threshold": 0.8},
                priority=1
            ),
            OptimizationRule(
                rule_id="emergency_compression",
                name="Emergency Compression",
                description="Apply aggressive compression when budget critical",
                condition="hourly_usage > budget.hourly_limit * 0.95",
                action="force_compression",
                parameters={"strategy": "aggressive"},
                priority=0
            ),
            OptimizationRule(
                rule_id="cache_optimization",
                name="Cache Optimization",
                description="Use cached responses for similar queries",
                condition="similarity_score > 0.85",
                action="use_cache",
                parameters={"similarity_threshold": 0.85},
                priority=2
            )
        ]
        
        for rule in rules:
            self.optimization_rules[rule.rule_id] = rule
    
    def set_budget(self, budget_id: str, budget: TokenBudget):
        """Set token budget for a user/project"""
        self.budgets[budget_id] = budget
    
    def get_current_usage(self, budget_id: str) -> Dict[str, int]:
        """Get current token usage for a budget"""
        now = datetime.now()
        current_hour = now.hour
        current_date = now.date()
        
        # Calculate usage for current period
        hourly_usage = 0
        daily_usage = 0
        
        for metric in self.usage_metrics:
            if budget_id not in metric.task_type:  # Simple budget association
                continue
                
            metric_date = metric.timestamp.date()
            metric_hour = metric.timestamp.hour
            
            total_tokens = metric.input_tokens + metric.output_tokens
            
            if metric_date == current_date:
                daily_usage += total_tokens
                
                if metric_hour == current_hour:
                    hourly_usage += total_tokens
        
        return {
            "hourly": hourly_usage,
            "daily": daily_usage
        }
    
    async def optimize_request(
        self,
        content: str,
        target_tokens: Optional[int] = None,
        strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
        budget_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> OptimizationResult:
        """Optimize content for token usage"""
        
        start_time = time.time()
        original_content = content
        context = context or {}
        
        # Calculate original token count
        original_tokens = len(self.encoder.encode(content))
        
        # Check cache first
        cache_key = self._generate_cache_key(content, target_tokens, strategy.value)
        cached_result = self._get_cached_result(cache_key)
        
        if cached_result:
            logging.info(f"Using cached optimization result for {original_tokens} tokens")
            return cached_result
        
        # Determine target tokens
        if not target_tokens:
            target_tokens = self._calculate_optimal_tokens(original_tokens, strategy, budget_id)
        
        # Apply optimization rules
        optimization_context = {
            "original_tokens": original_tokens,
            "target_tokens": target_tokens,
            "budget_id": budget_id,
            "strategy": strategy.value
        }
        
        await self._apply_optimization_rules(optimization_context)
        
        # Perform optimization
        optimized_content = content
        methods_applied = []
        
        if original_tokens > target_tokens:
            strategy_config = self.optimization_strategies[strategy.value]
            compression_methods = strategy_config["compression_methods"]
            
            # Try compression methods in order
            for method in compression_methods:
                if len(self.encoder.encode(optimized_content)) <= target_tokens:
                    break
                
                compressor = self.compressors[method]
                compressed = await compressor.compress(
                    optimized_content, 
                    target_tokens, 
                    context
                )
                
                # Check quality
                quality_loss = compressor.estimate_quality_loss(optimized_content, compressed)
                quality_threshold = strategy_config["quality_threshold"]
                
                if quality_loss <= (1.0 - quality_threshold):
                    optimized_content = compressed
                    methods_applied.append(method.value)
        
        # Calculate results
        optimized_tokens = len(self.encoder.encode(optimized_content))
        tokens_saved = original_tokens - optimized_tokens
        compression_ratio = optimized_tokens / original_tokens if original_tokens > 0 else 1.0
        quality_score = self._calculate_quality_score(original_content, optimized_content)
        processing_time = time.time() - start_time
        
        result = OptimizationResult(
            original_content=original_content,
            optimized_content=optimized_content,
            tokens_saved=tokens_saved,
            compression_ratio=compression_ratio,
            methods_applied=methods_applied,
            quality_score=quality_score,
            processing_time=processing_time
        )
        
        # Cache result
        self._cache_result(cache_key, result)
        
        return result
    
    def _calculate_optimal_tokens(
        self,
        original_tokens: int,
        strategy: OptimizationStrategy,
        budget_id: Optional[str]
    ) -> int:
        """Calculate optimal token count based on strategy and budget"""
        
        strategy_config = self.optimization_strategies[strategy.value]
        max_compression = strategy_config["max_compression_ratio"]
        
        # Base target from strategy
        target_tokens = int(original_tokens * max_compression)
        
        # Adjust based on budget constraints
        if budget_id and budget_id in self.budgets:
            budget = self.budgets[budget_id]
            current_usage = self.get_current_usage(budget_id)
            remaining_budget = budget.get_remaining_budget(current_usage)
            
            # If budget is tight, compress more aggressively
            hourly_ratio = current_usage["hourly"] / budget.hourly_limit
            if hourly_ratio > 0.8:
                # Increase compression when budget is tight
                budget_factor = max(0.3, 1.0 - hourly_ratio)
                target_tokens = int(target_tokens * budget_factor)
        
        return max(target_tokens, 100)  # Minimum 100 tokens
    
    async def _apply_optimization_rules(self, context: Dict[str, Any]):
        """Apply optimization rules based on current context"""
        
        # Sort rules by priority
        sorted_rules = sorted(
            self.optimization_rules.values(),
            key=lambda r: r.priority
        )
        
        for rule in sorted_rules:
            if not rule.enabled:
                continue
            
            # Evaluate condition (simplified evaluation)
            try:
                condition_met = self._evaluate_rule_condition(rule.condition, context)
                
                if condition_met:
                    await self._execute_rule_action(rule.action, rule.parameters, context)
                    
            except Exception as e:
                logging.warning(f"Failed to evaluate rule {rule.rule_id}: {e}")
    
    def _evaluate_rule_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate rule condition (simplified)"""
        # This is a simplified implementation
        # In production, use a proper expression evaluator
        
        if "budget.hourly_limit" in condition:
            budget_id = context.get("budget_id")
            if budget_id and budget_id in self.budgets:
                budget = self.budgets[budget_id]
                current_usage = self.get_current_usage(budget_id)
                
                # Replace variables in condition
                condition = condition.replace("hourly_usage", str(current_usage["hourly"]))
                condition = condition.replace("budget.hourly_limit", str(budget.hourly_limit))
                
                try:
                    return eval(condition)
                except:
                    return False
        
        return False
    
    async def _execute_rule_action(self, action: str, parameters: Dict[str, Any], context: Dict[str, Any]):
        """Execute rule action"""
        
        if action == "log_warning":
            logging.warning(f"Optimization rule triggered: {parameters}")
        
        elif action == "force_compression":
            strategy = parameters.get("strategy", "aggressive")
            context["forced_strategy"] = strategy
            logging.info(f"Forcing compression strategy: {strategy}")
        
        elif action == "use_cache":
            context["prefer_cache"] = True
            logging.info("Preferring cached results due to rule")
    
    def _generate_cache_key(self, content: str, target_tokens: Optional[int], strategy: str) -> str:
        """Generate cache key for content"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        key_parts = [content_hash, str(target_tokens), strategy]
        return ":".join(key_parts)
    
    def _get_cached_result(self, cache_key: str) -> Optional[OptimizationResult]:
        """Get cached optimization result"""
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            
            # Check TTL
            if time.time() - cached_data["timestamp"] < self.cache_ttl:
                return cached_data["result"]
            else:
                del self.cache[cache_key]
        
        return None
    
    def _cache_result(self, cache_key: str, result: OptimizationResult):
        """Cache optimization result"""
        # Clean cache if too large
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entries
            oldest_keys = sorted(
                self.cache.keys(),
                key=lambda k: self.cache[k]["timestamp"]
            )[:self.max_cache_size // 2]
            
            for key in oldest_keys:
                del self.cache[key]
        
        self.cache[cache_key] = {
            "result": result,
            "timestamp": time.time()
        }
    
    def _calculate_quality_score(self, original: str, optimized: str) -> float:
        """Calculate quality score for optimized content"""
        
        # Simple quality metrics
        original_len = len(original)
        optimized_len = len(optimized)
        
        if original_len == 0:
            return 1.0
        
        # Length preservation score
        length_score = min(1.0, optimized_len / original_len)
        
        # Word preservation score
        original_words = set(original.lower().split())
        optimized_words = set(optimized.lower().split())
        
        if original_words:
            word_score = len(original_words & optimized_words) / len(original_words)
        else:
            word_score = 1.0
        
        # Weighted average
        quality_score = (length_score * 0.3 + word_score * 0.7)
        
        return quality_score
    
    def track_usage(self, metrics: TokenUsageMetrics):
        """Track token usage metrics"""
        self.usage_metrics.append(metrics)
        
        # Update current usage
        budget_key = metrics.task_type  # Simplified budget association
        hour_key = f"{metrics.timestamp.date()}_{metrics.timestamp.hour}"
        day_key = str(metrics.timestamp.date())
        
        self.current_usage[budget_key]["hourly"] += metrics.input_tokens + metrics.output_tokens
        self.current_usage[budget_key]["daily"] += metrics.input_tokens + metrics.output_tokens
        
        # Cleanup old metrics (keep last 7 days)
        cutoff_date = datetime.now() - timedelta(days=7)
        self.usage_metrics = [
            m for m in self.usage_metrics
            if m.timestamp > cutoff_date
        ]
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        
        if not self.usage_metrics:
            return {"error": "No usage metrics available"}
        
        # Calculate aggregated stats
        total_original_tokens = sum(m.original_tokens for m in self.usage_metrics)
        total_optimized_tokens = sum(m.input_tokens + m.output_tokens for m in self.usage_metrics)
        total_cached_tokens = sum(m.cached_tokens for m in self.usage_metrics)
        total_cost = sum(m.cost for m in self.usage_metrics)
        
        cache_hits = sum(1 for m in self.usage_metrics if m.cache_hit)
        cache_rate = cache_hits / len(self.usage_metrics) if self.usage_metrics else 0
        
        # Compression stats
        compression_ratios = [m.compression_ratio for m in self.usage_metrics if m.compression_ratio > 0]
        avg_compression = sum(compression_ratios) / len(compression_ratios) if compression_ratios else 1.0
        
        # Method usage
        method_usage = defaultdict(int)
        for metric in self.usage_metrics:
            for method in metric.optimization_applied:
                method_usage[method] += 1
        
        return {
            "total_requests": len(self.usage_metrics),
            "token_stats": {
                "original_tokens": total_original_tokens,
                "optimized_tokens": total_optimized_tokens,
                "tokens_saved": total_original_tokens - total_optimized_tokens,
                "savings_ratio": (total_original_tokens - total_optimized_tokens) / max(total_original_tokens, 1),
                "cached_tokens": total_cached_tokens
            },
            "cost_stats": {
                "total_cost": total_cost,
                "estimated_original_cost": total_cost / avg_compression if avg_compression > 0 else total_cost,
                "cost_savings": total_cost * (1 - avg_compression)
            },
            "performance_stats": {
                "cache_hit_rate": cache_rate,
                "average_compression_ratio": avg_compression,
                "method_usage": dict(method_usage)
            },
            "budget_status": {
                budget_id: {
                    "current_usage": self.get_current_usage(budget_id),
                    "remaining": budget.get_remaining_budget(self.get_current_usage(budget_id))
                }
                for budget_id, budget in self.budgets.items()
            }
        }


async def demonstrate_token_optimization():
    """Demonstrate token optimization capabilities"""
    print("="*80)
    print("TOKEN OPTIMIZATION ENGINE v8.3 DEMONSTRATION")
    print("Advanced Token Usage Optimization and Cost Management")
    print("="*80)
    
    # Create optimization engine
    optimizer = TokenOptimizationEngine()
    
    print("\n1. BUDGET CONFIGURATION")
    print("-" * 50)
    
    # Set up sample budget
    daily_budget = TokenBudget(
        daily_limit=100000,
        hourly_limit=10000,
        per_request_limit=5000,
        cost_limit_daily=50.0,
        cost_limit_hourly=5.0,
        emergency_reserve=5000,
        priority_allocation={
            "critical": 0.4,
            "high": 0.3,
            "medium": 0.2,
            "low": 0.1
        }
    )
    
    optimizer.set_budget("demo_project", daily_budget)
    print("Budget configured:")
    print(f"  Daily limit: {daily_budget.daily_limit:,} tokens")
    print(f"  Hourly limit: {daily_budget.hourly_limit:,} tokens")
    print(f"  Per request limit: {daily_budget.per_request_limit:,} tokens")
    print(f"  Daily cost limit: ${daily_budget.cost_limit_daily:.2f}")
    
    print("\n2. OPTIMIZATION STRATEGIES")
    print("-" * 50)
    
    # Test content for optimization
    test_content = """
    Machine learning is a subset of artificial intelligence that focuses on the development of algorithms and statistical models that enable computer systems to automatically improve their performance on a specific task through experience. The core idea behind machine learning is to create systems that can learn and adapt without being explicitly programmed for every possible scenario.
    
    There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning. Supervised learning involves training algorithms on labeled datasets, where the correct answers are provided during the training process. Common supervised learning tasks include classification and regression. Unsupervised learning, on the other hand, deals with unlabeled data and aims to discover hidden patterns or structures within the dataset. Clustering and dimensionality reduction are typical unsupervised learning techniques.
    
    Reinforcement learning is a type of machine learning where an agent learns to make decisions by taking actions in an environment and receiving feedback in the form of rewards or penalties. This approach is particularly useful for problems where the optimal strategy is not immediately apparent and must be discovered through trial and error.
    
    Deep learning, a subset of machine learning, uses artificial neural networks with multiple layers to model and understand complex patterns in data. These deep neural networks have proven to be highly effective for tasks such as image recognition, natural language processing, and speech recognition. The success of deep learning has been driven by the availability of large datasets, increased computational power, and improvements in algorithms and architectures.
    
    The applications of machine learning are vast and continue to grow. In healthcare, machine learning is used for medical diagnosis, drug discovery, and personalized treatment plans. In finance, it powers fraud detection, algorithmic trading, and credit scoring. In technology, machine learning enables recommendation systems, search engines, and autonomous vehicles. As the field continues to evolve, we can expect to see even more innovative applications that will transform various industries and aspects of our daily lives.
    """
    
    print(f"Original content: {len(test_content)} characters")
    print(f"Original tokens: {len(optimizer.encoder.encode(test_content))}")
    
    # Test different optimization strategies
    strategies = [
        (OptimizationStrategy.CONSERVATIVE, 80),
        (OptimizationStrategy.BALANCED, 60),
        (OptimizationStrategy.AGGRESSIVE, 40)
    ]
    
    for strategy, target_percent in strategies:
        original_tokens = len(optimizer.encoder.encode(test_content))
        target_tokens = int(original_tokens * (target_percent / 100))
        
        print(f"\n{strategy.value.upper()} Strategy (target: {target_percent}% = {target_tokens} tokens):")
        
        result = await optimizer.optimize_request(
            content=test_content,
            target_tokens=target_tokens,
            strategy=strategy,
            budget_id="demo_project"
        )
        
        print(f"  Tokens saved: {result.tokens_saved}")
        print(f"  Compression ratio: {result.compression_ratio:.2%}")
        print(f"  Quality score: {result.quality_score:.2f}")
        print(f"  Methods used: {', '.join(result.methods_applied)}")
        print(f"  Processing time: {result.processing_time:.3f}s")
        print(f"  Optimized preview: {result.optimized_content[:100]}...")
    
    print("\n3. CACHE PERFORMANCE")
    print("-" * 50)
    
    # Test caching
    print("Testing cache performance...")
    
    # First request (cache miss)
    start_time = time.time()
    result1 = await optimizer.optimize_request(
        content=test_content,
        target_tokens=2000,
        strategy=OptimizationStrategy.BALANCED
    )
    first_time = time.time() - start_time
    
    # Second identical request (cache hit)
    start_time = time.time()
    result2 = await optimizer.optimize_request(
        content=test_content,
        target_tokens=2000,
        strategy=OptimizationStrategy.BALANCED
    )
    second_time = time.time() - start_time
    
    print(f"First request (cache miss): {first_time:.3f}s")
    print(f"Second request (cache hit): {second_time:.3f}s")
    print(f"Cache speedup: {first_time / max(second_time, 0.001):.1f}x")
    print(f"Results identical: {result1.optimized_content == result2.optimized_content}")
    
    print("\n4. USAGE TRACKING")
    print("-" * 50)
    
    # Simulate usage tracking
    sample_metrics = [
        TokenUsageMetrics(
            timestamp=datetime.now(),
            model_id="claude-3-sonnet-20240229",
            task_type="demo_project",
            input_tokens=1500,
            output_tokens=800,
            cached_tokens=0,
            compressed_tokens=200,
            original_tokens=2500,
            cost=0.012,
            optimization_applied=["semantic_compression"],
            compression_ratio=0.92,
            cache_hit=False
        ),
        TokenUsageMetrics(
            timestamp=datetime.now(),
            model_id="claude-3-haiku-20240307",
            task_type="demo_project",
            input_tokens=800,
            output_tokens=400,
            cached_tokens=400,
            compressed_tokens=100,
            original_tokens=1300,
            cost=0.003,
            optimization_applied=["truncation"],
            compression_ratio=0.85,
            cache_hit=True
        )
    ]
    
    for metric in sample_metrics:
        optimizer.track_usage(metric)
    
    print("Usage metrics tracked:")
    for i, metric in enumerate(sample_metrics, 1):
        print(f"  Request {i}:")
        print(f"    Model: {metric.model_id}")
        print(f"    Tokens: {metric.input_tokens + metric.output_tokens}")
        print(f"    Cost: ${metric.cost:.4f}")
        print(f"    Cache hit: {metric.cache_hit}")
        print(f"    Compression: {metric.compression_ratio:.1%}")
    
    print("\n5. OPTIMIZATION STATISTICS")
    print("-" * 50)
    
    stats = optimizer.get_optimization_stats()
    
    print("Token Statistics:")
    token_stats = stats["token_stats"]
    print(f"  Original tokens: {token_stats['original_tokens']:,}")
    print(f"  Optimized tokens: {token_stats['optimized_tokens']:,}")
    print(f"  Tokens saved: {token_stats['tokens_saved']:,}")
    print(f"  Savings ratio: {token_stats['savings_ratio']:.1%}")
    
    print("\nCost Statistics:")
    cost_stats = stats["cost_stats"]
    print(f"  Total cost: ${cost_stats['total_cost']:.4f}")
    print(f"  Estimated savings: ${cost_stats['cost_savings']:.4f}")
    
    print("\nPerformance Statistics:")
    perf_stats = stats["performance_stats"]
    print(f"  Cache hit rate: {perf_stats['cache_hit_rate']:.1%}")
    print(f"  Average compression: {perf_stats['average_compression_ratio']:.1%}")
    print(f"  Method usage: {perf_stats['method_usage']}")
    
    print("\nBudget Status:")
    for budget_id, budget_info in stats["budget_status"].items():
        print(f"  {budget_id}:")
        usage = budget_info["current_usage"]
        remaining = budget_info["remaining"]
        print(f"    Hourly: {usage['hourly']:,} / {remaining['hourly']:,} remaining")
        print(f"    Daily: {usage['daily']:,} / {remaining['daily']:,} remaining")
    
    print("\n6. COMPRESSION METHOD COMPARISON")
    print("-" * 50)
    
    # Compare different compression methods
    methods_to_test = [
        (CompressionMethod.TRUNCATION, "Simple truncation"),
        (CompressionMethod.SEMANTIC_COMPRESSION, "Semantic compression"),
        (CompressionMethod.SUMMARIZATION, "AI summarization")
    ]
    
    target_tokens = 1000
    original_tokens = len(optimizer.encoder.encode(test_content))
    
    print(f"Comparing compression methods (target: {target_tokens} tokens):")
    
    for method, description in methods_to_test:
        if method in optimizer.compressors:
            compressor = optimizer.compressors[method]
            
            start_time = time.time()
            compressed = await compressor.compress(test_content, target_tokens, {})
            compression_time = time.time() - start_time
            
            compressed_tokens = len(optimizer.encoder.encode(compressed))
            quality_loss = compressor.estimate_quality_loss(test_content, compressed)
            
            print(f"\n  {description}:")
            print(f"    Result tokens: {compressed_tokens}")
            print(f"    Compression ratio: {compressed_tokens / original_tokens:.1%}")
            print(f"    Quality loss: {quality_loss:.1%}")
            print(f"    Processing time: {compression_time:.3f}s")
            print(f"    Preview: {compressed[:80]}...")
    
    print("\n" + "="*80)
    print("TOKEN OPTIMIZATION DEMONSTRATION COMPLETE")
    print("="*80)
    
    # Summary of capabilities
    print("\nCapabilities Demonstrated:")
    print("• Multi-strategy token optimization (Conservative, Balanced, Aggressive)")
    print("• Intelligent compression methods (Truncation, Semantic, AI Summarization)")
    print("• Budget management and cost control")
    print("• Performance caching and optimization")
    print("• Real-time usage tracking and analytics")
    print("• Quality-aware compression with thresholds")
    print("• Rule-based optimization triggers")
    print("• Cross-method performance comparison")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run demonstration
    asyncio.run(demonstrate_token_optimization())