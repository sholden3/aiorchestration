"""
Port Discovery Integration for MCP Server

Provides port discovery functionality for the MCP governance server
using the existing port discovery system.

Author: Dr. Sarah Chen
Phase: MCP-001 PHOENIX_RISE_FOUNDATION
"""

import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.port_discovery import PortDiscovery, get_port_discovery


async def discover_backend_port(
    service_name: str = "mcp-governance",
    fallback: int = 8001
) -> int:
    """
    Discover an available port for the MCP governance server.
    
    This function wraps the existing port discovery system to provide
    async compatibility and specific defaults for MCP server.
    
    Args:
        service_name: Name of the service requesting port
        fallback: Fallback port if discovery fails
        
    Returns:
        Available port number for MCP server
    """
    try:
        discovery = get_port_discovery()
        
        # Set preferred port range for MCP services
        discovery.port_range = (8001, 8100)
        discovery.preferred_port = fallback
        
        # Find available port
        port = discovery.find_available_port(service_name)
        
        # Write to port file for other processes
        discovery.write_port_file(port, Path.home() / '.ai_assistant' / f'{service_name}_port.txt')
        
        return port
        
    except Exception as e:
        # If port discovery fails, use fallback
        import logging
        logging.error(f"Port discovery failed: {e}, using fallback port {fallback}")
        return fallback


def release_mcp_port(service_name: str = "mcp-governance") -> None:
    """
    Release the port allocation for MCP server.
    
    Args:
        service_name: Name of the service
    """
    try:
        discovery = get_port_discovery()
        discovery.release_port(service_name)
    except Exception as e:
        import logging
        logging.error(f"Failed to release port for {service_name}: {e}")


def get_allocated_mcp_port(service_name: str = "mcp-governance") -> Optional[int]:
    """
    Get the currently allocated port for MCP server.
    
    Args:
        service_name: Name of the service
        
    Returns:
        Port number if allocated, None otherwise
    """
    try:
        discovery = get_port_discovery()
        return discovery.get_allocated_port(service_name)
    except Exception:
        return None