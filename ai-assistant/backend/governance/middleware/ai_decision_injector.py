"""
File: ai-assistant/backend/governance/middleware/ai_decision_injector.py
Purpose: Middleware for injecting AI-driven decisions into request processing
Architecture: Integrates with FastAPI middleware stack for intelligent request handling
Dependencies: asyncio, enum, typing, logging
Owner: Dr. Sarah Chen

@fileoverview AI decision injection middleware for intelligent request routing
@author Dr. Sarah Chen v1.0 - Backend Systems Architect
@architecture Backend - Middleware layer for AI-driven decision injection
@business_logic Decision generation, confidence scoring, action application
@integration_points FastAPI middleware stack, governance validators, caching layer
@error_handling Timeout on decision generation, fallback on low confidence
@performance Sub-second decision generation, configurable timeout (1s default)
"""

from enum import Enum
from typing import Dict, Any, Optional, Callable, Awaitable, List
from dataclasses import dataclass
import asyncio
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """
    Types of AI decisions that can be injected.
    
    Each type represents a different category of AI-driven decision
    that can influence request processing.
    """
    ROUTING = "routing"              # Route request to specific handler
    VALIDATION = "validation"        # Validate request parameters
    TRANSFORMATION = "transformation" # Transform request/response data
    CACHING = "caching"             # Cache strategy decisions
    RATE_LIMITING = "rate_limiting"  # Dynamic rate limit adjustments
    SECURITY = "security"            # Security-related decisions


@dataclass
class AIDecision:
    """
    Represents an AI-driven decision for request processing.
    
    Attributes:
        type: Type of decision
        action: Specific action to take
        confidence: Confidence score (0-1)
        reasoning: Explanation for the decision
        metadata: Additional decision context
        timestamp: When decision was made
    """
    type: DecisionType
    action: str
    confidence: float
    reasoning: str
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """
        Check if decision meets confidence threshold.
        
        Args:
            threshold: Minimum confidence level (default: 0.8)
            
        Returns:
            True if confidence exceeds threshold
        """
        return self.confidence >= threshold
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert decision to dictionary representation.
        
        Returns:
            Dictionary with decision data
        """
        return {
            'type': self.type.value,
            'action': self.action,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }


class AIDecisionEngine:
    """
    Engine for generating AI-driven decisions.
    
    This class simulates an AI decision engine that would normally
    interface with ML models or external AI services.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize AI decision engine.
        
        Args:
            config: Engine configuration
        """
        self.config = config or {}
        self.decision_history: List[AIDecision] = []
        self.max_history = 1000
        
        # Decision rules (simulated AI logic)
        self.rules = self._load_decision_rules()
        
        logger.info("AIDecisionEngine initialized")
    
    def _load_decision_rules(self) -> Dict[str, Any]:
        """
        Load decision rules (simulated AI model).
        
        Returns:
            Dictionary of decision rules
        """
        return {
            'rate_limiting': {
                'high_traffic_threshold': 100,
                'burst_allowance': 10,
                'cooldown_period': 60
            },
            'caching': {
                'cache_threshold': 0.7,
                'ttl_default': 300,
                'ttl_static': 3600
            },
            'security': {
                'suspicious_patterns': ['../..', 'script>', 'DROP TABLE'],
                'blocked_ips': [],
                'require_auth_paths': ['/api/admin/*', '/api/secure/*']
            }
        }
    
    async def make_decision(self, context: Dict[str, Any]) -> Optional[AIDecision]:
        """
        Generate an AI decision based on context.
        
        Args:
            context: Request context including endpoint, method, headers, etc.
            
        Returns:
            AIDecision if action needed, None otherwise
        """
        # Analyze context and generate decision
        endpoint = context.get('endpoint', '')
        method = context.get('method', 'GET')
        headers = context.get('headers', {})
        
        # Check for security decisions
        security_decision = await self._check_security(context)
        if security_decision:
            self._record_decision(security_decision)
            return security_decision
        
        # Check for rate limiting decisions
        rate_decision = await self._check_rate_limiting(context)
        if rate_decision:
            self._record_decision(rate_decision)
            return rate_decision
        
        # Check for caching decisions
        cache_decision = await self._check_caching(context)
        if cache_decision:
            self._record_decision(cache_decision)
            return cache_decision
        
        return None
    
    async def _check_security(self, context: Dict[str, Any]) -> Optional[AIDecision]:
        """
        Check for security-related decisions.
        
        Args:
            context: Request context
            
        Returns:
            Security decision if needed
        """
        endpoint = context.get('endpoint', '')
        body = context.get('body', '')
        
        # Check for suspicious patterns
        for pattern in self.rules['security']['suspicious_patterns']:
            if pattern in endpoint or pattern in str(body):
                return AIDecision(
                    type=DecisionType.SECURITY,
                    action='block',
                    confidence=0.95,
                    reasoning=f"Suspicious pattern detected: {pattern}",
                    metadata={'pattern': pattern}
                )
        
        # Check if authentication required
        for auth_path in self.rules['security']['require_auth_paths']:
            if self._match_path(auth_path, endpoint):
                if not context.get('authenticated', False):
                    return AIDecision(
                        type=DecisionType.SECURITY,
                        action='require_auth',
                        confidence=1.0,
                        reasoning=f"Authentication required for {endpoint}",
                        metadata={'endpoint': endpoint}
                    )
        
        return None
    
    async def _check_rate_limiting(self, context: Dict[str, Any]) -> Optional[AIDecision]:
        """
        Check for rate limiting decisions.
        
        Args:
            context: Request context
            
        Returns:
            Rate limiting decision if needed
        """
        request_count = context.get('request_count', 0)
        threshold = self.rules['rate_limiting']['high_traffic_threshold']
        
        if request_count > threshold:
            return AIDecision(
                type=DecisionType.RATE_LIMITING,
                action='throttle',
                confidence=0.85,
                reasoning=f"High request rate detected: {request_count} requests",
                metadata={
                    'request_count': request_count,
                    'threshold': threshold,
                    'cooldown': self.rules['rate_limiting']['cooldown_period']
                }
            )
        
        return None
    
    async def _check_caching(self, context: Dict[str, Any]) -> Optional[AIDecision]:
        """
        Check for caching decisions.
        
        Args:
            context: Request context
            
        Returns:
            Caching decision if needed
        """
        method = context.get('method', 'GET')
        endpoint = context.get('endpoint', '')
        
        # Only cache GET requests
        if method != 'GET':
            return None
        
        # Determine if endpoint should be cached
        if '/static/' in endpoint:
            ttl = self.rules['caching']['ttl_static']
        else:
            ttl = self.rules['caching']['ttl_default']
        
        return AIDecision(
            type=DecisionType.CACHING,
            action='cache',
            confidence=0.75,
            reasoning=f"Cacheable {method} request to {endpoint}",
            metadata={'ttl': ttl}
        )
    
    def _match_path(self, pattern: str, path: str) -> bool:
        """
        Match path against pattern with wildcard support.
        
        Args:
            pattern: Path pattern (supports * wildcard)
            path: Actual path to match
            
        Returns:
            True if path matches pattern
        """
        if pattern.endswith('*'):
            return path.startswith(pattern[:-1])
        return pattern == path
    
    def _record_decision(self, decision: AIDecision):
        """
        Record decision in history.
        
        Args:
            decision: Decision to record
        """
        self.decision_history.append(decision)
        
        # Limit history size
        if len(self.decision_history) > self.max_history:
            self.decision_history = self.decision_history[-self.max_history:]


class AIDecisionInjector:
    """
    Middleware for injecting AI decisions into request processing.
    
    This class acts as middleware that intercepts requests, generates
    AI decisions, and applies them to influence request handling.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize AI decision injector.
        
        Args:
            config: Injector configuration including:
                - enabled: Whether injection is active (default: True)
                - confidence_threshold: Minimum confidence to apply (default: 0.7)
                - decision_timeout: Timeout for decision generation (default: 1.0)
        """
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        self.decision_timeout = self.config.get('decision_timeout', 1.0)
        
        self.engine = AIDecisionEngine(config)
        self.injection_stats = {
            'total_requests': 0,
            'decisions_made': 0,
            'decisions_applied': 0,
            'decisions_rejected': 0
        }
        
        logger.info(f"AIDecisionInjector initialized (enabled={self.enabled})")
    
    async def process_request(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process request and inject AI decisions.
        
        Args:
            context: Request context
            
        Returns:
            Modified context with AI decisions applied
        """
        if not self.enabled:
            return context
        
        self.injection_stats['total_requests'] += 1
        
        try:
            # Generate AI decision with timeout
            decision = await asyncio.wait_for(
                self.engine.make_decision(context),
                timeout=self.decision_timeout
            )
            
            if decision:
                self.injection_stats['decisions_made'] += 1
                
                # Apply decision if confidence threshold met
                if decision.is_high_confidence(self.confidence_threshold):
                    context = await self._apply_decision(context, decision)
                    self.injection_stats['decisions_applied'] += 1
                else:
                    self.injection_stats['decisions_rejected'] += 1
                    logger.debug(f"Decision rejected due to low confidence: {decision.confidence}")
                
                # Add decision to context for logging
                context['ai_decision'] = decision.to_dict()
            
        except asyncio.TimeoutError:
            logger.warning(f"AI decision timeout after {self.decision_timeout}s")
        except Exception as e:
            logger.error(f"Error in AI decision processing: {e}")
        
        return context
    
    async def _apply_decision(self, context: Dict[str, Any], decision: AIDecision) -> Dict[str, Any]:
        """
        Apply AI decision to request context.
        
        Args:
            context: Request context
            decision: AI decision to apply
            
        Returns:
            Modified context
        """
        logger.info(f"Applying AI decision: {decision.type.value} - {decision.action}")
        
        if decision.type == DecisionType.SECURITY:
            if decision.action == 'block':
                context['blocked'] = True
                context['block_reason'] = decision.reasoning
            elif decision.action == 'require_auth':
                context['require_auth'] = True
        
        elif decision.type == DecisionType.RATE_LIMITING:
            if decision.action == 'throttle':
                context['throttled'] = True
                context['throttle_delay'] = decision.metadata.get('cooldown', 60)
        
        elif decision.type == DecisionType.CACHING:
            if decision.action == 'cache':
                context['cache_enabled'] = True
                context['cache_ttl'] = decision.metadata.get('ttl', 300)
        
        elif decision.type == DecisionType.TRANSFORMATION:
            # Apply data transformation
            context['transform'] = decision.metadata
        
        elif decision.type == DecisionType.ROUTING:
            # Apply routing decision
            context['route_override'] = decision.metadata.get('target_route')
        
        return context
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get injection statistics.
        
        Returns:
            Dictionary containing:
                - total_requests: Total requests processed
                - decisions_made: Number of decisions generated
                - decisions_applied: Number of decisions applied
                - decisions_rejected: Number of low-confidence rejections
                - decision_rate: Percentage of requests with decisions
                - application_rate: Percentage of decisions applied
        """
        stats = self.injection_stats.copy()
        
        if stats['total_requests'] > 0:
            stats['decision_rate'] = (stats['decisions_made'] / stats['total_requests']) * 100
        else:
            stats['decision_rate'] = 0
        
        if stats['decisions_made'] > 0:
            stats['application_rate'] = (stats['decisions_applied'] / stats['decisions_made']) * 100
        else:
            stats['application_rate'] = 0
        
        # Add engine statistics
        stats['engine_history_size'] = len(self.engine.decision_history)
        
        return stats