"""
Claude Code Hook Bridge to MCP Governance Server

Implements the NEURAL_LINK_BRIDGE that connects Claude Code's native hook system
(PreToolUse, UserPromptSubmit, PostToolUse) to the MCP governance server for
proactive governance consultation.

Author: Alex Novak
Phase: MCP-002 NEURAL_LINK_BRIDGE
"""

import asyncio
import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import aiohttp
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from apps.api.mcp.config_loader import get_config

logger = logging.getLogger(__name__)


class ClaudeCodeGovernanceBridge:
    """
    Bridge between Claude Code hooks and MCP governance server.
    
    This bridge enables Claude Code to consult the MCP governance server
    BEFORE executing tools (PreToolUse), inject context (UserPromptSubmit),
    and audit actions (PostToolUse).
    """
    
    def __init__(self):
        """Initialize the hook bridge."""
        self.config = get_config()
        self.mcp_base_url = self._get_mcp_url()
        self.session: Optional[aiohttp.ClientSession] = None
        self.metrics = {
            'total_validations': 0,
            'blocks': 0,
            'allows': 0,
            'errors': 0,
            'avg_response_time': 0
        }
    
    def _get_mcp_url(self) -> str:
        """Get MCP server URL from configuration."""
        host = self.config.get('server.host', '127.0.0.1')
        port = self.config.get('server.port.preferred', 8001)
        return f"http://{host}:{port}"
    
    async def initialize(self):
        """Initialize the bridge with HTTP session."""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
            logger.info(f"Initialized hook bridge to MCP at {self.mcp_base_url}")
    
    async def pre_tool_validation(self, hook_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Handle PreToolUse hook - the primary governance gatekeeper.
        
        This is called BEFORE Claude Code executes any tool and can block execution.
        
        Args:
            hook_data: Data from Claude Code hook including:
                - tool: Tool name being invoked
                - parameters: Tool parameters
                - context: Execution context
                
        Returns:
            Tuple of (allow: bool, message: str)
            - allow: True to allow execution, False to block
            - message: Explanation for decision
        """
        start_time = time.time()
        self.metrics['total_validations'] += 1
        
        try:
            await self.initialize()
            
            # Prepare governance consultation request
            consultation_request = {
                'operation': f"tool_execution.{hook_data.get('tool', 'unknown')}",
                'context': {
                    'tool': hook_data.get('tool'),
                    'parameters': hook_data.get('parameters', {}),
                    'user_context': hook_data.get('context', {}),
                    'timestamp': datetime.utcnow().isoformat(),
                    'hook_type': 'PreToolUse'
                }
            }
            
            # Consult MCP governance server
            async with self.session.post(
                f"{self.mcp_base_url}/consult_governance",
                json=consultation_request
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Parse governance decision
                    approved = result.get('approved', True)
                    confidence = result.get('confidence', 0.5)
                    warnings = result.get('warnings', [])
                    recommendations = result.get('recommendations', [])
                    
                    # Log decision
                    logger.info(
                        f"Governance decision for {hook_data.get('tool')}: "
                        f"{'ALLOW' if approved else 'BLOCK'} (confidence: {confidence})"
                    )
                    
                    # Update metrics
                    elapsed = time.time() - start_time
                    self._update_response_time(elapsed)
                    
                    if approved:
                        self.metrics['allows'] += 1
                        message = self._format_allow_message(recommendations, warnings)
                        return True, message
                    else:
                        self.metrics['blocks'] += 1
                        message = self._format_block_message(result)
                        return False, message
                
                else:
                    # MCP server error - fail open with warning
                    logger.error(f"MCP server returned status {response.status}")
                    self.metrics['errors'] += 1
                    return True, "[WARNING] Governance server unavailable - proceeding with caution"
                    
        except asyncio.TimeoutError:
            logger.error("MCP consultation timeout")
            self.metrics['errors'] += 1
            return True, "[WARNING] Governance consultation timeout - proceeding"
            
        except Exception as e:
            logger.error(f"Error during pre-tool validation: {e}")
            self.metrics['errors'] += 1
            return True, f"[WARNING] Governance error: {str(e)} - proceeding"
    
    async def user_prompt_context_injection(self, hook_data: Dict[str, Any]) -> str:
        """
        Handle UserPromptSubmit hook - inject governance context.
        
        This is called when the user submits a prompt and allows injecting
        governance context into Claude's reasoning.
        
        Args:
            hook_data: Data from Claude Code hook including user prompt
            
        Returns:
            Context to inject into Claude's reasoning
        """
        try:
            await self.initialize()
            
            # Get relevant governance context
            context_request = {
                'operation': 'context_injection',
                'context': {
                    'user_prompt': hook_data.get('prompt', ''),
                    'timestamp': datetime.utcnow().isoformat(),
                    'hook_type': 'UserPromptSubmit'
                }
            }
            
            async with self.session.post(
                f"{self.mcp_base_url}/get_governance_context",
                json=context_request
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Format governance context for injection
                    context_lines = [
                        "[Governance Context]",
                        f"Active policies: {result.get('active_policies', 'standard')}",
                        f"Compliance level: {result.get('compliance_level', '95%')}",
                        f"Restrictions: {', '.join(result.get('restrictions', []))}",
                        f"Recommendations: {', '.join(result.get('recommendations', []))}"
                    ]
                    
                    return "\n".join(context_lines)
                
        except Exception as e:
            logger.error(f"Error during context injection: {e}")
        
        return ""  # Return empty context on error
    
    async def post_tool_audit(self, hook_data: Dict[str, Any]) -> None:
        """
        Handle PostToolUse hook - audit and feedback.
        
        This is called AFTER Claude Code executes a tool for audit trail
        and learning purposes.
        
        Args:
            hook_data: Data from Claude Code hook including execution results
        """
        try:
            await self.initialize()
            
            # Send audit data to MCP server
            audit_request = {
                'operation': f"audit.{hook_data.get('tool', 'unknown')}",
                'context': {
                    'tool': hook_data.get('tool'),
                    'parameters': hook_data.get('parameters', {}),
                    'result': hook_data.get('result', {}),
                    'exit_code': hook_data.get('exit_code', 0),
                    'timestamp': datetime.utcnow().isoformat(),
                    'hook_type': 'PostToolUse'
                }
            }
            
            async with self.session.post(
                f"{self.mcp_base_url}/audit_execution",
                json=audit_request
            ) as response:
                if response.status == 200:
                    logger.info(f"Audit recorded for {hook_data.get('tool')}")
                else:
                    logger.warning(f"Audit recording failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error during post-tool audit: {e}")
    
    def _format_allow_message(self, recommendations: list, warnings: list) -> str:
        """Format message for allowed execution."""
        message_parts = ["Execution allowed."]
        
        if recommendations:
            message_parts.append(f"Recommendations: {'; '.join(recommendations[:3])}")
        
        if warnings:
            message_parts.append(f"Warnings: {'; '.join(warnings[:2])}")
        
        return " ".join(message_parts)
    
    def _format_block_message(self, result: Dict[str, Any]) -> str:
        """Format message for blocked execution."""
        reason = result.get('block_reason', 'Governance policy violation')
        remediation = result.get('remediation', 'Contact governance team for approval')
        
        return f"BLOCKED: {reason}. {remediation}"
    
    def _update_response_time(self, elapsed: float):
        """Update average response time metric."""
        n = self.metrics['total_validations']
        if n == 1:
            self.metrics['avg_response_time'] = elapsed
        else:
            self.metrics['avg_response_time'] = (
                (self.metrics['avg_response_time'] * (n - 1) + elapsed) / n
            )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get bridge metrics."""
        return {
            **self.metrics,
            'avg_response_time_ms': self.metrics['avg_response_time'] * 1000,
            'block_rate': (
                self.metrics['blocks'] / self.metrics['total_validations'] 
                if self.metrics['total_validations'] > 0 else 0
            ),
            'error_rate': (
                self.metrics['errors'] / self.metrics['total_validations']
                if self.metrics['total_validations'] > 0 else 0
            )
        }
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Hook bridge cleaned up")


async def handle_claude_code_hook(hook_type: str, hook_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for Claude Code hooks.
    
    Args:
        hook_type: Type of hook (PreToolUse, UserPromptSubmit, PostToolUse)
        hook_data: Hook data from Claude Code
        
    Returns:
        Response for Claude Code
    """
    bridge = ClaudeCodeGovernanceBridge()
    
    try:
        if hook_type == "PreToolUse":
            allow, message = await bridge.pre_tool_validation(hook_data)
            return {
                'allow': allow,
                'message': message,
                'exit_code': 0 if allow else 2  # Exit code 2 blocks execution
            }
            
        elif hook_type == "UserPromptSubmit":
            context = await bridge.user_prompt_context_injection(hook_data)
            return {
                'context': context,
                'exit_code': 0
            }
            
        elif hook_type == "PostToolUse":
            await bridge.post_tool_audit(hook_data)
            return {
                'exit_code': 0,
                'message': 'Audit recorded'
            }
            
        else:
            logger.warning(f"Unknown hook type: {hook_type}")
            return {
                'exit_code': 1,
                'error': f'Unknown hook type: {hook_type}'
            }
            
    except Exception as e:
        logger.error(f"Hook handler error: {e}")
        return {
            'exit_code': 1,
            'error': str(e)
        }
        
    finally:
        await bridge.cleanup()


if __name__ == "__main__":
    # Example usage for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python claude_code_hook_bridge.py <hook_type> [hook_data_json]")
        sys.exit(1)
    
    hook_type = sys.argv[1]
    hook_data = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    
    # Run hook handler
    result = asyncio.run(handle_claude_code_hook(hook_type, hook_data))
    
    # Output result for Claude Code
    print(json.dumps(result))
    sys.exit(result.get('exit_code', 0))