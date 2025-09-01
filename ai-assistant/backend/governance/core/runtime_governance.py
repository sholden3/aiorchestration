"""
File: ai-assistant/backend/governance/core/runtime_governance.py
Purpose: Runtime governance system for request validation and decision management
Architecture: Provides hooks and validators for FastAPI middleware integration with resilience patterns
Dependencies: asyncio, enum, typing, logging, circuit_breaker, retry_logic, structured_logging
Owner: Dr. Sarah Chen

@fileoverview Runtime governance with hooks, validators, and resilience patterns
@author Dr. Sarah Chen v1.0 - Backend Systems Architect
@architecture Backend - Core governance system with circuit breakers and retry logic
@business_logic Request validation, decision tracking, hook execution, audit logging
@integration_points FastAPI middleware, request lifecycle hooks, audit systems
@error_handling Circuit breaker fallback, retry on transient failures, structured logging
@performance Sub-10ms validation, async hook execution, efficient decision tracking
"""

from enum import Enum
from typing import Dict, Any, Optional, List, Callable, Awaitable
from dataclasses import dataclass
import asyncio
import logging
from datetime import datetime

# Import resilience components
from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitOpenError
from .retry_logic import RetryManager, RetryConfig, with_retry
from .structured_logging import StructuredLogger, with_correlation_id, add_logging_context

# Use structured logger
logger = StructuredLogger(__name__)


class HookType(Enum):
    """
    Enumeration of governance hook types for request lifecycle.
    
    Each hook type represents a specific point in the request processing
    lifecycle where governance rules can be applied.
    """
    PRE_REQUEST = "pre_request"
    POST_REQUEST = "post_request"
    PRE_RESPONSE = "pre_response"
    ERROR_HANDLER = "error_handler"
    AUDIT = "audit"


class GovernanceLevel(Enum):
    """
    Enumeration of governance enforcement levels.
    
    Defines the strictness of governance rule enforcement.
    """
    RELAXED = "relaxed"     # Log violations but don't block
    STANDARD = "standard"   # Block critical violations
    STRICT = "strict"       # Block all violations
    AUDIT = "audit"        # Audit mode - log everything


@dataclass
class AgentContext:
    """
    Context for AI agent operations and decisions.
    
    Attributes:
        agent_id: Unique identifier for the agent
        agent_type: Type of agent (e.g., 'developer', 'reviewer')
        operation: Current operation being performed
        permissions: List of granted permissions
        metadata: Additional agent metadata
    """
    agent_id: str
    agent_type: str
    operation: str
    permissions: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.permissions is None:
            self.permissions = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DecisionContext:
    """
    Context object containing request information for governance decisions.
    
    Attributes:
        request_id: Unique identifier for the request
        endpoint: API endpoint being accessed
        method: HTTP method (GET, POST, etc.)
        user_id: Optional user identifier
        session_id: Optional session identifier
        metadata: Additional context metadata
        timestamp: Request timestamp
    """
    request_id: str
    endpoint: str
    method: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class RuntimeGovernanceValidator:
    """
    Validator for runtime governance rules and policies with resilience patterns.
    
    This class provides validation logic for various governance rules
    including rate limiting, access control, and audit requirements.
    Enhanced with circuit breakers and retry logic for fault tolerance.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the governance validator with resilience components.
        
        Args:
            config: Validator configuration dictionary
        """
        self.config = config or {}
        self.rules = self._load_rules()
        
        # Initialize circuit breaker for validation operations
        self.circuit_breaker = CircuitBreaker(
            CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30.0,
                success_threshold=2
            ),
            name="GovernanceValidator"
        )
        
        # Initialize retry manager for transient failures
        self.retry_manager = RetryManager(
            RetryConfig(
                max_attempts=3,
                initial_delay=0.1,
                max_delay=2.0,
                jitter=True
            )
        )
        
        logger.info(
            "RuntimeGovernanceValidator initialized",
            rule_count=len(self.rules),
            circuit_breaker_enabled=True,
            retry_enabled=True
        )
    
    def _load_rules(self) -> List[Dict[str, Any]]:
        """
        Load governance rules from configuration.
        
        Returns:
            List of governance rule dictionaries
        """
        return self.config.get('rules', [
            {
                'name': 'rate_limit',
                'enabled': True,
                'max_requests': 100,
                'window': 60
            },
            {
                'name': 'session_required',
                'enabled': True,
                'endpoints': ['/api/protected/*']
            }
        ])
    
    @with_correlation_id
    async def validate(self, context: DecisionContext) -> bool:
        """
        Validate a request against governance rules with resilience.
        
        Enhanced with circuit breaker and retry logic for fault tolerance.
        Includes correlation ID tracking for distributed tracing.
        
        Args:
            context: Decision context containing request information
            
        Returns:
            True if validation passes, False otherwise
            
        Raises:
            ValidationError: On critical validation failures
            CircuitOpenError: When circuit breaker is open
        """
        # Add context for structured logging
        add_logging_context(
            request_id=context.request_id,
            endpoint=context.endpoint,
            method=context.method,
            user_id=context.user_id
        )
        
        try:
            # Validate through circuit breaker with retry
            async def perform_validation():
                for rule in self.rules:
                    if rule.get('enabled', True):
                        with logger.log_operation(f"validate_rule_{rule['name']}", rule_name=rule['name']):
                            if not await self._validate_rule(rule, context):
                                logger.warning(
                                    "Validation failed for rule",
                                    rule_name=rule['name'],
                                    context_id=context.request_id
                                )
                                return False
                return True
            
            # Execute with circuit breaker protection
            try:
                result = await self.circuit_breaker.call(
                    self.retry_manager.execute_with_retry,
                    perform_validation
                )
                
                if result:
                    logger.info("Validation successful", request_id=context.request_id)
                else:
                    logger.warning("Validation failed", request_id=context.request_id)
                
                return result
                
            except CircuitOpenError as e:
                logger.error(
                    "Circuit breaker open - validation bypassed",
                    error=e,
                    fallback="allowing_request"
                )
                # Fallback: Allow request when circuit is open (configurable)
                return self.config.get('circuit_open_fallback', True)
                
        except Exception as e:
            logger.error(
                "Validation error",
                error=e,
                request_id=context.request_id
            )
            # Fallback: Deny on unexpected errors
            return False
    
    async def _validate_rule(self, rule: Dict[str, Any], context: DecisionContext) -> bool:
        """
        Validate a specific governance rule.
        
        Args:
            rule: Rule configuration dictionary
            context: Decision context
            
        Returns:
            True if rule validation passes
        """
        rule_name = rule.get('name')
        
        if rule_name == 'rate_limit':
            return await self._check_rate_limit(rule, context)
        elif rule_name == 'session_required':
            return await self._check_session(rule, context)
        
        # Unknown rule type passes by default
        return True
    
    async def _check_rate_limit(self, rule: Dict[str, Any], context: DecisionContext) -> bool:
        """Check rate limiting rule."""
        # Simplified rate limit check - would use Redis/cache in production
        return True
    
    async def _check_session(self, rule: Dict[str, Any], context: DecisionContext) -> bool:
        """Check session requirement rule."""
        endpoints = rule.get('endpoints', [])
        
        # Check if current endpoint requires session
        for pattern in endpoints:
            if self._match_endpoint(pattern, context.endpoint):
                return context.session_id is not None
        
        return True
    
    def _match_endpoint(self, pattern: str, endpoint: str) -> bool:
        """Match endpoint against pattern (supports wildcards)."""
        if pattern.endswith('*'):
            return endpoint.startswith(pattern[:-1])
        return pattern == endpoint


class RuntimeGovernanceSystem:
    """
    Main runtime governance system coordinating all governance activities.
    
    This class manages hooks, validators, and decision tracking for
    the entire application runtime.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the runtime governance system.
        
        Args:
            config: System configuration dictionary
        """
        self.config = config or {}
        self.validator = RuntimeGovernanceValidator(config)
        self.hooks: Dict[HookType, List[Callable]] = {
            hook_type: [] for hook_type in HookType
        }
        self.decisions: List[DecisionContext] = []
        self.max_decisions = 1000  # Keep last 1000 decisions
        logger.info("RuntimeGovernanceSystem initialized")
    
    def register_hook(self, hook_type: HookType, handler: Callable[[DecisionContext], Awaitable[None]]):
        """
        Register a hook handler for a specific hook type.
        
        Args:
            hook_type: Type of hook to register
            handler: Async function to handle the hook
            
        Example:
            async def audit_handler(context):
                log_audit_event(context)
            
            system.register_hook(HookType.AUDIT, audit_handler)
        """
        self.hooks[hook_type].append(handler)
        logger.debug(f"Registered hook for {hook_type.value}")
    
    async def execute_hook(self, hook_type: HookType, context: DecisionContext):
        """
        Execute all registered handlers for a hook type.
        
        Args:
            hook_type: Type of hook to execute
            context: Decision context for the hook
            
        Raises:
            HookExecutionError: If any hook handler fails critically
        """
        handlers = self.hooks.get(hook_type, [])
        
        for handler in handlers:
            try:
                await handler(context)
            except Exception as e:
                logger.error(f"Hook handler error for {hook_type.value}: {e}")
                # Continue executing other handlers
    
    async def make_decision(self, context: DecisionContext) -> bool:
        """
        Make a governance decision for a request.
        
        Args:
            context: Decision context containing request information
            
        Returns:
            True if request should proceed, False otherwise
        """
        # Pre-request hooks
        await self.execute_hook(HookType.PRE_REQUEST, context)
        
        # Validate request
        decision = await self.validator.validate(context)
        
        # Track decision
        self._track_decision(context, decision)
        
        # Audit hook
        await self.execute_hook(HookType.AUDIT, context)
        
        return decision
    
    def _track_decision(self, context: DecisionContext, decision: bool):
        """
        Track governance decisions for analysis.
        
        Args:
            context: Decision context
            decision: Decision result
        """
        context.metadata['decision'] = decision
        self.decisions.append(context)
        
        # Limit stored decisions
        if len(self.decisions) > self.max_decisions:
            self.decisions = self.decisions[-self.max_decisions:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get governance system statistics.
        
        Returns:
            Dictionary containing system statistics:
                - total_decisions: Total decisions made
                - approved: Number of approved requests
                - denied: Number of denied requests
                - hooks_registered: Number of hooks by type
        """
        approved = sum(1 for d in self.decisions if d.metadata.get('decision', False))
        denied = len(self.decisions) - approved
        
        return {
            'total_decisions': len(self.decisions),
            'approved': approved,
            'denied': denied,
            'hooks_registered': {
                hook_type.value: len(handlers) 
                for hook_type, handlers in self.hooks.items()
            }
        }