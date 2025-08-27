"""
FIX H3: Application Startup Coordinator with Dependency Management
Architecture: Dr. Sarah Chen
Pattern: Ordered initialization with health checks and degraded mode support
"""
import asyncio
import time
import logging
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)

class StartupState(Enum):
    """Application startup states"""
    INITIALIZING = "initializing"
    READY = "ready"
    DEGRADED = "degraded"
    FAILED = "failed"

class ComponentState(Enum):
    """Individual component states"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    READY = "ready"
    FAILED = "failed"
    DEGRADED = "degraded"

@dataclass
class ComponentStatus:
    """Status of a single component"""
    name: str
    state: ComponentState
    health: bool = False
    error: Optional[str] = None
    startup_time_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ApplicationReadiness:
    """Overall application readiness status"""
    ready: bool
    state: StartupState
    startup_time_ms: float
    component_status: Dict[str, ComponentStatus]
    degraded: bool = False
    failed_components: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class StartupMetrics:
    """Metrics tracking for application startup"""
    
    def __init__(self):
        self.startup_attempts = 0
        self.successful_startups = 0
        self.failed_startups = 0
        self.component_init_times: Dict[str, List[float]] = defaultdict(list)
        self.total_startup_times: List[float] = []
        self.failure_reasons: Dict[str, int] = defaultdict(int)
        
    def record_successful_startup(self, startup_time_ms: float):
        """Record successful startup"""
        self.successful_startups += 1
        self.total_startup_times.append(startup_time_ms)
        
    def record_failed_startup(self, reason: str):
        """Record failed startup"""
        self.failed_startups += 1
        self.failure_reasons[reason] += 1
        
    def record_component_init(self, component: str, init_time_ms: float):
        """Record component initialization time"""
        self.component_init_times[component].append(init_time_ms)
        
    def get_average_startup_time(self) -> float:
        """Get average startup time"""
        if not self.total_startup_times:
            return 0
        return sum(self.total_startup_times) / len(self.total_startup_times)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        return {
            'startup_attempts': self.startup_attempts,
            'successful_startups': self.successful_startups,
            'failed_startups': self.failed_startups,
            'average_startup_time_ms': self.get_average_startup_time(),
            'component_average_times': {
                comp: sum(times) / len(times) if times else 0
                for comp, times in self.component_init_times.items()
            },
            'top_failure_reasons': dict(sorted(
                self.failure_reasons.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5])
        }

class ApplicationStartupCoordinator:
    """
    FIX H3: Coordinated application startup with dependency management
    Sarah's pattern: No endpoints accessible until dependencies ready
    """
    
    def __init__(self):
        self.startup_state = StartupState.INITIALIZING
        self.components: Dict[str, ComponentStatus] = {}
        self.startup_metrics = StartupMetrics()
        
        # Component initialization functions
        self.initializers: Dict[str, Callable] = {}
        self.health_checkers: Dict[str, Callable] = {}
        
        # Dependency graph for ordered initialization
        self.dependency_graph: Dict[str, List[str]] = {
            'config': [],
            'database': ['config'],
            'cache': ['config'],
            'websocket_manager': ['config'],
            'orchestrator': ['database', 'cache'],
            'api_routes': ['database', 'cache', 'websocket_manager', 'orchestrator']
        }
        
        # Critical components (must be healthy for app to start)
        self.critical_components = {'config', 'database', 'api_routes'}
        
        # Component initialization timeout (seconds)
        self.component_timeout = 30
        
        logger.info("Application Startup Coordinator initialized")
    
    def register_component(
        self,
        name: str,
        initializer: Callable,
        health_checker: Optional[Callable] = None,
        dependencies: Optional[List[str]] = None,
        critical: bool = True
    ):
        """
        Register a component with its initialization function
        
        Args:
            name: Component name
            initializer: Async function to initialize component
            health_checker: Optional async function to check health
            dependencies: List of component names this depends on
            critical: Whether this component is critical for startup
        """
        self.initializers[name] = initializer
        
        if health_checker:
            self.health_checkers[name] = health_checker
            
        if dependencies is not None:
            self.dependency_graph[name] = dependencies
            
        if critical:
            self.critical_components.add(name)
            
        self.components[name] = ComponentStatus(
            name=name,
            state=ComponentState.PENDING
        )
        
        logger.info(f"Registered component: {name} "
                   f"(critical: {critical}, deps: {dependencies or []})")
    
    async def initialize_application(self) -> ApplicationReadiness:
        """
        Initialize application with coordinated startup
        Sarah's approach: Dependency resolution and ordered initialization
        """
        startup_start = time.time()
        self.startup_state = StartupState.INITIALIZING
        self.startup_metrics.startup_attempts += 1
        
        logger.info("=== APPLICATION STARTUP INITIATED ===")
        
        try:
            # Resolve initialization order
            init_order = self._resolve_dependency_order()
            logger.info(f"Initialization order: {init_order}")
            
            # Initialize components in order
            for component_name in init_order:
                success = await self._initialize_component_safely(component_name)
                if not success and component_name in self.critical_components:
                    # Critical component failed
                    raise Exception(f"Critical component {component_name} failed to initialize")
            
            # Perform health checks
            health_results = await self._perform_health_checks()
            
            # Determine startup state
            failed_components = [
                name for name, status in self.components.items()
                if status.state == ComponentState.FAILED
            ]
            
            unhealthy_components = [
                name for name, healthy in health_results.items()
                if not healthy
            ]
            
            # Check if we can start
            critical_failures = [
                comp for comp in failed_components + unhealthy_components
                if comp in self.critical_components
            ]
            
            if not critical_failures:
                # All critical components are healthy
                if failed_components or unhealthy_components:
                    # Some non-critical components failed - degraded mode
                    self.startup_state = StartupState.DEGRADED
                    logger.warning(f"Starting in DEGRADED mode. "
                                 f"Failed: {failed_components}, "
                                 f"Unhealthy: {unhealthy_components}")
                else:
                    # Everything is healthy
                    self.startup_state = StartupState.READY
                    logger.info("Application startup completed successfully")
                
                startup_time = (time.time() - startup_start) * 1000
                self.startup_metrics.record_successful_startup(startup_time)
                
                return ApplicationReadiness(
                    ready=True,
                    state=self.startup_state,
                    startup_time_ms=startup_time,
                    component_status=self.components.copy(),
                    degraded=(self.startup_state == StartupState.DEGRADED),
                    failed_components=failed_components + unhealthy_components,
                    warnings=self._generate_warnings()
                )
            else:
                # Critical components failed
                self.startup_state = StartupState.FAILED
                error_msg = f"Critical components failed: {critical_failures}"
                self.startup_metrics.record_failed_startup(error_msg)
                
                raise Exception(error_msg)
                
        except Exception as e:
            self.startup_state = StartupState.FAILED
            logger.error(f"Application startup failed: {e}", exc_info=True)
            
            startup_time = (time.time() - startup_start) * 1000
            
            return ApplicationReadiness(
                ready=False,
                state=StartupState.FAILED,
                startup_time_ms=startup_time,
                component_status=self.components.copy(),
                failed_components=[
                    name for name, status in self.components.items()
                    if status.state == ComponentState.FAILED
                ],
                warnings=[str(e)]
            )
    
    async def _initialize_component_safely(self, component_name: str) -> bool:
        """
        Initialize a single component with error handling
        
        Returns:
            True if initialization succeeded, False otherwise
        """
        if component_name not in self.initializers:
            logger.warning(f"No initializer for component: {component_name}")
            return True  # Skip if no initializer
        
        component = self.components[component_name]
        component.state = ComponentState.INITIALIZING
        start_time = time.time()
        
        try:
            logger.info(f"Initializing component: {component_name}")
            
            # Check dependencies are ready
            for dep in self.dependency_graph.get(component_name, []):
                dep_status = self.components.get(dep)
                if not dep_status or dep_status.state != ComponentState.READY:
                    raise Exception(f"Dependency {dep} not ready")
            
            # Initialize with timeout
            initializer = self.initializers[component_name]
            await asyncio.wait_for(
                initializer(),
                timeout=self.component_timeout
            )
            
            # Mark as ready
            component.state = ComponentState.READY
            component.startup_time_ms = (time.time() - start_time) * 1000
            
            self.startup_metrics.record_component_init(
                component_name,
                component.startup_time_ms
            )
            
            logger.info(f"Component {component_name} initialized in "
                       f"{component.startup_time_ms:.2f}ms")
            return True
            
        except asyncio.TimeoutError:
            component.state = ComponentState.FAILED
            component.error = f"Initialization timeout ({self.component_timeout}s)"
            logger.error(f"Component {component_name} initialization timeout")
            return False
            
        except Exception as e:
            component.state = ComponentState.FAILED
            component.error = str(e)
            logger.error(f"Component {component_name} initialization failed: {e}")
            return False
    
    async def _perform_health_checks(self) -> Dict[str, bool]:
        """
        Perform health checks on all components
        
        Returns:
            Dictionary of component_name -> is_healthy
        """
        health_results = {}
        
        for component_name, health_checker in self.health_checkers.items():
            try:
                logger.debug(f"Health check: {component_name}")
                is_healthy = await asyncio.wait_for(
                    health_checker(),
                    timeout=5  # Quick health check timeout
                )
                health_results[component_name] = is_healthy
                self.components[component_name].health = is_healthy
                
                if not is_healthy:
                    logger.warning(f"Component {component_name} is unhealthy")
                    
            except Exception as e:
                logger.error(f"Health check failed for {component_name}: {e}")
                health_results[component_name] = False
                self.components[component_name].health = False
        
        return health_results
    
    def _resolve_dependency_order(self) -> List[str]:
        """
        Resolve component initialization order using topological sort
        
        Returns:
            List of component names in initialization order
        """
        # Build in-degree map
        in_degree = defaultdict(int)
        for component in self.dependency_graph:
            in_degree[component] = 0
            
        for component, deps in self.dependency_graph.items():
            for dep in deps:
                in_degree[component] += 1
        
        # Find components with no dependencies
        queue = [comp for comp, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            component = queue.pop(0)
            result.append(component)
            
            # Check components that depend on this one
            for other_comp, deps in self.dependency_graph.items():
                if component in deps:
                    in_degree[other_comp] -= 1
                    if in_degree[other_comp] == 0:
                        queue.append(other_comp)
        
        # Check for circular dependencies
        if len(result) != len(self.dependency_graph):
            raise Exception("Circular dependency detected in component graph")
        
        return result
    
    def _generate_warnings(self) -> List[str]:
        """Generate warnings based on current state"""
        warnings = []
        
        # Check for slow components
        for name, status in self.components.items():
            if status.startup_time_ms and status.startup_time_ms > 5000:
                warnings.append(f"Component {name} took {status.startup_time_ms:.0f}ms to initialize")
        
        # Check for degraded components
        degraded = [
            name for name, status in self.components.items()
            if status.state == ComponentState.DEGRADED
        ]
        if degraded:
            warnings.append(f"Components in degraded state: {degraded}")
        
        return warnings
    
    def get_status(self) -> Dict[str, Any]:
        """Get current startup status"""
        return {
            'state': self.startup_state.value,
            'components': {
                name: {
                    'state': status.state.value,
                    'health': status.health,
                    'error': status.error,
                    'startup_time_ms': status.startup_time_ms
                }
                for name, status in self.components.items()
            },
            'metrics': self.startup_metrics.get_metrics(),
            'critical_components': list(self.critical_components),
            'is_ready': self.startup_state in [StartupState.READY, StartupState.DEGRADED]
        }
    
    def is_ready(self) -> bool:
        """Check if application is ready to serve requests"""
        return self.startup_state in [StartupState.READY, StartupState.DEGRADED]
    
    def is_healthy(self) -> bool:
        """Check if application is fully healthy"""
        return self.startup_state == StartupState.READY