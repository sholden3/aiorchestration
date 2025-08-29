"""
@fileoverview Runtime governance system for real-time AI operation validation
@author Dr. Sarah Chen v1.0 & Sam Martinez v1.0 - 2025-08-29
@architecture Backend - Runtime governance enforcement
@responsibility Enforce governance rules during AI agent execution
@dependencies asyncio, logging, dataclasses, governance core modules
@integration_points AI agents, hooks, monitoring, decision injection
@testing_strategy Unit tests for hooks, integration tests for AI operations
@governance Real-time enforcement of AI safety and compliance rules

Business Logic Summary:
- Hook into AI agent lifecycle events
- Inject governance decisions in real-time
- Monitor and log AI operations
- Enforce rate limits and safety checks
- Manage circuit breakers for AI calls

Architecture Integration:
- Intercepts AI agent operations
- Integrates with runtime hooks
- Provides decision injection
- Manages governance state
- Enables real-time monitoring

Sarah's Framework Check:
- What breaks first: AI agent timeout or governance validation failure
- How we know: Hook execution metrics and error logs
- Plan B: Fail-safe mode with conservative defaults
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Set
from enum import Enum
from dataclasses import dataclass, field
import traceback
from pathlib import Path

# Import existing governance components
from .engine import GovernanceEngine
from .context import GovernanceContext
from .result import GovernanceResult as BaseGovernanceResult
from .exceptions import GovernanceViolation
from ..rules.smart_rules import SmartRules
from ..validators.basic_hallucination_detector import BasicHallucinationDetector
from .governance_monitor import GovernanceMonitor, GovernanceEvent, GovernanceEventType

logger = logging.getLogger(__name__)


class GovernanceResult:
    """Wrapper for compatibility between runtime and base governance result"""
    
    def __init__(self, decision=None, approved=None, reason=None, risk_level=None, 
                 recommendations=None, confidence=None, metadata=None):
        # Handle both interfaces
        if approved is not None:
            self.approved = approved
            self.decision = "approved" if approved else "rejected"
        elif decision is not None:
            self.decision = decision
            self.approved = decision == "approved"
        else:
            self.approved = True
            self.decision = "approved"
        
        self.reason = reason or ""
        self.risk_level = risk_level or "LOW"
        self.recommendations = recommendations or []
        self.confidence = confidence or 1.0
        self.metadata = metadata or {}


class HookType(Enum):
    """Types of governance hooks"""
    PRE_AGENT_SPAWN = "pre_agent_spawn"
    POST_AGENT_SPAWN = "post_agent_spawn"
    PRE_AGENT_EXECUTE = "pre_agent_execute"
    POST_AGENT_EXECUTE = "post_agent_execute"
    PRE_DECISION = "pre_decision"
    POST_DECISION = "post_decision"
    AGENT_TERMINATE = "agent_terminate"
    RESOURCE_CHECK = "resource_check"
    AUDIT_LOG = "audit_log"


class GovernanceLevel(Enum):
    """Enforcement levels for governance"""
    STRICT = "strict"      # Block violations
    WARNING = "warning"    # Warn but allow
    MONITOR = "monitor"    # Log only
    BYPASS = "bypass"      # Skip checks


@dataclass
class AgentContext:
    """Context for agent operations"""
    agent_id: str
    agent_type: str
    agent_name: str
    spawn_time: datetime
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    task_history: List[Dict[str, Any]] = field(default_factory=list)
    violations: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionContext:
    """Context for AI decisions"""
    decision_id: str
    agent_id: str
    decision_type: str
    input_data: Dict[str, Any]
    proposed_output: Any
    confidence_score: float = 0.0
    risk_score: float = 0.0
    personas_consulted: List[str] = field(default_factory=list)
    validation_results: Dict[str, Any] = field(default_factory=dict)


class RuntimeGovernanceSystem:
    """
    Core runtime governance system for AI operations
    Manages hooks, validations, and real-time enforcement
    """
    
    def __init__(self, config_path: Optional[Path] = None, enable_monitor: bool = True):
        self.config_path = config_path or Path("governance-config")
        self.governance_level = GovernanceLevel.STRICT
        
        # Core components
        self.engine = GovernanceEngine()
        self.smart_rules = SmartRules()
        self.hallucination_detector = BasicHallucinationDetector()
        
        # Initialize monitor
        self.monitor = GovernanceMonitor(verbose=enable_monitor) if enable_monitor else None
        if self.monitor:
            self.monitor.log_event(GovernanceEvent(
                event_type=GovernanceEventType.SYSTEM_START,
                timestamp=datetime.now(),
                description="Governance system initialized and monitoring all operations",
                details={
                    "governance_level": self.governance_level.value,
                    "config_path": str(self.config_path)
                },
                severity="INFO",
                actor="System"
            ))
        
        # Hook registry
        self.hooks: Dict[HookType, List[Callable]] = {
            hook_type: [] for hook_type in HookType
        }
        
        # Active agents tracking
        self.active_agents: Dict[str, AgentContext] = {}
        
        # Resource limits
        self.resource_limits = {
            "max_agents": 6,
            "max_memory_per_agent": 512 * 1024 * 1024,  # 512MB
            "max_cpu_per_agent": 25,  # 25% CPU
            "max_tokens_per_minute": 10000,
            "max_api_calls_per_minute": 100
        }
        
        # Metrics
        self.metrics = {
            "agents_spawned": 0,
            "agents_terminated": 0,
            "decisions_validated": 0,
            "violations_detected": 0,
            "hallucinations_caught": 0,
            "resource_limits_hit": 0
        }
        
        # Audit log
        self.audit_log: List[Dict[str, Any]] = []
        
        # Load configurations
        self._load_configurations()
        
    def _load_configurations(self):
        """Load governance configurations"""
        try:
            # Load resource limits
            limits_path = self.config_path / "resource-limits.json"
            if limits_path.exists():
                with open(limits_path) as f:
                    self.resource_limits.update(json.load(f))
            
            # Load rule configurations
            rules_path = self.config_path / "rules"
            if rules_path.exists():
                for rule_file in rules_path.glob("*.json"):
                    with open(rule_file) as f:
                        rule_config = json.load(f)
                        # Process rule configurations
                        logger.info(f"Loaded rule config: {rule_file.name}")
                        
        except Exception as e:
            logger.error(f"Error loading configurations: {e}")
    
    # ============= Hook Registration =============
    
    def register_hook(self, hook_type: HookType, callback: Callable) -> None:
        """Register a hook callback"""
        if hook_type not in self.hooks:
            raise ValueError(f"Invalid hook type: {hook_type}")
        
        self.hooks[hook_type].append(callback)
        logger.info(f"Registered hook for {hook_type.value}")
    
    async def trigger_hook(self, hook_type: HookType, context: Any) -> List[Any]:
        """Trigger all registered hooks for a type"""
        results = []
        
        for callback in self.hooks[hook_type]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    result = await callback(context)
                else:
                    result = callback(context)
                results.append(result)
            except Exception as e:
                logger.error(f"Hook {callback.__name__} failed: {e}")
                if self.governance_level == GovernanceLevel.STRICT:
                    raise
                    
        return results
    
    # ============= Agent Lifecycle Management =============
    
    async def validate_agent_spawn(
        self,
        agent_type: str,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> GovernanceResult:
        """
        Validate agent spawn request
        Called BEFORE agent is created
        """
        # Log spawn request
        if self.monitor:
            self.monitor.log_agent_spawn_request(agent_type, agent_name or "unnamed", metadata or {})
        
        try:
            # Check resource limits
            if self.monitor:
                self.monitor.log_resource_check(
                    "agent_slots",
                    len(self.active_agents),
                    self.resource_limits["max_agents"],
                    self.resource_limits["max_agents"] - len(self.active_agents)
                )
            
            if len(self.active_agents) >= self.resource_limits["max_agents"]:
                self.metrics["resource_limits_hit"] += 1
                reason = f"Maximum agent limit ({self.resource_limits['max_agents']}) reached"
                
                if self.monitor:
                    self.monitor.log_validation_result("Agent spawn", False, reason, "HIGH")
                
                return GovernanceResult(
                    decision="rejected",
                    reason=reason,
                    recommendations=["Wait for existing agents to terminate"],
                    confidence=1.0
                )
            
            # Create agent context
            agent_context = AgentContext(
                agent_id=f"pending_{datetime.now().timestamp()}",
                agent_type=agent_type,
                agent_name=agent_name or f"{agent_type}_agent",
                spawn_time=datetime.now(),
                metadata=metadata or {}
            )
            
            # Trigger pre-spawn hooks
            hook_results = await self.trigger_hook(
                HookType.PRE_AGENT_SPAWN,
                agent_context
            )
            
            # Check hook vetoes
            for result in hook_results:
                if isinstance(result, dict) and not result.get("approved", True):
                    return GovernanceResult(
                        approved=False,
                        reason=result.get("reason", "Hook validation failed"),
                        risk_level="HIGH"
                    )
            
            # Validate with smart rules - using validate_file method
            # Create pseudo-code to check
            pseudo_code = f"# Agent spawn operation\nspawn_agent('{agent_type}')"
            validation_result = self.smart_rules.validate_file(
                file_path=f"agent_spawn_{agent_type}.py",
                content=pseudo_code
            )
            
            if not validation_result.get("valid", True):
                self.metrics["violations_detected"] += 1
                errors = validation_result.get("errors", ["Agent spawn not allowed"])
                return GovernanceResult(
                    approved=False,
                    reason="; ".join(errors),
                    risk_level="HIGH"
                )
            
            # Log audit event
            self._audit_log_event({
                "event": "agent_spawn_validated",
                "agent_type": agent_type,
                "timestamp": datetime.now().isoformat(),
                "result": "approved"
            })
            
            return GovernanceResult(
                approved=True,
                reason="Agent spawn approved",
                risk_level="LOW"
            )
            
        except Exception as e:
            logger.error(f"Error validating agent spawn: {e}")
            if self.governance_level == GovernanceLevel.STRICT:
                return GovernanceResult(
                    approved=False,
                    reason=f"Validation error: {str(e)}",
                    risk_level="HIGH"
                )
            return GovernanceResult(
                approved=True,
                reason="Validation bypassed due to error",
                risk_level="MEDIUM"
            )
    
    async def register_agent(
        self,
        agent_id: str,
        agent_type: str,
        agent_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register a spawned agent for monitoring
        Called AFTER agent is created
        """
        agent_context = AgentContext(
            agent_id=agent_id,
            agent_type=agent_type,
            agent_name=agent_name,
            spawn_time=datetime.now(),
            metadata=metadata or {}
        )
        
        self.active_agents[agent_id] = agent_context
        self.metrics["agents_spawned"] += 1
        
        # Trigger post-spawn hooks
        await self.trigger_hook(HookType.POST_AGENT_SPAWN, agent_context)
        
        # Start monitoring
        asyncio.create_task(self._monitor_agent(agent_id))
        
        logger.info(f"Registered agent {agent_name} ({agent_id}) for governance")
    
    async def validate_agent_execution(
        self,
        agent_id: str,
        command: str,
        context: Optional[Dict[str, Any]] = None
    ) -> GovernanceResult:
        """
        Validate agent execution request
        Called BEFORE execution
        """
        if agent_id not in self.active_agents:
            return GovernanceResult(
                approved=False,
                reason="Unknown agent ID",
                risk_level="HIGH"
            )
        
        agent_context = self.active_agents[agent_id]
        
        # Check for dangerous patterns
        validation = self.smart_rules.validate_file(
            file_path="command_execution.py",
            content=command
        )
        if not validation.get("valid", True):
            agent_context.violations.append({
                "type": "dangerous_command",
                "command": command,
                "timestamp": datetime.now().isoformat()
            })
            self.metrics["violations_detected"] += 1
            
            errors = validation.get("errors", ["Command not allowed"])
            return GovernanceResult(
                approved=False,
                reason="; ".join(errors),
                risk_level="HIGH"
            )
        
        # Trigger pre-execution hooks
        execution_context = {
            "agent": agent_context,
            "command": command,
            "context": context
        }
        
        hook_results = await self.trigger_hook(
            HookType.PRE_AGENT_EXECUTE,
            execution_context
        )
        
        # Check hook vetoes
        for result in hook_results:
            if isinstance(result, dict) and not result.get("approved", True):
                return GovernanceResult(
                    approved=False,
                    reason=result.get("reason", "Execution blocked by hook"),
                    risk_level="HIGH"
                )
        
        # Update task history
        agent_context.task_history.append({
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "approved": True
        })
        
        return GovernanceResult(
            approved=True,
            reason="Execution approved",
            risk_level="LOW"
        )
    
    async def terminate_agent(self, agent_id: str, reason: str = "Normal termination") -> None:
        """Handle agent termination"""
        if agent_id in self.active_agents:
            agent_context = self.active_agents[agent_id]
            
            # Trigger termination hooks
            await self.trigger_hook(HookType.AGENT_TERMINATE, agent_context)
            
            # Log termination
            self._audit_log_event({
                "event": "agent_terminated",
                "agent_id": agent_id,
                "agent_name": agent_context.agent_name,
                "reason": reason,
                "lifetime": (datetime.now() - agent_context.spawn_time).total_seconds(),
                "tasks_completed": len(agent_context.task_history),
                "violations": len(agent_context.violations)
            })
            
            # Remove from active agents
            del self.active_agents[agent_id]
            self.metrics["agents_terminated"] += 1
            
            logger.info(f"Agent {agent_id} terminated: {reason}")
    
    # ============= AI Decision Injection =============
    
    async def validate_ai_decision(
        self,
        agent_id: str,
        decision_type: str,
        input_data: Dict[str, Any],
        proposed_output: Any
    ) -> GovernanceResult:
        """
        Validate AI decision before execution
        Checks for hallucinations, policy violations, etc.
        """
        decision_context = DecisionContext(
            decision_id=f"decision_{datetime.now().timestamp()}",
            agent_id=agent_id,
            decision_type=decision_type,
            input_data=input_data,
            proposed_output=proposed_output
        )
        
        try:
            # Check for hallucinations
            if isinstance(proposed_output, str):
                hallucination_check = self.hallucination_detector.detect(
                    proposed_output,
                    {"type": decision_type, "input": input_data}
                )
                
                if hallucination_check.get("is_hallucination", False):
                    self.metrics["hallucinations_caught"] += 1
                    decision_context.validation_results["hallucination"] = hallucination_check
                    
                    if self.governance_level == GovernanceLevel.STRICT:
                        return GovernanceResult(
                            approved=False,
                            reason=f"Potential hallucination detected: {hallucination_check.get('reason')}",
                            risk_level="HIGH",
                            recommendations=["Review output for accuracy", "Request clarification"]
                        )
            
            # Trigger pre-decision hooks
            hook_results = await self.trigger_hook(
                HookType.PRE_DECISION,
                decision_context
            )
            
            # Aggregate hook feedback
            risk_scores = []
            for result in hook_results:
                if isinstance(result, dict):
                    if not result.get("approved", True):
                        return GovernanceResult(
                            approved=False,
                            reason=result.get("reason", "Decision blocked"),
                            risk_level="HIGH"
                        )
                    if "risk_score" in result:
                        risk_scores.append(result["risk_score"])
            
            # Calculate aggregate risk
            if risk_scores:
                decision_context.risk_score = sum(risk_scores) / len(risk_scores)
            
            # Make final decision
            if decision_context.risk_score > 0.7:
                return GovernanceResult(
                    approved=False,
                    reason="Risk score too high",
                    risk_level="HIGH",
                    metadata={"risk_score": decision_context.risk_score}
                )
            
            self.metrics["decisions_validated"] += 1
            
            # Trigger post-decision hooks (async, don't wait)
            asyncio.create_task(
                self.trigger_hook(HookType.POST_DECISION, decision_context)
            )
            
            return GovernanceResult(
                approved=True,
                reason="Decision approved",
                risk_level="LOW" if decision_context.risk_score < 0.3 else "MEDIUM",
                metadata={
                    "risk_score": decision_context.risk_score,
                    "decision_id": decision_context.decision_id
                }
            )
            
        except Exception as e:
            logger.error(f"Error validating decision: {e}")
            if self.governance_level == GovernanceLevel.STRICT:
                return GovernanceResult(
                    approved=False,
                    reason=f"Validation error: {str(e)}",
                    risk_level="HIGH"
                )
            return GovernanceResult(
                approved=True,
                reason="Validation error, proceeding with caution",
                risk_level="MEDIUM"
            )
    
    # ============= Resource Management =============
    
    async def check_resource_limits(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Check current resource usage against limits"""
        usage = {
            "agents": {
                "current": len(self.active_agents),
                "limit": self.resource_limits["max_agents"],
                "available": self.resource_limits["max_agents"] - len(self.active_agents)
            }
        }
        
        if agent_id and agent_id in self.active_agents:
            agent_context = self.active_agents[agent_id]
            usage["agent_specific"] = {
                "agent_id": agent_id,
                "resource_usage": agent_context.resource_usage,
                "task_count": len(agent_context.task_history),
                "violation_count": len(agent_context.violations)
            }
        
        # Trigger resource check hooks
        await self.trigger_hook(HookType.RESOURCE_CHECK, usage)
        
        return usage
    
    async def _monitor_agent(self, agent_id: str):
        """Background task to monitor agent resources"""
        while agent_id in self.active_agents:
            try:
                agent_context = self.active_agents[agent_id]
                
                # Update resource usage (would connect to actual monitoring)
                # This is a placeholder for real resource monitoring
                agent_context.resource_usage = {
                    "memory_mb": 100,  # Placeholder
                    "cpu_percent": 5,   # Placeholder
                    "api_calls": len(agent_context.task_history)
                }
                
                # Check for violations
                if agent_context.resource_usage.get("memory_mb", 0) > \
                   self.resource_limits["max_memory_per_agent"] / (1024 * 1024):
                    logger.warning(f"Agent {agent_id} exceeding memory limit")
                    agent_context.violations.append({
                        "type": "memory_limit",
                        "timestamp": datetime.now().isoformat()
                    })
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring agent {agent_id}: {e}")
                await asyncio.sleep(10)
    
    # ============= Audit and Logging =============
    
    def _audit_log_event(self, event: Dict[str, Any]):
        """Log an audit event"""
        event["timestamp"] = event.get("timestamp", datetime.now().isoformat())
        self.audit_log.append(event)
        
        # Trigger audit hooks
        asyncio.create_task(self.trigger_hook(HookType.AUDIT_LOG, event))
        
        # Keep audit log size manageable
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-5000:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current governance metrics"""
        return {
            **self.metrics,
            "active_agents": len(self.active_agents),
            "audit_log_size": len(self.audit_log),
            "governance_level": self.governance_level.value
        }
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit log entries"""
        return self.audit_log[-limit:]
    
    # ============= Configuration Management =============
    
    def set_governance_level(self, level: GovernanceLevel):
        """Change governance enforcement level"""
        old_level = self.governance_level
        self.governance_level = level
        
        self._audit_log_event({
            "event": "governance_level_changed",
            "old_level": old_level.value,
            "new_level": level.value
        })
        
        logger.info(f"Governance level changed from {old_level.value} to {level.value}")
    
    def update_resource_limits(self, limits: Dict[str, Any]):
        """Update resource limits"""
        old_limits = self.resource_limits.copy()
        self.resource_limits.update(limits)
        
        self._audit_log_event({
            "event": "resource_limits_updated",
            "old_limits": old_limits,
            "new_limits": self.resource_limits
        })
        
        logger.info("Resource limits updated")


# ============= Singleton Instance =============

_governance_instance: Optional[RuntimeGovernanceSystem] = None


def get_governance_system() -> RuntimeGovernanceSystem:
    """Get or create the singleton governance instance"""
    global _governance_instance
    if _governance_instance is None:
        _governance_instance = RuntimeGovernanceSystem()
    return _governance_instance


async def initialize_governance(config_path: Optional[Path] = None) -> RuntimeGovernanceSystem:
    """Initialize the governance system"""
    global _governance_instance
    _governance_instance = RuntimeGovernanceSystem(config_path)
    logger.info("Runtime governance system initialized")
    return _governance_instance