"""
File: ai-assistant/backend/governance/api/health_endpoints.py
Purpose: Health check endpoints for governance system monitoring
Architecture: FastAPI router providing comprehensive health status endpoints
Dependencies: fastapi, typing, datetime
Owner: Dr. Sarah Chen

@fileoverview Health check API endpoints for system monitoring and observability
@author Dr. Sarah Chen v1.0 - Backend Systems Architect
@architecture Backend - FastAPI health check router with multi-level monitoring
@business_logic Provides health status for governance components, circuit breakers, and sessions
@integration_points FastAPI app, Kubernetes probes, monitoring systems
@error_handling Returns 503 for unhealthy states, graceful degradation
@performance Sub-millisecond response for basic checks, <100ms for detailed
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel

# Import governance components
from ..core.runtime_governance import RuntimeGovernanceSystem
from ..core.session_manager import SessionManager
from ..validators.health_checker import HealthChecker, HealthStatus
from ..core.circuit_breaker import circuit_breaker_manager
from ..core.structured_logging import StructuredLogger, with_correlation_id

logger = StructuredLogger(__name__)

# Create health check router
health_router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={
        503: {"description": "Service unhealthy"},
        200: {"description": "Service healthy"}
    }
)


class HealthResponse(BaseModel):
    """
    Health check response model.
    
    Attributes:
        status: Overall health status
        timestamp: Check timestamp
        checks: Individual component health checks
        metadata: Additional health metadata
    """
    status: str
    timestamp: str
    checks: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class DetailedHealthResponse(BaseModel):
    """
    Detailed health check response with comprehensive metrics.
    
    Attributes:
        status: Overall health status
        timestamp: Check timestamp
        components: Detailed component health information
        metrics: System metrics and statistics
        circuit_breakers: Circuit breaker states
        sessions: Session management statistics
    """
    status: str
    timestamp: str
    components: Dict[str, Any]
    metrics: Dict[str, Any]
    circuit_breakers: Dict[str, Any]
    sessions: Dict[str, Any]


@health_router.get("/", response_model=HealthResponse)
@with_correlation_id
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.
    
    Performs quick health check of critical components.
    Returns 503 if any critical component is unhealthy.
    
    Returns:
        HealthResponse with basic health status
    """
    logger.info("Health check requested")
    
    # Initialize health checker
    health_checker = HealthChecker()
    
    # Perform basic checks
    checks = {}
    overall_status = HealthStatus.HEALTHY
    
    try:
        # Check governance system
        governance_system = RuntimeGovernanceSystem()
        governance_stats = governance_system.get_statistics()
        checks['governance'] = {
            'status': 'healthy',
            'total_decisions': governance_stats.get('total_decisions', 0)
        }
    except Exception as e:
        checks['governance'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        overall_status = HealthStatus.UNHEALTHY
    
    try:
        # Check session manager
        session_manager = SessionManager()
        session_stats = session_manager.get_statistics()
        checks['sessions'] = {
            'status': 'healthy',
            'active_sessions': session_stats.get('active_sessions', 0)
        }
    except Exception as e:
        checks['sessions'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        overall_status = HealthStatus.UNHEALTHY
    
    # Check circuit breakers
    breaker_stats = circuit_breaker_manager.get_all_stats()
    open_breakers = [
        name for name, stats in breaker_stats.items()
        if stats.get('state') == 'open'
    ]
    
    if open_breakers:
        checks['circuit_breakers'] = {
            'status': 'degraded',
            'open_breakers': open_breakers
        }
        if overall_status == HealthStatus.HEALTHY:
            overall_status = HealthStatus.DEGRADED
    else:
        checks['circuit_breakers'] = {
            'status': 'healthy',
            'all_closed': True
        }
    
    response = HealthResponse(
        status=overall_status.value,
        timestamp=datetime.utcnow().isoformat() + 'Z',
        checks=checks
    )
    
    # Return appropriate status code
    if overall_status == HealthStatus.UNHEALTHY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response.dict()
        )
    
    logger.info("Health check completed", status=overall_status.value)
    return response


@health_router.get("/live", status_code=status.HTTP_204_NO_CONTENT)
async def liveness_probe():
    """
    Kubernetes liveness probe endpoint.
    
    Simple endpoint that returns 204 if the service is alive.
    Used for container orchestration health checks.
    """
    logger.debug("Liveness probe")
    return None


@health_router.get("/ready", response_model=Dict[str, str])
@with_correlation_id
async def readiness_probe() -> Dict[str, str]:
    """
    Kubernetes readiness probe endpoint.
    
    Checks if the service is ready to accept traffic.
    Returns 503 if critical dependencies are not available.
    
    Returns:
        Dictionary with readiness status
    """
    logger.info("Readiness probe requested")
    
    # Check critical dependencies
    ready = True
    reasons = []
    
    try:
        # Check if governance is initialized
        governance_system = RuntimeGovernanceSystem()
        if not governance_system.validator:
            ready = False
            reasons.append("Governance validator not initialized")
    except Exception as e:
        ready = False
        reasons.append(f"Governance system error: {e}")
    
    try:
        # Check if session manager is operational
        session_manager = SessionManager()
        stats = session_manager.get_statistics()
        if stats.get('total_sessions', 0) > 10000:
            ready = False
            reasons.append("Session limit approaching")
    except Exception as e:
        ready = False
        reasons.append(f"Session manager error: {e}")
    
    if ready:
        logger.info("Service ready")
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
    else:
        logger.warning("Service not ready", reasons=reasons)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "reasons": reasons,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@health_router.get("/detailed", response_model=DetailedHealthResponse)
@with_correlation_id
async def detailed_health_check() -> DetailedHealthResponse:
    """
    Detailed health check with comprehensive metrics.
    
    Provides detailed information about all system components,
    including metrics, statistics, and circuit breaker states.
    
    Returns:
        DetailedHealthResponse with comprehensive health information
    """
    logger.info("Detailed health check requested")
    
    # Initialize components
    health_checker = HealthChecker()
    governance_system = RuntimeGovernanceSystem()
    session_manager = SessionManager()
    
    # Get comprehensive health report
    health_report = await health_checker.get_health_report()
    
    # Collect detailed component information
    components = {
        'governance': {
            'status': 'operational',
            'statistics': governance_system.get_statistics(),
            'validator': {
                'circuit_state': governance_system.validator.circuit_breaker.get_state().value,
                'retry_stats': governance_system.validator.retry_manager.get_statistics()
            }
        },
        'sessions': {
            'status': 'operational',
            'statistics': session_manager.get_statistics(),
            'active_count': len(session_manager.get_active_sessions())
        },
        'health_checker': health_report
    }
    
    # Collect system metrics
    metrics = {
        'uptime': datetime.utcnow().isoformat(),
        'governance_decisions': governance_system.get_statistics().get('total_decisions', 0),
        'active_sessions': session_manager.get_statistics().get('active_sessions', 0),
        'circuit_breakers_open': len([
            name for name, stats in circuit_breaker_manager.get_all_stats().items()
            if stats.get('state') == 'open'
        ])
    }
    
    # Get circuit breaker details
    circuit_breakers = circuit_breaker_manager.get_all_stats()
    
    # Get session details
    sessions = {
        'statistics': session_manager.get_statistics(),
        'timeout_seconds': session_manager.timeout_seconds,
        'max_sessions': session_manager.max_sessions
    }
    
    response = DetailedHealthResponse(
        status=health_report.get('overall_status', 'unknown'),
        timestamp=datetime.utcnow().isoformat() + 'Z',
        components=components,
        metrics=metrics,
        circuit_breakers=circuit_breakers,
        sessions=sessions
    )
    
    logger.info("Detailed health check completed", status=response.status)
    return response


@health_router.get("/components/{component_name}")
@with_correlation_id
async def component_health_check(component_name: str) -> Dict[str, Any]:
    """
    Health check for specific component.
    
    Args:
        component_name: Name of component to check
        
    Returns:
        Component-specific health information
    """
    logger.info("Component health check requested", component=component_name)
    
    health_checker = HealthChecker()
    
    # Map component names to check methods
    component_checks = {
        'database': health_checker._check_database,
        'cache': health_checker._check_cache,
        'websocket': health_checker._check_websocket,
        'filesystem': health_checker._check_filesystem,
        'governance': lambda: _check_governance_health(),
        'sessions': lambda: _check_session_health()
    }
    
    if component_name not in component_checks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Component '{component_name}' not found"
        )
    
    try:
        result = await health_checker.check_service(component_name)
        logger.info("Component health check completed", component=component_name, status=result['status'])
        return result
    except Exception as e:
        logger.error("Component health check failed", component=component_name, error=e)
        return {
            'status': 'error',
            'component': component_name,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }


async def _check_governance_health() -> bool:
    """Check governance system health."""
    try:
        governance_system = RuntimeGovernanceSystem()
        stats = governance_system.get_statistics()
        return stats.get('total_decisions', 0) >= 0
    except Exception:
        return False


async def _check_session_health() -> bool:
    """Check session manager health."""
    try:
        session_manager = SessionManager()
        stats = session_manager.get_statistics()
        return stats.get('active_sessions', 0) < session_manager.max_sessions
    except Exception:
        return False


# Export router for inclusion in main app
__all__ = ['health_router']