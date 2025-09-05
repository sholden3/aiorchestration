"""
Governance MCP Server Implementation

Provides intelligent governance consultation via Model Context Protocol,
enabling Claude Code to proactively query governance decisions during
reasoning rather than being validated after actions.

Author: Alex Novak & Dr. Sarah Chen
Phase: MCP-001 PHOENIX_RISE_FOUNDATION
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import configuration loader
from apps.api.mcp.config_loader import get_config, get_mcp_config
from apps.api.mcp.port_integration import discover_backend_port, release_mcp_port

# Note: The mcp library would need to be installed separately
# For now, we'll create a placeholder implementation
try:
    from mcp import Server, Request, Response
    from mcp.types import Tool, TextContent, Resource
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    # Placeholder classes for development
    class Server:
        def __init__(self, name): 
            self.name = name
        def tool(self): 
            return lambda f: f
        def resource(self): 
            return lambda f: f
        async def run(self): 
            pass

# Import our data-driven persona manager
from libs.governance.personas import PersonaManager

logger = logging.getLogger(__name__)


class GovernanceMCPServer:
    """
    MCP Server for governance intelligence and consultation.
    
    Provides proactive governance guidance to Claude Code through
    the Model Context Protocol, enabling intelligent assistance
    during the reasoning process.
    
    This implementation uses data-driven persona definitions from
    libs/governance/personas.yaml for all consultation logic.
    """
    
    def __init__(self):
        """Initialize the governance MCP server."""
        # Load configuration
        self.config = get_config()
        server_config = self.config.get_server_config()
        
        self.server = Server(server_config.get('name', 'governance-intelligence'))
        self.port: Optional[int] = None
        
        # Use data-driven PersonaManager with configurable path
        personas_path = Path(self.config.get('governance.personas_config', 'libs/governance/personas.yaml'))
        self.personas = PersonaManager(personas_path)
        
        # Session tracking
        self.sessions: Dict[str, Dict] = {}
        self.start_time = datetime.utcnow()
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_response_time': 0,
            'errors': 0
        }
        
        # Note: These would be initialized with actual implementations
        self.governance = None  # Would be RuntimeGovernanceSystem()
        self.db = None  # Would be DatabaseManager()
        self.cache = {}  # Simple dict cache for now
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP protocol handlers."""
        
        # Tool: Consult governance for an operation
        @self.server.tool()
        async def consult_governance(
            operation: str,
            context: Dict[str, Any]
        ) -> str:
            """
            Consult governance system for guidance on an operation.
            
            Args:
                operation: Type of operation (e.g., 'file_edit', 'command_execution')
                context: Context information about the operation
                
            Returns:
                Governance guidance and recommendations
            """
            start_time = asyncio.get_event_loop().time()
            self.metrics['total_requests'] += 1
            
            try:
                # Check cache first
                cache_key = f"governance:{operation}:{json.dumps(context, sort_keys=True)}"
                if cache_key in self.cache:
                    self.metrics['cache_hits'] += 1
                    return self.cache[cache_key]
                
                self.metrics['cache_misses'] += 1
                
                # Get persona guidance using data-driven system
                persona_guidance = await self._get_persona_guidance(operation, context)
                
                # Format response
                response = {
                    'approved': True,  # Would come from actual governance check
                    'confidence': 0.95,
                    'operation': operation,
                    'context_summary': {k: str(v)[:100] for k, v in context.items()},
                    'persona_guidance': persona_guidance,
                    'recommendations': self._generate_recommendations(operation, context),
                    'warnings': self._check_warnings(operation, context)
                }
                
                response_str = json.dumps(response, indent=2)
                
                # Cache the response
                self.cache[cache_key] = response_str
                
                # Update metrics
                elapsed = asyncio.get_event_loop().time() - start_time
                self._update_response_time(elapsed)
                
                return response_str
                
            except Exception as e:
                self.metrics['errors'] += 1
                logger.error(f"Error in governance consultation: {e}")
                return json.dumps({
                    'error': str(e),
                    'fallback': 'Proceed with caution, follow standard practices'
                })
        
        # Tool: Get historical decisions
        @self.server.tool()
        async def get_historical_decisions(
            pattern: str,
            limit: int = 10
        ) -> str:
            """
            Retrieve historical governance decisions for learning.
            
            Args:
                pattern: Pattern to search for in decisions
                limit: Maximum number of results
                
            Returns:
                Historical decisions and their outcomes
            """
            try:
                # Placeholder for database query
                # In real implementation, would query actual database
                decisions = [
                    {
                        'id': f'DEC-2025-{i:03d}',
                        'operation': f'Operation {i}',
                        'context': {'example': 'context'},
                        'outcome': 'approved',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    for i in range(min(limit, 5))
                    if pattern.lower() in f'operation {i}'.lower()
                ]
                
                return json.dumps(decisions, indent=2)
                
            except Exception as e:
                logger.error(f"Error retrieving historical decisions: {e}")
                return json.dumps({'error': str(e), 'decisions': []})
        
        # Tool: Consult specific persona
        @self.server.tool()
        async def consult_persona(
            persona_name: str,
            question: str,
            context: Dict[str, Any]
        ) -> str:
            """
            Consult a specific persona for domain expertise.
            
            Args:
                persona_name: Name of the persona to consult
                question: Question for the persona
                context: Context information
                
            Returns:
                Persona's expert guidance
            """
            try:
                # Use data-driven persona consultation
                guidance = await self.personas.consult(
                    persona_name=persona_name,
                    question=question,
                    context=context
                )
                
                return json.dumps({
                    'persona': persona_name,
                    'guidance': guidance,
                    'timestamp': datetime.utcnow().isoformat()
                }, indent=2)
                
            except Exception as e:
                logger.error(f"Error consulting persona {persona_name}: {e}")
                return json.dumps({
                    'error': str(e),
                    'persona': persona_name,
                    'fallback': 'Persona temporarily unavailable'
                })
        
        # Tool: Get available personas
        @self.server.tool()
        async def get_available_personas() -> str:
            """Get list of all available personas and their specialties."""
            try:
                personas = self.personas.get_all_personas()
                return json.dumps(personas, indent=2)
            except Exception as e:
                logger.error(f"Error getting personas: {e}")
                return json.dumps({'error': str(e), 'personas': {}})
        
        # Resource: Current governance configuration
        @self.server.resource()
        async def governance_config() -> str:
            """Get current governance configuration."""
            rules_path = Path(self.config.get('governance.rules_config', 'libs/governance/documentation_standards.yaml'))
            if rules_path.exists():
                return rules_path.read_text()
            return "Configuration not found"
        
        # Resource: Persona configuration
        @self.server.resource()
        async def persona_config() -> str:
            """Get current persona configuration."""
            personas_path = Path(self.config.get('governance.personas_config', 'libs/governance/personas.yaml'))
            if personas_path.exists():
                return personas_path.read_text()
            return "Persona configuration not found"
        
        # Resource: System health status
        @self.server.resource()
        async def system_status() -> str:
            """Get MCP server health status."""
            uptime = (datetime.utcnow() - self.start_time).total_seconds()
            
            status = {
                'status': 'operational',
                'uptime_seconds': uptime,
                'metrics': self.metrics,
                'cache_hit_rate': self._calculate_cache_hit_rate(),
                'avg_response_time_ms': self.metrics['avg_response_time'] * 1000,
                'active_sessions': len(self.sessions),
                'available_personas': len(self.personas.personas),
                'mcp_available': MCP_AVAILABLE
            }
            
            return json.dumps(status, indent=2)
    
    async def _get_persona_guidance(
        self,
        operation: str,
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Get guidance from relevant personas based on operation type."""
        guidance = {}
        
        # Use data-driven persona determination
        relevant_personas = self.personas.determine_relevant_personas(operation, context)
        
        for persona_name, confidence in relevant_personas:
            try:
                result = await self.personas.consult(
                    persona_name=persona_name,
                    question=f"Guidance for {operation}",
                    context=context
                )
                guidance[persona_name] = {
                    'guidance': result,
                    'confidence': confidence
                }
            except Exception as e:
                logger.warning(f"Failed to consult {persona_name}: {e}")
        
        return guidance
    
    def _generate_recommendations(
        self,
        operation: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on operation and context."""
        recommendations = []
        
        # File operations
        if 'file' in operation.lower():
            recommendations.append("Ensure file backup before modification")
            recommendations.append("Check file permissions and ownership")
            recommendations.append("Validate file path to prevent traversal")
        
        # Command execution
        if 'command' in operation.lower() or 'bash' in operation.lower():
            recommendations.append("Sanitize command inputs")
            recommendations.append("Use timeout for long-running commands")
            recommendations.append("Log command execution for audit")
        
        # Database operations
        if 'database' in operation.lower() or 'sql' in context:
            recommendations.append("Use parameterized queries")
            recommendations.append("Check connection pool status")
            recommendations.append("Monitor query performance")
        
        # API operations
        if 'api' in operation.lower() or 'endpoint' in operation.lower():
            recommendations.append("Implement rate limiting")
            recommendations.append("Add authentication checks")
            recommendations.append("Validate input schemas")
        
        return recommendations[:5]  # Limit recommendations
    
    def _check_warnings(
        self,
        operation: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """Check for potential warnings based on operation."""
        warnings = []
        
        # Check for dangerous patterns
        if 'command' in context:
            cmd = context['command']
            dangerous_patterns = [
                'rm -rf /',
                'DROP TABLE',
                'DELETE FROM',
                ':(){ :|:& };:',  # Fork bomb
                'curl | sh'
            ]
            for pattern in dangerous_patterns:
                if pattern in cmd:
                    warnings.append(f"[WARNING] Dangerous pattern detected: '{pattern}'")
        
        # Check for sensitive file paths
        if 'file_path' in context:
            path = context['file_path']
            sensitive_paths = ['.env', 'credentials', 'password', 'secret', 'key']
            for sensitive in sensitive_paths:
                if sensitive in path.lower():
                    warnings.append(f"[WARNING] Sensitive file path detected: {sensitive}")
        
        # Check for production indicators
        if 'production' in str(context).lower() or 'prod' in str(context).lower():
            warnings.append("[WARNING] Production environment - extra caution required")
        
        return warnings
    
    def _update_response_time(self, elapsed: float):
        """Update average response time metric."""
        n = self.metrics['total_requests']
        if n == 1:
            self.metrics['avg_response_time'] = elapsed
        else:
            # Calculate running average
            self.metrics['avg_response_time'] = (
                (self.metrics['avg_response_time'] * (n - 1) + elapsed) / n
            )
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.metrics['cache_hits'] + self.metrics['cache_misses']
        if total == 0:
            return 0.0
        return self.metrics['cache_hits'] / total
    
    async def initialize(self):
        """Initialize the MCP server with port discovery."""
        try:
            # Initialize personas
            await self.personas.initialize()
            
            # Use port discovery from configuration
            port_config = self.config.get_port_config()
            self.port = await discover_backend_port(
                service_name=port_config['service_name'],
                fallback=port_config['fallback']
            )
            
            logger.info(f"Discovered port {self.port} for MCP server")
            
            # In real implementation, would also initialize:
            # - Database connection
            # - Cache system (Redis or memory)
            # - Governance system
            
            # Generate MCP configuration file
            await self._generate_mcp_config()
            
            logger.info("MCP server initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP server: {e}")
            raise
    
    async def _generate_mcp_config(self):
        """Generate .mcp.json configuration for Claude Code."""
        config = {
            "mcpServers": {
                "governance": {
                    "command": "python",
                    "args": [
                        "-m",
                        "apps.api.mcp.governance_server"
                    ],
                    "env": {
                        "GOVERNANCE_PORT": str(self.port),
                        "DATABASE_URL": self.config.get_database_url(),
                        "CACHE_TYPE": self.config.get('cache.type', 'memory'),
                        "LOG_LEVEL": self.config.get('server.log_level', 'INFO'),
                        "MCP_ENV": self.config.get('server.environment', 'development')
                    }
                }
            }
        }
        
        # Write configuration
        config_path = Path(".mcp.json")
        config_path.write_text(json.dumps(config, indent=2))
        logger.info(f"Generated MCP configuration at {config_path}")
    
    async def start(self):
        """Start the MCP server."""
        if not self.port:
            await self.initialize()
        
        logger.info(f"Starting MCP server on port {self.port}")
        
        if MCP_AVAILABLE:
            # Start the actual MCP server
            await self.server.run()
        else:
            # Development mode - just log
            logger.warning("MCP library not available - running in development mode")
            logger.info("MCP server would be running on port %s", self.port)
            # Keep running for testing
            while True:
                await asyncio.sleep(60)
    
    async def shutdown(self):
        """Gracefully shutdown the MCP server."""
        logger.info("Shutting down MCP server")
        
        # Save metrics (would save to actual database in production)
        logger.info(f"Final metrics: {self.metrics}")
        
        # Release port allocation
        if self.port:
            release_mcp_port(self.config.get('server.name', 'mcp-governance'))
        
        logger.info("MCP server shutdown complete")


async def main():
    """Main entry point for the MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    server = GovernanceMCPServer()
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await server.shutdown()


if __name__ == "__main__":
    asyncio.run(main())