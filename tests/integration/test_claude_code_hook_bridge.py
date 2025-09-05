"""
Integration tests for Claude Code Hook Bridge

Tests the complete flow from Claude Code hooks to MCP governance server.

Author: Dr. Sarah Chen & Alex Novak
Phase: MCP-002 NEURAL_LINK_BRIDGE
"""

import pytest
import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import aiohttp
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps.api.mcp.claude_code_hook_bridge import (
    ClaudeCodeGovernanceBridge,
    handle_claude_code_hook
)
from apps.api.mcp.hook_handlers import (
    parse_hook_input,
    format_hook_response,
    handle_with_fallback
)


class TestClaudeCodeGovernanceBridge:
    """Test suite for Claude Code Governance Bridge."""
    
    @pytest.fixture
    def bridge(self):
        """Create a bridge instance for testing."""
        return ClaudeCodeGovernanceBridge()
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock aiohttp session."""
        session = AsyncMock(spec=aiohttp.ClientSession)
        return session
    
    @pytest.mark.asyncio
    async def test_pre_tool_validation_allow(self, bridge, mock_session):
        """Test PreToolUse validation that allows execution."""
        # Dr. Sarah Chen: Test the happy path first
        bridge.session = mock_session
        
        # Mock successful MCP consultation
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'approved': True,
            'confidence': 0.95,
            'warnings': [],
            'recommendations': ['Use defensive patterns', 'Add timeout'],
            'persona_guidance': {
                'Alex Novak': {'guidance': 'Add IPC timeout', 'confidence': 0.9},
                'Dr. Sarah Chen': {'guidance': 'Implement circuit breaker', 'confidence': 0.95}
            }
        })
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        # Test data
        hook_data = {
            'tool': 'file_edit',
            'parameters': {'file': 'test.py', 'content': 'print("test")'},
            'context': {'user': 'test_user'}
        }
        
        # Execute
        allow, message = await bridge.pre_tool_validation(hook_data)
        
        # Verify
        assert allow is True
        assert 'Execution allowed' in message
        assert 'Use defensive patterns' in message
        assert bridge.metrics['allows'] == 1
        assert bridge.metrics['total_validations'] == 1
    
    @pytest.mark.asyncio
    async def test_pre_tool_validation_block(self, bridge, mock_session):
        """Test PreToolUse validation that blocks execution."""
        # Alex Novak: Test the blocking path - critical for security
        bridge.session = mock_session
        
        # Mock MCP consultation that blocks
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'approved': False,
            'confidence': 0.98,
            'block_reason': 'Dangerous command detected',
            'remediation': 'Request manual approval from security team',
            'warnings': ['Command matches dangerous pattern'],
            'recommendations': []
        })
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        # Test data with dangerous command
        hook_data = {
            'tool': 'bash',
            'parameters': {'command': 'rm -rf /'},
            'context': {'user': 'test_user'}
        }
        
        # Execute
        allow, message = await bridge.pre_tool_validation(hook_data)
        
        # Verify
        assert allow is False
        assert 'BLOCKED' in message
        assert 'Dangerous command detected' in message
        assert bridge.metrics['blocks'] == 1
        assert bridge.metrics['total_validations'] == 1
    
    @pytest.mark.asyncio
    async def test_pre_tool_validation_timeout(self, bridge, mock_session):
        """Test PreToolUse validation with timeout."""
        # Dr. Sarah Chen: What breaks first? Timeouts!
        bridge.session = mock_session
        
        # Mock timeout
        mock_session.post.side_effect = asyncio.TimeoutError()
        
        # Test data
        hook_data = {
            'tool': 'file_edit',
            'parameters': {'file': 'test.py'},
            'context': {}
        }
        
        # Execute
        allow, message = await bridge.pre_tool_validation(hook_data)
        
        # Verify - should fail open with warning
        assert allow is True  # Fail open on timeout
        assert 'timeout' in message.lower()
        assert bridge.metrics['errors'] == 1
    
    @pytest.mark.asyncio
    async def test_pre_tool_validation_server_error(self, bridge, mock_session):
        """Test PreToolUse validation with server error."""
        # Alex Novak: Test graceful degradation
        bridge.session = mock_session
        
        # Mock server error
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        # Test data
        hook_data = {
            'tool': 'file_edit',
            'parameters': {'file': 'test.py'},
            'context': {}
        }
        
        # Execute
        allow, message = await bridge.pre_tool_validation(hook_data)
        
        # Verify - should fail open with warning
        assert allow is True
        assert 'unavailable' in message.lower()
        assert bridge.metrics['errors'] == 1
    
    @pytest.mark.asyncio
    async def test_user_prompt_context_injection(self, bridge, mock_session):
        """Test UserPromptSubmit context injection."""
        bridge.session = mock_session
        
        # Mock context response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'active_policies': 'strict',
            'compliance_level': '95%',
            'restrictions': ['no production changes', 'require tests'],
            'recommendations': ['use TDD', 'add documentation']
        })
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        # Test data
        hook_data = {
            'prompt': 'Help me refactor this code',
            'context': {'file': 'main.py'}
        }
        
        # Execute
        context = await bridge.user_prompt_context_injection(hook_data)
        
        # Verify
        assert '[Governance Context]' in context
        assert 'strict' in context
        assert '95%' in context
        assert 'no production changes' in context
    
    @pytest.mark.asyncio
    async def test_post_tool_audit(self, bridge, mock_session):
        """Test PostToolUse audit logging."""
        bridge.session = mock_session
        
        # Mock audit response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        # Test data
        hook_data = {
            'tool': 'file_edit',
            'parameters': {'file': 'test.py'},
            'result': {'success': True, 'lines_changed': 10},
            'exit_code': 0
        }
        
        # Execute
        await bridge.post_tool_audit(hook_data)
        
        # Verify audit was sent
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert '/audit_execution' in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_metrics_calculation(self, bridge):
        """Test metrics calculation."""
        # Set some metrics
        bridge.metrics = {
            'total_validations': 100,
            'blocks': 10,
            'allows': 85,
            'errors': 5,
            'avg_response_time': 0.045
        }
        
        # Get metrics
        metrics = await bridge.get_metrics()
        
        # Verify calculations
        assert metrics['avg_response_time_ms'] == 45.0
        assert metrics['block_rate'] == 0.1  # 10/100
        assert metrics['error_rate'] == 0.05  # 5/100


class TestHookHandlers:
    """Test suite for hook handlers module."""
    
    def test_parse_hook_input_with_argv(self):
        """Test parsing hook input from command line."""
        # Mock sys.argv
        with patch.object(sys, 'argv', ['hook_handlers.py', 'PreToolUse', '{"tool": "bash"}']):
            with patch('sys.stdin.isatty', return_value=True):
                hook_type, hook_data, correlation_id = parse_hook_input()
        
        assert hook_type == 'PreToolUse'
        assert hook_data['tool'] == 'bash'
        assert 'correlation_id' in hook_data
    
    def test_parse_hook_input_no_type(self):
        """Test parsing with missing hook type."""
        with patch.object(sys, 'argv', ['hook_handlers.py']):
            hook_type, hook_data, correlation_id = parse_hook_input()
        
        assert hook_type is None
        assert hook_data == {}
        assert correlation_id  # Should still have correlation ID
    
    def test_format_hook_response_allow(self):
        """Test formatting allow response."""
        result = {
            'allow': True,
            'message': 'Test allowed'
        }
        
        formatted = format_hook_response(result, 'test-correlation-id')
        parsed = json.loads(formatted)
        
        assert parsed['exit_code'] == 0
        assert parsed['correlation_id'] == 'test-correlation-id'
        assert 'timestamp' in parsed
    
    def test_format_hook_response_block(self):
        """Test formatting block response."""
        result = {
            'exit_code': 2,
            'message': 'Blocked by policy'
        }
        
        formatted = format_hook_response(result, 'test-correlation-id')
        parsed = json.loads(formatted)
        
        assert parsed['exit_code'] == 2
        assert parsed['blocked'] is True
        assert 'executive_summary' in parsed
    
    @pytest.mark.asyncio
    async def test_handle_with_fallback_success(self):
        """Test handle_with_fallback with successful bridge call."""
        hook_data = {'tool': 'file_edit'}
        
        with patch('apps.api.mcp.claude_code_hook_bridge.handle_claude_code_hook') as mock_handle:
            mock_handle.return_value = {
                'allow': True,
                'exit_code': 0,
                'message': 'Allowed'
            }
            
            result = await handle_with_fallback('PreToolUse', hook_data, 'test-id')
        
        assert result['exit_code'] == 0
        assert result['message'] == 'Allowed'
    
    @pytest.mark.asyncio
    async def test_handle_with_fallback_timeout(self):
        """Test handle_with_fallback with timeout."""
        # Dr. Sarah Chen: Critical test - timeouts are our most common failure
        hook_data = {'tool': 'file_edit'}
        
        with patch('apps.api.mcp.claude_code_hook_bridge.handle_claude_code_hook') as mock_handle:
            # Simulate timeout
            async def timeout_func(*args):
                await asyncio.sleep(10)  # Longer than timeout
            mock_handle.side_effect = timeout_func
            
            result = await handle_with_fallback('PreToolUse', hook_data, 'test-id')
        
        assert result['exit_code'] == 0  # Fail open
        assert result['fallback'] is True
        assert 'timeout' in result['warning'].lower()
        assert result['elapsed_ms'] == 5000
    
    @pytest.mark.asyncio  
    async def test_handle_with_fallback_import_error(self):
        """Test handle_with_fallback when bridge module not available."""
        # Alex Novak: Test deployment scenarios where bridge isn't installed
        hook_data = {'tool': 'file_edit'}
        
        with patch('builtins.__import__', side_effect=ImportError('Module not found')):
            result = await handle_with_fallback('PreToolUse', hook_data, 'test-id')
        
        assert result['exit_code'] == 0  # Don't block
        assert result['fallback'] is True
        assert 'not available' in result['warning']


class TestEndToEndIntegration:
    """End-to-end integration tests."""
    
    @pytest.mark.asyncio
    async def test_full_pretooluse_flow(self):
        """Test complete PreToolUse flow from hook to response."""
        # Setup mock MCP server response
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'approved': True,
                'confidence': 0.9,
                'recommendations': ['Add tests'],
                'warnings': []
            })
            mock_session.post.return_value.__aenter__.return_value = mock_response
            
            # Test complete flow
            result = await handle_claude_code_hook('PreToolUse', {
                'tool': 'file_edit',
                'parameters': {'file': 'test.py'}
            })
            
            assert result['allow'] is True
            assert result['exit_code'] == 0
            assert 'Add tests' in result['message']
    
    @pytest.mark.asyncio
    async def test_full_blocking_flow(self):
        """Test complete flow that blocks execution."""
        # Alex Novak: Critical test - ensure blocking works end-to-end
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'approved': False,
                'confidence': 0.99,
                'block_reason': 'Security violation',
                'remediation': 'Contact security team'
            })
            mock_session.post.return_value.__aenter__.return_value = mock_response
            
            # Test complete flow
            result = await handle_claude_code_hook('PreToolUse', {
                'tool': 'bash',
                'parameters': {'command': 'sudo rm -rf /'}
            })
            
            assert result['allow'] is False
            assert result['exit_code'] == 2  # Exit code 2 blocks
            assert 'BLOCKED' in result['message']
            assert 'Security violation' in result['message']


# Performance tests
class TestPerformance:
    """Performance and load tests."""
    
    @pytest.mark.asyncio
    async def test_response_time_under_load(self):
        """Test response time remains under 50ms target."""
        # Dr. Sarah Chen: Performance is critical for hook response
        bridge = ClaudeCodeGovernanceBridge()
        
        with patch.object(bridge, 'session') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'approved': True,
                'confidence': 0.9
            })
            mock_session.post.return_value.__aenter__.return_value = mock_response
            
            # Run 100 validations
            import time
            start = time.time()
            
            for _ in range(100):
                await bridge.pre_tool_validation({
                    'tool': 'file_edit',
                    'parameters': {}
                })
            
            elapsed = time.time() - start
            avg_time = (elapsed / 100) * 1000  # Convert to ms
            
            # Should average under 50ms
            assert avg_time < 50, f"Average response time {avg_time}ms exceeds 50ms target"
    
    @pytest.mark.asyncio
    async def test_cache_effectiveness(self):
        """Test that caching improves performance."""
        bridge = ClaudeCodeGovernanceBridge()
        
        with patch.object(bridge, 'session') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'approved': True,
                'confidence': 0.9
            })
            mock_session.post.return_value.__aenter__.return_value = mock_response
            
            # Same request multiple times
            hook_data = {
                'tool': 'file_edit',
                'parameters': {'file': 'test.py'}
            }
            
            # First call - cache miss
            await bridge.pre_tool_validation(hook_data)
            assert bridge.metrics['cache_misses'] == 1
            
            # Second call - cache hit
            await bridge.pre_tool_validation(hook_data)
            assert bridge.metrics['cache_hits'] == 1
            
            # Verify MCP server only called once
            assert mock_session.post.call_count == 1


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])