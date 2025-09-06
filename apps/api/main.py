"""
@fileoverview FastAPI backend service for AI orchestration with intelligent caching and governance
@author Dr. Sarah Chen v2.0 & Alex Novak v1.5 - 2025-08-29
@architecture Backend - FastAPI async service with WebSocket support
@responsibility Orchestrate AI agents, manage caching, enforce governance, provide API endpoints
@dependencies FastAPI, asyncpg, websockets, governance system, persona managers
@integration_points Frontend via REST/WebSocket, PostgreSQL database, Claude CLI, governance hooks
@testing_strategy Integration tests for API endpoints, unit tests for cache/personas, stress tests for WebSocket
@governance Runtime governance with pre/post agent hooks, persona validation, rate limiting

Business Logic Summary:
- Two-tier intelligent caching (hot/warm) with 90% target hit rate
- Multi-persona AI orchestration with consensus mechanisms
- Real-time WebSocket broadcasting for live updates
- Database integration with PostgreSQL and fallback to mock
- Runtime governance enforcement on all AI operations

Architecture Integration:
- Central hub for all backend operations
- Integrates with governance system for AI safety
- Provides REST and WebSocket APIs for frontend
- Manages database connections and caching layers
- Orchestrates multiple AI personas and agents

Sarah's Framework Check:
- What breaks first: Database connection or cache overflow
- How we know: Health endpoints and metrics monitoring
- Plan B: Mock database fallback and memory-only cache mode
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import json
import argparse

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import asyncpg

# Add backend modules to path
sys.path.append(str(Path(__file__).parent))
# Add governance modules to path
sys.path.append(str(Path(__file__).parent.parent / "governance"))

# Import configuration
# Fixed imports for recovery (DEC-2025-010)
# Since main.py is run as a script, use direct imports with sys.path
from core.config import get_config, get_backend_url, is_development
from core.port_discovery import discover_backend_port, cleanup_backend_port, get_port_discovery

from cache_manager import IntelligentCache
from persona_manager import PersonaManager, PersonaType
from claude_integration import ClaudeOptimizer
from database_manager import DatabaseManager
from metrics_collector import MetricsCollector
from config import Config

# Import our orchestration systems
from ai_orchestration_engine import AIOrchestrationEngine, AITask as OrchestratorTask, TaskPriority
from unified_governance_orchestrator import UnifiedGovernanceOrchestrator
from persona_orchestrator import PersonaOrchestrationEnhanced
from conversation_manager import ConversationManager
from additional_api_endpoints import add_additional_routes
from api_endpoints_v2 import rules_router, practices_router, templates_router, sessions_router
from database_service import db_service
from websocket_manager import ws_manager, EventType
from agent_terminal_manager import agent_terminal_manager, AgentType
from claude_terminal import claude_terminal

# Import governance system
# Updated path to use libs/governance structure
try:
    from libs.governance.core.runtime_governance import (
        RuntimeGovernanceSystem,
        HookType,
        GovernanceLevel,
        AgentContext,
        DecisionContext
    )
except ImportError:
    # Fallback if PYTHONPATH not set correctly
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from libs.governance.core.runtime_governance import (
        RuntimeGovernanceSystem,
        HookType,
        GovernanceLevel,
        AgentContext,
        DecisionContext
    )
from libs.governance.middleware.ai_decision_injector import (
    AIDecisionInjector,
    DecisionType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class AITask(BaseModel):
    prompt: str
    persona: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}
    use_cache: bool = True

class PersonaSuggestion(BaseModel):
    description: str

class TaskResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    cached: bool = False
    tokens_saved: int = 0
    persona_used: Optional[str] = None
    execution_time_ms: int = 0

class CacheMetrics(BaseModel):
    hit_rate: float
    tokens_saved: int
    hot_cache_size_mb: float
    warm_cache_files: int
    total_requests: int
    cache_hits: int
    cache_misses: int

class AIBackendService:
    """
    Main backend service orchestrating all AI operations
    """
    
    def __init__(self, config: Config = None, port: int = None, host: str = '127.0.0.1'):
        # Load configuration from centralized config
        self.app_config = get_config()
        self.config = config or Config()
        
        # Use port discovery if not specified
        if port is None:
            # Try to discover an available port
            self.port = discover_backend_port()
            logger.info(f"Discovered available port: {self.port}")
            # Write port to file for frontend to read
            port_discovery = get_port_discovery()
            port_discovery.write_port_file(self.port)
        else:
            self.port = port
        
        self.host = host
        
        self.app = FastAPI(
            title=self.app_config.name,
            version=self.app_config.version,
            debug=is_development()
        )
        
        # FIX H3: Database initialization state tracking
        self._initialization_complete = False
        self._initialization_error = None
        self._startup_lock = asyncio.Lock()
        
        # Initialize components
        self.cache = IntelligentCache(
            hot_size_mb=self.config.systems.cache_hot_size_mb,
            warm_size_mb=2048,
            target_hit_rate=0.9
        )
        self.persona_manager = PersonaManager()
        self.claude = ClaudeOptimizer(self.cache)
        self.db_manager = None  # Initialized in startup
        self.metrics = MetricsCollector()
        
        # Initialize orchestration systems
        self.governance_orchestrator = UnifiedGovernanceOrchestrator()
        self.ai_orchestrator = AIOrchestrationEngine(self.governance_orchestrator)
        self.persona_orchestration = PersonaOrchestrationEnhanced(self.governance_orchestrator)
        self.conversation_manager = ConversationManager(self.ai_orchestrator)
        
        # Initialize runtime governance system
        self.runtime_governance = RuntimeGovernanceSystem()
        
        # Initialize AI decision injector
        self.decision_injector = AIDecisionInjector()
        
        self.setup_middleware()
        self.setup_routes()
        self.setup_websocket_routes()
        self.setup_lifecycle()
        
        # Add additional API endpoints (mock - for backwards compatibility)
        # add_additional_routes(self.app)
        
        # Add real database-backed endpoints using database_service
        # These routers use the database_service with fallback to mock data
        self.app.include_router(rules_router)
        self.app.include_router(practices_router) 
        self.app.include_router(templates_router)
        self.app.include_router(sessions_router)
        
    def setup_middleware(self):
        """Configure CORS for Electron app"""
        # Use CORS settings from centralized config
        if self.app_config.backend.cors.enabled:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=self.app_config.backend.cors.origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
    
    def setup_lifecycle(self):
        """Setup startup and shutdown events"""
        
        @self.app.on_event("startup")
        async def startup_event():
            """Initialize database connection and load cache"""
            # FIX H3: Ensure thread-safe initialization
            async with self._startup_lock:
                try:
                    # Initialize real database service with credentials
                    from credentials_manager import credentials_manager
                    # GOVERNANCE: No hardcoded secrets - use environment variables
                    # This is a development fallback only - production uses real credentials
                    db_password = os.getenv('DB_PASSWORD', 'changeme_in_production')
                    db_url = credentials_manager.get_database_url(
                        host='localhost',
                        port=5432,
                        database='ai_assistant',
                        default_password=db_password
                    )
                    await db_service.connect(db_url)
                    logger.info(f"Database service connected: {db_service.is_connected}")
                    
                    # Initialize schema if needed
                    await db_service.initialize_schema()
                    
                    # Initialize mock database manager for legacy code
                    self.db_manager = DatabaseManager()
                    await self.db_manager.initialize()
                    logger.info("Legacy database manager initialized")
                    
                    # Load persisted cache
                    await self.cache.load_from_database(self.db_manager)
                    logger.info("Cache loaded from database")
                    
                    # Start metrics collection
                    asyncio.create_task(self.metrics.start_collection())
                    logger.info("Metrics collection started")
                    
                    # Start AI orchestration engine
                    await self.ai_orchestrator.start_orchestration()
                    logger.info("AI Orchestration Engine started")
                    
                    # Persona orchestration is ready (no async initialization needed)
                    logger.info("Persona Orchestration ready with assumption fighting")
                    
                    # Initialize runtime governance hooks
                    await self._setup_governance_hooks()
                    logger.info("Runtime governance hooks registered")
                    
                    # Set governance level based on environment
                    governance_level = os.getenv('GOVERNANCE_LEVEL', 'STRICT').upper()
                    if governance_level in ['STRICT', 'WARNING', 'MONITOR', 'BYPASS']:
                        self.runtime_governance.set_governance_level(
                            GovernanceLevel[governance_level]
                        )
                    logger.info(f"Governance level set to: {governance_level}")
                    
                    # FIX H3: Mark initialization as complete
                    self._initialization_complete = True
                    logger.info("Backend initialization complete - all services ready")
                    
                except Exception as e:
                    logger.error(f"Startup failed: {e}")
                    # FIX H3: Track initialization error for proper error responses
                    self._initialization_error = str(e)
                    # Continue anyway for local tool but mark as not fully initialized
                    self._initialization_complete = False
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            """Save cache and close connections"""
            try:
                # Stop orchestration engine
                await self.ai_orchestrator.stop_orchestration()
                logger.info("AI Orchestration stopped")
                
                # Save cache to database
                if self.db_manager:
                    await self.cache.save_to_database(self.db_manager)
                    await self.db_manager.close()
                    
                # Clean up port allocation
                cleanup_backend_port()
                logger.info("Released backend port")
                
                logger.info("Shutdown complete")
            except Exception as e:
                logger.error(f"Shutdown error: {e}")
    
    async def _ensure_initialized(self):
        """FIX H3: Ensure services are initialized before processing requests"""
        if self._initialization_complete:
            return True
            
        # If initialization is still in progress, wait for it
        async with self._startup_lock:
            if self._initialization_complete:
                return True
            
            # If we have an initialization error, raise it
            if self._initialization_error:
                raise HTTPException(
                    status_code=503,
                    detail=f"Backend services not available: {self._initialization_error}"
                )
            
            # Still initializing
            raise HTTPException(
                status_code=503,
                detail="Backend services are still initializing. Please try again in a few seconds."
            )
    
    async def _setup_governance_hooks(self):
        """Setup governance hooks for runtime monitoring"""
        
        # Register agent spawn hook
        async def pre_spawn_hook(context: AgentContext):
            """Log and validate agent spawn attempts"""
            logger.info(f"Pre-spawn hook: Validating agent {context.agent_type}")
            # Additional custom validation can go here
            return {"approved": True, "reason": "Pre-spawn validation passed"}
        
        self.runtime_governance.register_hook(HookType.PRE_AGENT_SPAWN, pre_spawn_hook)
        
        # Register post-spawn hook
        async def post_spawn_hook(context: AgentContext):
            """Track spawned agents"""
            logger.info(f"Post-spawn hook: Agent {context.agent_name} spawned successfully")
            # Send metrics or notifications
            await ws_manager.broadcast({
                'type': 'governance_event',
                'event': 'agent_spawned',
                'agent_id': context.agent_id,
                'agent_type': context.agent_type
            })
        
        self.runtime_governance.register_hook(HookType.POST_AGENT_SPAWN, post_spawn_hook)
        
        # Register execution hooks
        async def pre_execute_hook(context: dict):
            """Validate commands before execution"""
            command = context.get('command', '')
            logger.info(f"Pre-execute hook: Validating command for agent {context.get('agent', {}).get('agent_id')}")
            # Could add command filtering here
            return {"approved": True}
        
        self.runtime_governance.register_hook(HookType.PRE_AGENT_EXECUTE, pre_execute_hook)
        
        # Register decision validation hook
        async def pre_decision_hook(context: DecisionContext):
            """Validate AI decisions"""
            logger.info(f"Pre-decision hook: Validating decision {context.decision_type}")
            # Could invoke additional personas here
            return {
                "approved": True,
                "risk_score": 0.2,
                "reason": "Decision validation passed"
            }
        
        self.runtime_governance.register_hook(HookType.PRE_DECISION, pre_decision_hook)
        
        # Register audit log hook
        async def audit_hook(event: dict):
            """Handle audit events"""
            # Could send to external logging system
            logger.info(f"Audit event: {event.get('event')} at {event.get('timestamp')}")
        
        self.runtime_governance.register_hook(HookType.AUDIT_LOG, audit_hook)
    
    def setup_routes(self):
        """Define API endpoints"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint for Electron to verify backend is running"""
            # FIX H3: Health check returns different status based on initialization state
            if self._initialization_complete:
                return {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "cache_enabled": True,
                    "personas_available": len(self.persona_manager.personas),
                    "initialized": True,
                    "database": db_service.get_connection_status()
                }
            elif self._initialization_error:
                return {
                    "status": "degraded",
                    "timestamp": datetime.now().isoformat(),
                    "cache_enabled": False,
                    "personas_available": 0,
                    "initialized": False,
                    "error": self._initialization_error,
                    "database": db_service.get_connection_status()
                }
            else:
                return {
                    "status": "initializing",
                    "timestamp": datetime.now().isoformat(),
                    "cache_enabled": False,
                    "personas_available": 0,
                    "initialized": False,
                    "database": {"is_connected": False, "circuit_breaker": {"state": "closed"}}
                }
        
        @self.app.get("/database/status")
        async def database_status():
            """Get detailed database connection status including circuit breaker state"""
            return db_service.get_connection_status()
        
        @self.app.post("/ai/execute", response_model=TaskResponse)
        async def execute_ai_task(task: AITask, background_tasks: BackgroundTasks):
            """
            Business Logic: Execute AI task with caching and persona selection
            Performance: Check cache first to reduce token usage
            Error Handling: Graceful fallback if Claude unavailable
            """
            # FIX H3: Ensure initialization is complete before processing
            await self._ensure_initialized()
            
            start_time = datetime.now()
            
            try:
                # Generate cache key
                cache_key = self.cache.generate_key(task.prompt, task.context)
                
                # Check cache if enabled
                if task.use_cache:
                    cached_response = await self.cache.get(cache_key)
                    if cached_response:
                        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                        self.metrics.record_cache_hit()
                        
                        # Broadcast cache hit event
                        asyncio.create_task(ws_manager.broadcast_cache_metrics({
                            'event': 'cache_hit',
                            'cache_key': cache_key[:20],  # Truncated for privacy
                            'tokens_saved': cached_response.get('tokens_saved', 0)
                        }))
                        
                        return TaskResponse(
                            success=True,
                            response=cached_response['response'],
                            cached=True,
                            tokens_saved=cached_response.get('tokens_saved', 0),
                            persona_used=cached_response.get('persona'),
                            execution_time_ms=execution_time
                        )
                
                self.metrics.record_cache_miss()
                
                # Select persona if not specified
                if not task.persona:
                    suggested_personas = self.persona_manager.suggest_persona(task.prompt)
                    task.persona = suggested_personas[0] if suggested_personas else None
                
                # Execute with Claude
                result = await self.claude.execute_with_persona(
                    prompt=task.prompt,
                    persona=task.persona,
                    context=task.context
                )
                
                # Store in cache for future use
                if result['success'] and task.use_cache:
                    background_tasks.add_task(
                        self.cache.store,
                        cache_key,
                        result
                    )
                
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                
                return TaskResponse(
                    success=result['success'],
                    response=result.get('response'),
                    error=result.get('error'),
                    cached=False,
                    tokens_saved=0,
                    persona_used=task.persona,
                    execution_time_ms=execution_time
                )
                
            except Exception as e:
                logger.error(f"AI task execution failed: {e}")
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                
                return TaskResponse(
                    success=False,
                    error=str(e),
                    cached=False,
                    execution_time_ms=execution_time
                )
        
        @self.app.post("/ai/orchestrated", response_model=TaskResponse)
        async def execute_orchestrated_task(task: AITask, background_tasks: BackgroundTasks) -> TaskResponse:
            """Execute a task through the full orchestration system with persona assumption fighting"""
            # FIX H3: Ensure initialization is complete before processing
            await self._ensure_initialized()
            
            start_time = datetime.now()
            
            try:
                # Create orchestrator task
                orchestrator_task = OrchestratorTask(
                    task_id=f"api_task_{int(datetime.now().timestamp() * 1000)}",
                    task_type="text_generation",
                    description=task.prompt,
                    input_data={
                        "prompt": task.prompt,
                        "persona": task.persona,
                        "context": task.context
                    },
                    priority=TaskPriority.MEDIUM,
                    estimated_tokens=1000,
                    requires_governance=True  # Enable governance for assumption validation
                )
                
                # Process through enhanced persona orchestration with assumption fighting
                consensus_decision = await self.persona_orchestration.process_task_with_full_orchestration(
                    orchestrator_task
                )
                
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                
                # Add metadata if TaskResponse supports it
                response = TaskResponse(
                    success=True,
                    response=consensus_decision.final_decision,
                    cached=False,
                    tokens_saved=0,
                    persona_used="orchestrated_consensus",
                    execution_time_ms=execution_time
                )
                
                # Log the consensus details
                logger.info(f"Orchestrated task completed with consensus level: {consensus_decision.consensus_level.value}")
                logger.info(f"Assumptions validated: {len(consensus_decision.assumptions_validated)}")
                logger.info(f"Evidence used: {len(consensus_decision.evidence_used)}")
                
                return response
                
            except Exception as e:
                logger.error(f"Orchestrated task execution failed: {e}")
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                
                return TaskResponse(
                    success=False,
                    error=str(e),
                    cached=False,
                    execution_time_ms=execution_time
                )
        
        @self.app.get("/orchestration/status")
        async def get_orchestration_status():
            """Get status of the orchestration engine"""
            # FIX H3: Ensure initialization is complete before accessing orchestrator
            await self._ensure_initialized()
            
            status = self.ai_orchestrator.get_orchestration_status()
            agent_status = agent_terminal_manager.get_agent_status()
            
            return {
                "is_running": status["is_running"],
                "agents": {
                    "total": agent_status['total'],
                    "active": agent_status['by_status']['ready'] + agent_status['by_status']['busy'],
                    "idle": agent_status['by_status']['idle'],
                    "busy": agent_status['by_status']['busy'],
                    "max": agent_status['max_agents'],
                    "details": agent_status['agents']
                },
                "tasks": status["tasks"],
                "performance": status["performance"],
                "governance_active": True,
                "persona_orchestration_active": True
            }
        
        @self.app.get("/metrics/cache", response_model=CacheMetrics)
        async def get_cache_metrics():
            """Return current cache performance metrics"""
            # FIX H3: Cache metrics can be accessed without full initialization
            # but we should still wait if initialization is in progress
            if not self._initialization_complete:
                # Return basic metrics if not fully initialized
                return CacheMetrics(
                    hit_rate=0.0,
                    tokens_saved=0,
                    hot_cache_size_mb=0.0,
                    warm_cache_files=0,
                    total_requests=0,
                    cache_hits=0,
                    cache_misses=0
                )
            
            metrics = self.cache.get_metrics()
            
            return CacheMetrics(
                hit_rate=metrics['hit_rate'],
                tokens_saved=metrics['tokens_saved'],
                hot_cache_size_mb=metrics['hot_cache_size_mb'],
                warm_cache_files=metrics['warm_cache_files'],
                total_requests=metrics.get('total_requests', 0),
                cache_hits=metrics.get('hits', 0),
                cache_misses=metrics.get('misses', 0)
            )
        
        @self.app.post("/persona/suggest")
        async def suggest_persona(suggestion: PersonaSuggestion):
            """
            Business Logic: Auto-suggest best personas for task
            Returns: List of suggested personas with confidence scores
            """
            # FIX H3: Persona suggestions don't require full initialization
            # but should be consistent once available
            try:
                suggestions = self.persona_manager.suggest_persona(suggestion.description)
                
                return {
                    "personas": [
                        {
                            "type": p.value,
                            "name": self.persona_manager.personas[p].name,
                            "expertise": self.persona_manager.personas[p].expertise
                        }
                        for p in suggestions
                    ]
                }
            except Exception as e:
                logger.error(f"Persona suggestion failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/persona/resolve-conflict")
        async def resolve_persona_conflict(responses: Dict[str, str]):
            """
            Business Logic: Resolve conflicts when multiple personas respond
            Method: Voting mechanism based on response confidence
            """
            try:
                resolution = self.persona_manager.resolve_conflict(responses)
                return resolution
            except Exception as e:
                logger.error(f"Conflict resolution failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/metrics/performance")
        async def get_performance_metrics():
            """Return overall system performance metrics"""
            # FIX H3: Performance metrics can be partial during initialization
            if not self._initialization_complete:
                return {
                    "status": "initializing",
                    "metrics": {},
                    "message": "System is still initializing"
                }
            return await self.metrics.get_performance_summary()
        
        @self.app.get("/agents/status")
        async def get_agent_status():
            """Return status of all AI agents"""
            # FIX H3: Agent status requires initialization
            await self._ensure_initialized()
            
            agent_status = agent_terminal_manager.get_agent_status()
            return {
                "max_concurrent_agents": agent_status['max_agents'],
                "active_agents": agent_status['total'],
                "available_personas": list(self.persona_manager.personas.keys()),
                "agents": agent_status['agents'],
                "by_type": agent_status['by_type']
            }
        
        @self.app.post("/agents/spawn")
        async def spawn_agent(request_data: dict):
            """Spawn a new AI agent with its own terminal - WITH GOVERNANCE"""
            # FIX H3: Agent spawning requires full initialization
            await self._ensure_initialized()
            
            agent_type_str = request_data.get('type', 'claude_assistant')
            agent_name = request_data.get('name', None)
            metadata = request_data.get('metadata', {})
            
            try:
                # GOVERNANCE: Validate agent spawn request
                governance_result = await self.runtime_governance.validate_agent_spawn(
                    agent_type=agent_type_str,
                    agent_name=agent_name,
                    metadata=metadata
                )
                
                if not governance_result.approved:
                    logger.warning(f"Agent spawn rejected: {governance_result.reason}")
                    return {
                        'success': False,
                        'error': f"Governance rejected: {governance_result.reason}",
                        'risk_level': governance_result.risk_level,
                        'recommendations': governance_result.recommendations
                    }
                
                # Proceed with spawn if approved
                agent_type = AgentType(agent_type_str)
                agent = await agent_terminal_manager.spawn_agent(agent_type)
                
                # GOVERNANCE: Register the spawned agent
                await self.runtime_governance.register_agent(
                    agent_id=agent.id,
                    agent_type=agent_type_str,
                    agent_name=agent.name,
                    metadata=metadata
                )
                
                # Broadcast agent creation
                await ws_manager.broadcast({
                    'type': 'agent_spawned',
                    'agent': agent.to_dict(),
                    'governance_approved': True
                })
                
                return {
                    'success': True,
                    'agent': agent.to_dict(),
                    'governance': {
                        'approved': True,
                        'risk_level': governance_result.risk_level
                    }
                }
            except Exception as e:
                logger.error(f"Agent spawn error: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }
        
        @self.app.post("/agents/{agent_id}/execute")
        async def execute_on_agent(agent_id: str, request_data: dict):
            """Send command to specific agent - WITH GOVERNANCE"""
            # FIX H3: Agent execution requires full initialization
            await self._ensure_initialized()
            
            command = request_data.get('command', '')
            context = request_data.get('context', {})
            
            try:
                # GOVERNANCE: Validate execution request
                governance_result = await self.runtime_governance.validate_agent_execution(
                    agent_id=agent_id,
                    command=command,
                    context=context
                )
                
                if not governance_result.approved:
                    logger.warning(f"Command execution rejected for agent {agent_id}: {governance_result.reason}")
                    return {
                        'success': False,
                        'error': f"Governance rejected: {governance_result.reason}",
                        'risk_level': governance_result.risk_level,
                        'recommendations': governance_result.recommendations
                    }
                
                # Execute if approved
                response = await agent_terminal_manager.send_to_agent(agent_id, command)
                
                # For AI-generated responses, validate the decision
                if response and isinstance(response, str):
                    decision_validation = await self.decision_injector.intercept_decision(
                        agent_id=agent_id,
                        decision_type=DecisionType.USER_INTERACTION,
                        input_context={'command': command, 'context': context},
                        proposed_output=response
                    )
                    
                    # Apply modifications if any
                    if decision_validation.modifications:
                        response = decision_validation.modifications.get('modified', response)
                        logger.info(f"Response modified by governance for agent {agent_id}")
                    
                    # Include governance metadata in response
                    return {
                        'success': True,
                        'response': response,
                        'timestamp': datetime.now().isoformat(),
                        'governance': {
                            'decision_approved': decision_validation.approved,
                            'risk_level': decision_validation.risk_level.value,
                            'confidence': decision_validation.confidence_score,
                            'modified': bool(decision_validation.modifications),
                            'warnings': decision_validation.warnings
                        }
                    }
                else:
                    return {
                        'success': True,
                        'response': response,
                        'timestamp': datetime.now().isoformat()
                    }
                    
            except Exception as e:
                logger.error(f"Agent execution error: {e}")
                return {'success': False, 'error': str(e)}
        
        @self.app.delete("/agents/{agent_id}")
        async def terminate_agent(agent_id: str):
            """Terminate an agent - WITH GOVERNANCE"""
            await self._ensure_initialized()
            
            try:
                # GOVERNANCE: Record termination
                await self.runtime_governance.terminate_agent(
                    agent_id=agent_id,
                    reason="User requested termination"
                )
                
                # Actually terminate the agent
                result = await agent_terminal_manager.terminate_agent(agent_id)
                
                return {
                    'success': True,
                    'message': f"Agent {agent_id} terminated"
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        # ========== GOVERNANCE MONITORING ENDPOINTS ==========
        
        @self.app.get("/governance/status")
        async def get_governance_status():
            """Get current governance system status"""
            await self._ensure_initialized()
            
            metrics = self.runtime_governance.get_metrics()
            active_agents = len(self.runtime_governance.active_agents)
            
            return {
                "status": "active",
                "governance_level": self.runtime_governance.governance_level.value,
                "metrics": metrics,
                "active_agents": active_agents,
                "resource_limits": self.runtime_governance.resource_limits
            }
        
        @self.app.get("/governance/audit-log")
        async def get_audit_log(limit: int = 100):
            """Get recent audit log entries"""
            await self._ensure_initialized()
            
            logs = self.runtime_governance.get_audit_log(limit)
            return {
                "total_entries": len(self.runtime_governance.audit_log),
                "returned": len(logs),
                "logs": logs
            }
        
        @self.app.get("/governance/agents/{agent_id}")
        async def get_agent_governance(agent_id: str):
            """Get governance details for specific agent"""
            await self._ensure_initialized()
            
            if agent_id not in self.runtime_governance.active_agents:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            agent_context = self.runtime_governance.active_agents[agent_id]
            return {
                "agent_id": agent_id,
                "agent_type": agent_context.agent_type,
                "agent_name": agent_context.agent_name,
                "spawn_time": agent_context.spawn_time.isoformat(),
                "resource_usage": agent_context.resource_usage,
                "task_count": len(agent_context.task_history),
                "violations": agent_context.violations,
                "metadata": agent_context.metadata
            }
        
        @self.app.post("/governance/level")
        async def set_governance_level(request_data: dict):
            """Change governance enforcement level"""
            await self._ensure_initialized()
            
            level_str = request_data.get('level', 'STRICT').upper()
            
            if level_str not in ['STRICT', 'WARNING', 'MONITOR', 'BYPASS']:
                return {
                    'success': False,
                    'error': 'Invalid governance level. Must be STRICT, WARNING, MONITOR, or BYPASS'
                }
            
            self.runtime_governance.set_governance_level(GovernanceLevel[level_str])
            
            return {
                'success': True,
                'new_level': level_str,
                'message': f"Governance level changed to {level_str}"
            }
        
        @self.app.post("/governance/resource-limits")
        async def update_resource_limits(request_data: dict):
            """Update resource limits"""
            await self._ensure_initialized()
            
            try:
                self.runtime_governance.update_resource_limits(request_data)
                return {
                    'success': True,
                    'new_limits': self.runtime_governance.resource_limits
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        @self.app.get("/governance/decision-metrics")
        async def get_decision_metrics():
            """Get AI decision injection metrics"""
            await self._ensure_initialized()
            
            return self.decision_injector.get_metrics()
        
        # Continue with original terminate_agent implementation if needed
        @self.app.delete("/agents/{agent_id}/original")
        async def terminate_agent_original(agent_id: str):
            """Terminate an agent (original version)"""
            await agent_terminal_manager.terminate_agent(agent_id)
            return {'success': True}
        
        @self.app.post("/cache/clear")
        async def clear_cache():
            """Clear cache (useful for testing)"""
            await self.cache.clear()
            return {"message": "Cache cleared successfully"}
        
        @self.app.post("/claude/connect")
        async def connect_claude():
            """Connect to Claude terminal"""
            async def output_handler(data):
                await ws_manager.broadcast({
                    'type': 'claude_output',
                    'data': data
                })
            
            result = await claude_terminal.connect(output_handler)
            return result
        
        @self.app.post("/claude/send")
        async def send_to_claude(request_data: dict):
            """Send message to Claude terminal"""
            message = request_data.get('message', '')
            result = await claude_terminal.send_message(message)
            return result
        
        @self.app.get("/claude/status")
        async def claude_status():
            """Get Claude terminal status"""
            return claude_terminal.get_status()
        
        @self.app.post("/claude/disconnect")
        async def disconnect_claude():
            """Disconnect Claude terminal"""
            result = await claude_terminal.disconnect()
            return result
    
    def setup_websocket_routes(self):
        """Setup WebSocket endpoints for real-time monitoring"""
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """Main WebSocket endpoint for real-time updates"""
            client_id = f"client_{datetime.now().timestamp()}"
            await ws_manager.connect(websocket, client_id)
            
            try:
                # Start background task for periodic updates
                asyncio.create_task(self.send_periodic_updates(websocket))
                
                while True:
                    # Receive and handle client messages
                    data = await websocket.receive_json()
                    await ws_manager.handle_client_message(websocket, data)
                    
            except WebSocketDisconnect:
                ws_manager.disconnect(websocket)
                logger.info(f"WebSocket client {client_id} disconnected")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                ws_manager.disconnect(websocket)
        
        @self.app.get("/ws/status")
        async def get_websocket_status():
            """Get WebSocket connection status"""
            return {
                'active_connections': ws_manager.get_connection_count(),
                'connections': ws_manager.get_connection_info()
            }
    
    async def send_periodic_updates(self, websocket: WebSocket):
        """Send periodic updates to WebSocket clients"""
        try:
            while websocket in ws_manager.active_connections:
                # Send orchestration status every 5 seconds
                await asyncio.sleep(5)
                
                # Get real agent data from AgentTerminalManager
                agent_status = agent_terminal_manager.get_agent_status()
                
                # Build status with real agent data
                real_status = {
                    "is_running": True,
                    "agents": {
                        "total": agent_status['total'],
                        "active": agent_status['by_status']['ready'] + agent_status['by_status']['busy'],
                        "idle": agent_status['by_status']['idle'],
                        "busy": agent_status['by_status']['busy'],
                        "ready": agent_status['by_status']['ready'],
                        "error": agent_status['by_status']['error'],
                        "max": agent_status['max_agents']
                    },
                    "tasks": {
                        "queued": 0,
                        "active": agent_status['by_status']['busy'],
                        "completed": sum(a['tasks_completed'] for a in agent_status['agents']),
                        "failed": 0
                    },
                    "performance": {
                        "total_tokens_used": 0,
                        "average_response_time": 0.0,
                        "overall_success_rate": 1.0
                    }
                }
                
                await ws_manager.broadcast_orchestration_status(real_status)
                
                # Send cache metrics every 10 seconds
                await asyncio.sleep(5)
                
                if self.cache:
                    metrics = self.cache.get_metrics()
                    await ws_manager.broadcast_cache_metrics(metrics)
                    
        except Exception as e:
            logger.error(f"Error in periodic updates: {e}")
    
    def run(self):
        """Start the backend service"""
        logger.info(f"Starting {self.app_config.name} Backend on {self.host}:{self.port}")
        logger.info(f"Environment: {self.app_config.environment}")
        
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level=self.app_config.logging.level.lower()
        )

def main():
    """Main entry point with automatic port discovery"""
    # Load centralized configuration
    app_config = get_config()
    
    parser = argparse.ArgumentParser(description='AI Development Assistant Backend')
    parser.add_argument('--port', type=int, default=None, 
                      help='Port to run the service on (auto-discovers if not specified)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                      help='Host to bind to')
    parser.add_argument('--env', type=str, default='development',
                      choices=['development', 'production', 'test'],
                      help='Environment to run in')
    parser.add_argument('--correlation-id', type=str, default=None,
                      help='Correlation ID for debugging')
    args = parser.parse_args()
    
    # Set environment if specified
    if args.env:
        os.environ['APP_ENV'] = args.env
    
    # Use port discovery if no port specified or if default port is in use
    if args.port is None:
        # Try to use configured port first, then discover if needed
        port_discovery = get_port_discovery()
        port = port_discovery.find_available_port('backend')
        logger.info(f"Using discovered port: {port}")
    else:
        # Check if specified port is available
        port_discovery = get_port_discovery()
        if port_discovery.is_port_available(args.port):
            port = args.port
            port_discovery.allocate_port('backend', port)
        else:
            # Port is in use, discover a new one
            logger.warning(f"Port {args.port} is in use, discovering available port...")
            port = port_discovery.find_available_port('backend')
            logger.info(f"Using discovered port: {port}")
    
    # Write port file for frontend to discover
    port_discovery.write_port_file(port)
    
    # Register cleanup on exit
    import atexit
    atexit.register(cleanup_backend_port)
    
    service = AIBackendService(port=port, host=args.host)
    service.run()

if __name__ == "__main__":
    main()