"""
File: ai-assistant/backend/governance/__init__.py
Purpose: Initialize governance module for runtime validation and system management
Architecture: Provides core governance services to FastAPI application with failsafe defaults
Dependencies: FastAPI, pydantic, asyncio
Owner: Dr. Sarah Chen

@fileoverview Governance module initialization with failsafe defaults
@author Dr. Sarah Chen v1.0 - Backend Systems Architect
@architecture Backend - Core governance module providing runtime validation
@business_logic Initializes governance subsystem with graceful degradation for missing components
@integration_points FastAPI middleware, runtime validators, session management
@error_handling Graceful fallback when components unavailable
@performance O(1) module initialization with lazy component loading
"""

from typing import Optional, Dict, Any
import logging

# Configure module logger
logger = logging.getLogger(__name__)

# Module version
__version__ = "1.0.0"

# Import core components with error handling
try:
    from .core.runtime_governance import (
        RuntimeGovernanceSystem,
        RuntimeGovernanceValidator,
        HookType,
        GovernanceLevel,
        AgentContext,
        DecisionContext
    )
    from .core.session_manager import SessionManager
    from .validators.health_checker import HealthChecker
    from .middleware.ai_decision_injector import (
        AIDecisionInjector,
        DecisionType
    )
    
    # Export public API
    __all__ = [
        'RuntimeGovernanceSystem',
        'RuntimeGovernanceValidator',
        'SessionManager',
        'HealthChecker',
        'AIDecisionInjector',
        'DecisionType',
        'HookType',
        'GovernanceLevel',
        'AgentContext',
        'DecisionContext',
        'initialize_governance',
        'get_governance_config'
    ]
    
    logger.info(f"Governance module v{__version__} initialized successfully")
    
except ImportError as e:
    logger.warning(f"Governance module initialization with limited functionality: {e}")
    
    # Provide stub implementations for graceful degradation
    RuntimeGovernanceSystem = None
    RuntimeGovernanceValidator = None
    SessionManager = None
    HealthChecker = None
    AIDecisionInjector = None
    DecisionType = None
    HookType = None
    GovernanceLevel = None
    AgentContext = None
    DecisionContext = None
    
    __all__ = [
        'initialize_governance',
        'get_governance_config'
    ]


def initialize_governance(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Initialize governance subsystem with failsafe defaults.
    
    This function sets up the governance module with the provided configuration
    or uses sensible defaults if no configuration is provided. It ensures the
    system can start even if some governance components are unavailable.
    
    Args:
        config: Optional governance configuration dictionary with keys:
            - enabled: Whether governance is active (default: True)
            - validators: List of active validators (default: ['health', 'session'])
            - session_timeout: Session timeout in seconds (default: 3600)
            - health_check_interval: Health check interval in seconds (default: 30)
            - fallback_mode: Enable fallback for missing components (default: True)
    
    Returns:
        Governance configuration dictionary with applied settings
        
    Raises:
        GovernanceInitError: Only on critical failures that prevent any operation
        
    Example:
        config = initialize_governance({
            'enabled': True,
            'validators': ['health', 'session', 'audit'],
            'session_timeout': 7200
        })
    """
    default_config = {
        'enabled': True,
        'validators': ['health', 'session'],
        'middleware_order': ['logging', 'governance', 'cors'],
        'session_timeout': 3600,
        'health_check_interval': 30,
        'fallback_mode': True,
        'version': __version__
    }
    
    # Merge provided config with defaults
    if config:
        default_config.update(config)
    
    # Validate configuration
    if not isinstance(default_config['validators'], list):
        logger.warning("Invalid validators configuration, using defaults")
        default_config['validators'] = ['health', 'session']
    
    # Log initialization
    logger.info(f"Governance initialized with config: {default_config}")
    
    return default_config


def get_governance_config() -> Dict[str, Any]:
    """
    Retrieve current governance configuration.
    
    Returns the active governance configuration including runtime status
    of various components.
    
    Returns:
        Dictionary containing:
            - version: Module version
            - components_available: List of available components
            - fallback_active: Whether fallback mode is active
            - health_status: Current health check status
            
    Example:
        config = get_governance_config()
        if 'health' in config['components_available']:
            run_health_checks()
    """
    components_available = []
    
    # Check which components are available
    if RuntimeGovernanceSystem is not None:
        components_available.append('runtime_governance')
    if SessionManager is not None:
        components_available.append('session_manager')
    if HealthChecker is not None:
        components_available.append('health_checker')
    if AIDecisionInjector is not None:
        components_available.append('ai_decision_injector')
    
    return {
        'version': __version__,
        'components_available': components_available,
        'fallback_active': len(components_available) < 4,
        'health_status': 'operational' if components_available else 'degraded'
    }


# Module initialization logging
logger.info(f"Governance module loaded: {get_governance_config()}")