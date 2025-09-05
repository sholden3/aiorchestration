"""
Test Suite for MCP Governance Server

Validates that the MCP server works correctly with data-driven personas
and provides expected governance consultation.

Author: Alex Novak & Dr. Sarah Chen
Phase: MCP-001 PHOENIX_RISE_FOUNDATION
"""

import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps.api.mcp.governance_server import GovernanceMCPServer
from libs.governance.personas import PersonaManager


class TestMCPServer:
    """Test suite for MCP Governance Server."""
    
    @pytest.fixture
    async def mcp_server(self):
        """Create MCP server instance for testing."""
        server = GovernanceMCPServer()
        await server.initialize()
        return server
    
    @pytest.fixture
    def sample_context(self):
        """Sample context for testing."""
        return {
            'file_path': 'test.py',
            'operation': 'file_edit',
            'user': 'test_user'
        }
    
    @pytest.mark.asyncio
    async def test_server_initialization(self, mcp_server):
        """Test that server initializes correctly."""
        assert mcp_server.port is not None
        assert mcp_server.personas is not None
        assert len(mcp_server.personas.personas) > 0
        assert mcp_server.metrics['total_requests'] == 0
    
    @pytest.mark.asyncio
    async def test_persona_loading(self):
        """Test that personas load correctly from YAML."""
        personas = PersonaManager(Path("libs/governance/personas.yaml"))
        await personas.initialize()
        
        # Check core personas loaded
        assert 'Alex Novak' in personas.personas
        assert 'Dr. Sarah Chen' in personas.personas
        
        # Check specialist personas loaded
        assert 'Morgan Hayes' in personas.personas
        assert 'Jordan Lee' in personas.personas
        
        # Check persona details
        alex = personas.personas['Alex Novak']
        assert alex.role == "Senior Electron/Angular Architect"
        assert alex.persona_type == 'core'
        assert alex.always_present == True
    
    @pytest.mark.asyncio
    async def test_persona_consultation(self):
        """Test consulting a specific persona."""
        personas = PersonaManager(Path("libs/governance/personas.yaml"))
        await personas.initialize()
        
        # Test consulting Alex for frontend question
        result = await personas.consult(
            persona_name='Alex Novak',
            question='How should I handle IPC timeouts?',
            context={'operation': 'ipc_communication'}
        )
        
        assert 'Alex Novak' in result
        assert 'IPC' in result or 'timeout' in result.lower()
    
    @pytest.mark.asyncio
    async def test_relevant_persona_determination(self):
        """Test that relevant personas are determined correctly."""
        personas = PersonaManager(Path("libs/governance/personas.yaml"))
        await personas.initialize()
        
        # Test database operation triggers Jamie
        relevant = personas.determine_relevant_personas(
            operation='database_query',
            context={'query': 'SELECT * FROM users'}
        )
        
        persona_names = [p[0] for p in relevant]
        assert 'Dr. Jamie Rodriguez' in persona_names or 'Dr. Sarah Chen' in persona_names
        
        # Test security operation triggers Morgan
        relevant = personas.determine_relevant_personas(
            operation='authentication_check',
            context={'type': 'security'}
        )
        
        persona_names = [p[0] for p in relevant]
        assert 'Morgan Hayes' in persona_names
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, mcp_server):
        """Test that caching works correctly."""
        context = {'test': 'data'}
        operation = 'test_operation'
        
        # First call - should be cache miss
        cache_key = f"governance:{operation}:{json.dumps(context, sort_keys=True)}"
        assert cache_key not in mcp_server.cache
        
        # Simulate adding to cache
        mcp_server.cache[cache_key] = "cached_response"
        
        # Check cache hit
        assert mcp_server.cache[cache_key] == "cached_response"
        
    @pytest.mark.asyncio
    async def test_metrics_tracking(self, mcp_server):
        """Test that metrics are tracked correctly."""
        # Initial state
        assert mcp_server.metrics['total_requests'] == 0
        assert mcp_server.metrics['errors'] == 0
        
        # Simulate request
        mcp_server.metrics['total_requests'] += 1
        mcp_server.metrics['cache_hits'] += 1
        
        assert mcp_server.metrics['total_requests'] == 1
        assert mcp_server.metrics['cache_hits'] == 1
        
        # Test cache hit rate calculation
        hit_rate = mcp_server._calculate_cache_hit_rate()
        assert hit_rate == 1.0  # 100% hit rate (1 hit, 0 misses)
    
    @pytest.mark.asyncio
    async def test_dangerous_pattern_detection(self, mcp_server):
        """Test that dangerous patterns are detected."""
        warnings = mcp_server._check_warnings(
            operation='command_execution',
            context={'command': 'rm -rf /'}
        )
        
        assert len(warnings) > 0
        assert any('Dangerous pattern' in w for w in warnings)
    
    @pytest.mark.asyncio
    async def test_sensitive_file_detection(self, mcp_server):
        """Test that sensitive files are detected."""
        warnings = mcp_server._check_warnings(
            operation='file_edit',
            context={'file_path': '/home/user/.env'}
        )
        
        assert len(warnings) > 0
        assert any('Sensitive file' in w for w in warnings)
    
    @pytest.mark.asyncio
    async def test_recommendations_generation(self, mcp_server):
        """Test that recommendations are generated correctly."""
        # Test file operation recommendations
        recs = mcp_server._generate_recommendations(
            operation='file_edit',
            context={'file_path': 'test.py'}
        )
        
        assert len(recs) > 0
        assert any('backup' in r.lower() for r in recs)
        
        # Test database operation recommendations
        recs = mcp_server._generate_recommendations(
            operation='database_query',
            context={'sql': 'SELECT * FROM users'}
        )
        
        assert len(recs) > 0
        assert any('parameterized' in r.lower() for r in recs)
    
    @pytest.mark.asyncio
    async def test_mcp_config_generation(self, mcp_server):
        """Test that MCP configuration is generated correctly."""
        await mcp_server._generate_mcp_config()
        
        config_path = Path(".mcp.json")
        assert config_path.exists()
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert 'mcpServers' in config
        assert 'governance' in config['mcpServers']
        assert config['mcpServers']['governance']['command'] == 'python'
        
        # Clean up
        config_path.unlink(missing_ok=True)


class TestPersonaManager:
    """Test suite for PersonaManager."""
    
    @pytest.fixture
    def personas(self):
        """Create PersonaManager instance."""
        return PersonaManager(Path("libs/governance/personas.yaml"))
    
    @pytest.mark.asyncio
    async def test_yaml_loading(self, personas):
        """Test that YAML configuration loads correctly."""
        await personas.initialize()
        
        # Check metadata loaded
        assert personas.config.get('version') == '1.0.0'
        assert personas.config.get('metadata', {}).get('max_concurrent_personas') == 3
        
        # Check personas loaded
        assert len(personas.personas) > 10  # Should have at least 12 personas
        
    def test_pattern_matching(self, personas):
        """Test pattern matching functionality."""
        # Test exact match
        assert personas._matches_pattern('test.py', '*.py')
        assert not personas._matches_pattern('test.js', '*.py')
        
        # Test complex patterns
        assert personas._matches_pattern('src/app/test.ts', '**/app/*.ts')
        assert personas._matches_pattern('component.tsx', '*.tsx')
    
    def test_condition_evaluation(self, personas):
        """Test condition evaluation for invocation rules."""
        # Test 'in' condition
        assert personas._evaluate_condition(
            "'security' in operation",
            operation='security_check',
            context={}
        )
        
        # Test endswith condition
        assert personas._evaluate_condition(
            "file_path.endswith('.sql')",
            operation='edit',
            context={'file_path': 'query.sql'}
        )
        
        # Test equality condition
        assert personas._evaluate_condition(
            "operation == 'test'",
            operation='test',
            context={}
        )
    
    @pytest.mark.asyncio
    async def test_consultation_history(self, personas):
        """Test that consultation history is tracked."""
        await personas.initialize()
        
        # Initial state
        initial_count = len(personas.consultation_history)
        
        # Perform consultation
        await personas.consult(
            persona_name='Alex Novak',
            question='Test question',
            context={'test': 'data'}
        )
        
        # Check history updated
        assert len(personas.consultation_history) == initial_count + 1
        latest = personas.consultation_history[-1]
        assert latest['persona'] == 'Alex Novak'
        assert latest['question'] == 'Test question'


@pytest.mark.asyncio
async def test_end_to_end_consultation():
    """Test complete end-to-end consultation flow."""
    server = GovernanceMCPServer()
    await server.initialize()
    
    # Test consulting for a WebSocket operation (should trigger Jordan Lee)
    guidance = await server._get_persona_guidance(
        operation='websocket_connection',
        context={'type': 'realtime', 'connections': 100}
    )
    
    # Should have consulted Jordan Lee
    assert any('Jordan Lee' in key for key in guidance.keys())
    
    # Test consulting for database operation (should trigger Jamie Rodriguez)
    guidance = await server._get_persona_guidance(
        operation='database_migration',
        context={'type': 'migration', 'database': 'postgresql'}
    )
    
    # Should have consulted database specialist
    assert any('Jamie' in key or 'Sarah' in key for key in guidance.keys())


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])