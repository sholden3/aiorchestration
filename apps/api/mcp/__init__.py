"""
MCP (Model Context Protocol) Server for Governance Intelligence

This module implements the MCP server that provides proactive governance
consultation to Claude Code, transforming reactive validation into 
intelligent assistance during the reasoning process.

Author: Alex Novak & Dr. Sarah Chen
Version: 0.1.0
Phase: MCP-001 PHOENIX_RISE_FOUNDATION
"""

from .governance_server import GovernanceMCPServer

__all__ = [
    'GovernanceMCPServer'
]

__version__ = '0.1.0'