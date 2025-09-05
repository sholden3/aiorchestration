#!/usr/bin/env python3
"""
Claude Code Hook Handlers

Entry point for Claude Code hooks that bridges to the MCP governance server.
This module is invoked by Claude Code when hooks are triggered.

Author: Alex Novak
Phase: MCP-002 NEURAL_LINK_BRIDGE
"""

import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import uuid
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Configure logging with defensive patterns
log_dir = Path.home() / '.ai_assistant' / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'hook_bridge.log'),
        logging.StreamHandler(sys.stderr)  # Also log to stderr for debugging
    ]
)

logger = logging.getLogger(__name__)


class CorrelationFilter(logging.Filter):
    """Add correlation ID to all log records."""
    
    def __init__(self):
        super().__init__()
        self.correlation_id = str(uuid.uuid4())
    
    def filter(self, record):
        record.correlation_id = getattr(record, 'correlation_id', self.correlation_id)
        return True


# Add correlation filter to logger
correlation_filter = CorrelationFilter()
logger.addFilter(correlation_filter)


def parse_hook_input() -> Tuple[Optional[str], Dict[str, Any], str]:
    """
    Parse input from Claude Code with defensive error handling.
    
    Claude Code passes hook data via stdin as JSON or command line args.
    
    Returns:
        Tuple of (hook_type, hook_data, correlation_id)
    """
    correlation_id = str(uuid.uuid4())
    
    # Alex Novak: Always assume hostile input
    if len(sys.argv) < 2:
        logger.error("No hook type provided", extra={'correlation_id': correlation_id})
        return None, {}, correlation_id
    
    hook_type = sys.argv[1]
    logger.info(f"Processing hook type: {hook_type}", extra={'correlation_id': correlation_id})
    
    # Read hook data with multiple fallback strategies
    hook_data = {}
    
    try:
        # Strategy 1: Read from stdin (preferred)
        if not sys.stdin.isatty():
            import select
            # Check if stdin has data (with timeout)
            ready, _, _ = select.select([sys.stdin], [], [], 0.1)
            if ready:
                hook_data_raw = sys.stdin.read()
                if hook_data_raw:
                    hook_data = json.loads(hook_data_raw)
                    logger.info(f"Parsed hook data from stdin", extra={'correlation_id': correlation_id})
    except Exception as e:
        logger.warning(f"Failed to read from stdin: {e}", extra={'correlation_id': correlation_id})
    
    # Strategy 2: Command line argument fallback
    if not hook_data and len(sys.argv) > 2:
        try:
            hook_data = json.loads(sys.argv[2])
            logger.info(f"Parsed hook data from argv", extra={'correlation_id': correlation_id})
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse hook data from argv: {e}", extra={'correlation_id': correlation_id})
    
    # Add correlation ID to hook data
    hook_data['correlation_id'] = correlation_id
    
    return hook_type, hook_data, correlation_id


def format_hook_response(result: Dict[str, Any], correlation_id: str) -> str:
    """
    Format response for Claude Code with defensive patterns.
    
    Args:
        result: Result from hook handler
        correlation_id: Correlation ID for tracing
        
    Returns:
        JSON string for Claude Code
    """
    # Dr. Sarah Chen: Always include debugging context
    result['correlation_id'] = correlation_id
    result['timestamp'] = time.time()
    
    # Ensure required fields with safe defaults
    if 'exit_code' not in result:
        result['exit_code'] = 0
    
    # Alex Novak: Executive-readable error context
    if result.get('exit_code') == 2:
        # Blocking response needs clear explanation
        result['blocked'] = True
        if 'executive_summary' not in result:
            result['executive_summary'] = "Operation blocked by governance policy"
    
    # Format with pretty printing for debugging
    return json.dumps(result, indent=2, default=str)


async def handle_with_fallback(hook_type: str, hook_data: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
    """
    Handle hook with circuit breaker and fallback patterns.
    
    Dr. Sarah Chen: This implements the Three Questions framework.
    """
    start_time = time.time()
    
    try:
        # Try to import and use the bridge
        from apps.api.mcp.claude_code_hook_bridge import handle_claude_code_hook
        
        logger.info(f"Calling hook bridge for {hook_type}", extra={'correlation_id': correlation_id})
        
        # Set timeout for MCP consultation (Alex Novak: never trust external calls)
        result = await asyncio.wait_for(
            handle_claude_code_hook(hook_type, hook_data),
            timeout=5.0  # 5 second timeout
        )
        
        elapsed = time.time() - start_time
        logger.info(f"Hook handled successfully in {elapsed:.2f}s", extra={'correlation_id': correlation_id})
        
        return result
        
    except asyncio.TimeoutError:
        # What breaks first? Timeout
        logger.error(f"Hook bridge timeout after 5s", extra={'correlation_id': correlation_id})
        
        # What's Plan B? Fail open with warning
        return {
            'exit_code': 0,  # Don't block on timeout
            'warning': 'Governance consultation timeout - proceeding with caution',
            'fallback': True,
            'elapsed_ms': 5000,
            'executive_summary': 'Governance system slow - allowing with monitoring'
        }
        
    except ImportError as e:
        # Bridge module not available
        logger.error(f"Hook bridge not available: {e}", extra={'correlation_id': correlation_id})
        
        return {
            'exit_code': 0,
            'warning': 'Governance bridge not available',
            'fallback': True,
            'executive_summary': 'Governance system offline - manual review recommended'
        }
        
    except Exception as e:
        # Unknown failure - log comprehensively
        logger.error(f"Hook handler error: {e}", exc_info=True, extra={'correlation_id': correlation_id})
        
        # Dr. Sarah Chen: Never hide errors, but don't block operations
        return {
            'exit_code': 1,  # Indicate error but don't block (exit 2 blocks)
            'error': str(e),
            'fallback': True,
            'executive_summary': f'Technical error in governance: {type(e).__name__}'
        }


async def main():
    """Main entry point with comprehensive error handling."""
    correlation_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Parse input with correlation tracking
        hook_type, hook_data, correlation_id = parse_hook_input()
        
        if not hook_type:
            result = {
                'exit_code': 1,
                'error': 'No hook type provided',
                'executive_summary': 'Configuration error - hook type missing'
            }
        else:
            # Log hook invocation for audit
            logger.info(
                f"Hook invoked: {hook_type}",
                extra={
                    'correlation_id': correlation_id,
                    'tool': hook_data.get('tool', 'unknown'),
                    'user': hook_data.get('user', 'unknown')
                }
            )
            
            # Handle with fallback patterns
            result = await handle_with_fallback(hook_type, hook_data, correlation_id)
            
            # Log result for audit
            logger.info(
                f"Hook result: exit_code={result.get('exit_code', 0)}",
                extra={
                    'correlation_id': correlation_id,
                    'blocked': result.get('blocked', False),
                    'fallback': result.get('fallback', False)
                }
            )
    
    except Exception as e:
        # Catastrophic failure - still try to respond
        logger.critical(f"Critical hook handler error: {e}", exc_info=True, extra={'correlation_id': correlation_id})
        result = {
            'exit_code': 1,
            'error': 'Critical system error',
            'executive_summary': 'Governance system critical failure - manual intervention required'
        }
    
    finally:
        # Always provide response
        elapsed = time.time() - start_time
        result['elapsed_ms'] = int(elapsed * 1000)
        
        # Output result for Claude Code
        print(format_hook_response(result, correlation_id))
        
        # Flush logs
        logging.shutdown()
        
        # Exit with appropriate code
        sys.exit(result.get('exit_code', 0))


if __name__ == "__main__":
    # Handle both Windows and Unix environments
    if sys.platform == "win32":
        # Windows doesn't support select on stdin
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run main with proper event loop handling
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "already running" in str(e):
            # Already in async context
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
        else:
            raise