"""
Multi-Tenant AI Agent Orchestration System
Evidence-Based Implementation with Cross-Persona Validation
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging
from enum import Enum

from config import Config
from cache_manager import IntelligentCache
from database_manager import DatabaseManager
from persona_manager import PersonaManager, PersonaType
from base_patterns import OrchestrationResult

logger = logging.getLogger(__name__)

class TenantIsolationLevel(Enum):
    """Tenant isolation levels"""
    SHARED = "shared"  # Shared resources, isolated data
    ISOLATED = "isolated"  # Fully isolated resources
    DEDICATED = "dedicated"  # Dedicated infrastructure

@dataclass
class Tenant:
    """Tenant configuration and state"""
    id: str
    name: str
    isolation_level: TenantIsolationLevel
    max_agents: int = 5
    active_agents: Dict[str, 'AIAgent'] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AIAgent:
    """Individual AI agent instance"""
    id: str
    tenant_id: str
    persona_type: Optional[PersonaType]
    session_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    
class MultiTenantOrchestrator:
    """
    Orchestrates multiple AI agents across tenants
    Marcus: Evidence-based resource management
    Sarah: Validated AI agent coordination
    Emily: Clear tenant boundaries
    """
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.tenants: Dict[str, Tenant] = {}
        self.agents: Dict[str, AIAgent] = {}
        self.cache = IntelligentCache(
            hot_size_mb=self.config.systems.cache_hot_size_mb,
            warm_size_mb=self.config.systems.cache_warm_size_mb
        )
        self.database = DatabaseManager(self.config)
        self.persona_manager = PersonaManager()
        
        logger.info("Multi-tenant orchestrator initialized")
    
    async def create_tenant(
        self, 
        name: str, 
        isolation_level: TenantIsolationLevel = TenantIsolationLevel.SHARED
    ) -> OrchestrationResult[Tenant]:
        """
        Create new tenant with specified isolation
        Sarah: Validates tenant configuration
        Marcus: Allocates resources based on isolation level
        """
        try:
            tenant_id = str(uuid.uuid4())
            
            # Validate resources available
            if isolation_level == TenantIsolationLevel.DEDICATED:
                # Check if dedicated resources available
                if len(self.tenants) >= self.config.systems.max_tenants:
                    return OrchestrationResult.error(
                        "Maximum tenant limit reached",
                        code="TENANT_LIMIT"
                    )
            
            tenant = Tenant(
                id=tenant_id,
                name=name,
                isolation_level=isolation_level,
                max_agents=self._get_max_agents_for_level(isolation_level)
            )
            
            self.tenants[tenant_id] = tenant
            
            # Initialize tenant resources
            await self._initialize_tenant_resources(tenant)
            
            logger.info(f"Created tenant {tenant_id} with {isolation_level.value} isolation")
            return OrchestrationResult.ok(tenant, tenant_id=tenant_id)
            
        except Exception as e:
            logger.error(f"Failed to create tenant: {e}")
            return OrchestrationResult.error(str(e))
    
    async def create_agent(
        self,
        tenant_id: str,
        persona_type: Optional[PersonaType] = None
    ) -> OrchestrationResult[AIAgent]:
        """
        Create AI agent for tenant
        Emily: Validates agent limits
        Sarah: Assigns appropriate persona
        """
        try:
            # Validate tenant exists
            if tenant_id not in self.tenants:
                return OrchestrationResult.error(
                    "Tenant not found",
                    code="TENANT_NOT_FOUND"
                )
            
            tenant = self.tenants[tenant_id]
            
            # Check agent limit
            if len(tenant.active_agents) >= tenant.max_agents:
                return OrchestrationResult.error(
                    f"Agent limit ({tenant.max_agents}) reached",
                    code="AGENT_LIMIT"
                )
            
            # Create agent
            agent_id = str(uuid.uuid4())
            session_id = f"session_{agent_id[:8]}"
            
            agent = AIAgent(
                id=agent_id,
                tenant_id=tenant_id,
                persona_type=persona_type,
                session_id=session_id
            )
            
            # Register agent
            self.agents[agent_id] = agent
            tenant.active_agents[agent_id] = agent
            
            logger.info(f"Created agent {agent_id} for tenant {tenant_id}")
            return OrchestrationResult.ok(agent, agent_id=agent_id)
            
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            return OrchestrationResult.error(str(e))
    
    async def execute_task(
        self,
        agent_id: str,
        task: str,
        context: Optional[Dict] = None
    ) -> OrchestrationResult[Dict]:
        """
        Execute task through agent
        Marcus: Measures actual execution time
        Sarah: Validates task through persona
        """
        import time
        start_time = time.perf_counter()
        
        try:
            # Validate agent
            if agent_id not in self.agents:
                return OrchestrationResult.error(
                    "Agent not found",
                    code="AGENT_NOT_FOUND"
                )
            
            agent = self.agents[agent_id]
            agent.last_activity = datetime.now()
            
            # Update context
            if context:
                agent.context.update(context)
            
            # Check cache
            cache_key = self.cache.generate_key(task, agent.context)
            cached_result = await self.cache.get(cache_key)
            
            if cached_result:
                execution_time = (time.perf_counter() - start_time) * 1000
                logger.info(f"Cache hit for agent {agent_id}, execution: {execution_time:.2f}ms")
                return OrchestrationResult.ok(
                    cached_result,
                    cache_hit=True,
                    execution_ms=execution_time
                )
            
            # Execute through persona if assigned
            if agent.persona_type:
                result = await self._execute_with_persona(
                    agent.persona_type,
                    task,
                    agent.context
                )
            else:
                # Auto-suggest persona
                suggested = self.persona_manager.suggest_persona(task)
                if suggested:
                    agent.persona_type = suggested[0]
                    result = await self._execute_with_persona(
                        agent.persona_type,
                        task,
                        agent.context
                    )
                else:
                    result = {"response": "No suitable persona found", "success": False}
            
            # Cache result
            if result.get('success'):
                await self.cache.store(cache_key, result)
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.info(f"Task executed for agent {agent_id} in {execution_time:.2f}ms")
            
            return OrchestrationResult.ok(
                result,
                execution_ms=execution_time,
                persona_used=agent.persona_type.value if agent.persona_type else None
            )
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Task execution failed: {e}")
            return OrchestrationResult.error(
                str(e),
                execution_ms=execution_time
            )
    
    async def remove_agent(self, agent_id: str) -> OrchestrationResult[bool]:
        """Remove agent and cleanup resources"""
        try:
            if agent_id not in self.agents:
                return OrchestrationResult.error(
                    "Agent not found",
                    code="AGENT_NOT_FOUND"
                )
            
            agent = self.agents[agent_id]
            tenant = self.tenants.get(agent.tenant_id)
            
            # Remove from tenant
            if tenant and agent_id in tenant.active_agents:
                del tenant.active_agents[agent_id]
            
            # Remove agent
            del self.agents[agent_id]
            
            logger.info(f"Removed agent {agent_id}")
            return OrchestrationResult.ok(True)
            
        except Exception as e:
            logger.error(f"Failed to remove agent: {e}")
            return OrchestrationResult.error(str(e))
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get orchestrator metrics
        Marcus: Real measurements, not estimates
        """
        return {
            'total_tenants': len(self.tenants),
            'total_agents': len(self.agents),
            'agents_by_tenant': {
                tid: len(t.active_agents) 
                for tid, t in self.tenants.items()
            },
            'cache_metrics': self.cache.get_metrics(),
            'personas_active': [
                a.persona_type.value 
                for a in self.agents.values() 
                if a.persona_type
            ]
        }
    
    def _get_max_agents_for_level(self, level: TenantIsolationLevel) -> int:
        """Get max agents based on isolation level"""
        limits = {
            TenantIsolationLevel.SHARED: 3,
            TenantIsolationLevel.ISOLATED: 5,
            TenantIsolationLevel.DEDICATED: 10
        }
        return limits.get(level, 3)
    
    async def _initialize_tenant_resources(self, tenant: Tenant):
        """Initialize resources for tenant"""
        # In production, would create database schemas, cache namespaces, etc.
        logger.info(f"Initialized resources for tenant {tenant.id}")
    
    async def _execute_with_persona(
        self,
        persona_type: PersonaType,
        task: str,
        context: Dict
    ) -> Dict:
        """Execute task with specific persona"""
        # In production, would call actual Claude API
        return {
            'response': f"Mock {persona_type.value} response to: {task[:50]}",
            'success': True,
            'persona': persona_type.value,
            'context_used': bool(context)
        }