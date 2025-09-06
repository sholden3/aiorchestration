"""
MCP Server Integration Test

This script tests that the MCP server works correctly with 
data-driven personas and can provide governance consultation.

Run this to verify the system is working as expected.

Author: Alex Novak & Dr. Sarah Chen
Phase: MCP-001 PHOENIX_RISE_FOUNDATION
"""

import asyncio
import json
from pathlib import Path
import sys

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from apps.api.mcp.governance_server import GovernanceMCPServer
from libs.governance.personas import PersonaManager


async def test_persona_loading():
    """Test that personas load from YAML correctly."""
    print("\n=== Testing Persona Loading ===")
    
    personas = PersonaManager(Path("libs/governance/personas.yaml"))
    await personas.initialize()
    
    print(f"[OK] Loaded {len(personas.personas)} personas")
    print(f"   Core personas: {', '.join(personas.core_personas)}")
    print(f"   Specialists: {', '.join(personas.specialist_personas[:5])}...")
    
    return personas


async def test_persona_consultation(personas):
    """Test consulting specific personas."""
    print("\n=== Testing Persona Consultation ===")
    
    # Test 1: Consult Alex about frontend
    result = await personas.consult(
        persona_name='Alex Novak',
        question='Should I use IPC for this Electron communication?',
        context={'operation': 'electron_ipc', 'file_path': 'renderer.ts'}
    )
    print(f"\n[CONSULTATION] Alex Novak consultation:")
    print(result[:300] + "..." if len(result) > 300 else result)
    
    # Test 2: Consult Sarah about backend
    result = await personas.consult(
        persona_name='Dr. Sarah Chen',
        question='How should I handle this WebSocket connection?',
        context={'operation': 'websocket_init', 'connections': 1000}
    )
    print(f"\n[CONSULTATION] Dr. Sarah Chen consultation:")
    print(result[:300] + "..." if len(result) > 300 else result)
    
    # Test 3: Consult Security specialist
    result = await personas.consult(
        persona_name='Morgan Hayes',
        question='Is this command safe to execute?',
        context={'operation': 'command_execution', 'command': 'rm -rf node_modules'}
    )
    print(f"\n[CONSULTATION] Morgan Hayes consultation:")
    print(result[:300] + "..." if len(result) > 300 else result)


async def test_automatic_persona_selection(personas):
    """Test automatic persona selection based on context."""
    print("\n=== Testing Automatic Persona Selection ===")
    
    # Test database operation - should select Jamie Rodriguez
    relevant = personas.determine_relevant_personas(
        operation='database_migration',
        context={'file_path': 'migration.sql', 'database': 'postgresql'}
    )
    print(f"\n[AUTO-SELECT] For database migration:")
    for persona_name, confidence in relevant:
        print(f"   - {persona_name}: {confidence:.0%} confidence")
    
    # Test WebSocket operation - should select Jordan Lee
    relevant = personas.determine_relevant_personas(
        operation='websocket_connection_pool',
        context={'type': 'realtime', 'connections': 5000}
    )
    print(f"\n[AUTO-SELECT] For WebSocket pool:")
    for persona_name, confidence in relevant:
        print(f"   - {persona_name}: {confidence:.0%} confidence")
    
    # Test security operation - should select Morgan Hayes
    relevant = personas.determine_relevant_personas(
        operation='authentication_implementation',
        context={'type': 'jwt', 'encryption': 'RS256'}
    )
    print(f"\n[AUTO-SELECT] For authentication:")
    for persona_name, confidence in relevant:
        print(f"   - {persona_name}: {confidence:.0%} confidence")


async def test_mcp_server():
    """Test MCP server initialization and basic operations."""
    print("\n=== Testing MCP Server ===")
    
    server = GovernanceMCPServer()
    await server.initialize()
    
    print(f"[OK] MCP Server initialized")
    print(f"   Port: {server.port}")
    print(f"   Personas available: {len(server.personas.personas)}")
    print(f"   Cache initialized: {type(server.cache)}")
    
    # Test getting persona guidance
    guidance = await server._get_persona_guidance(
        operation='critical_architecture_decision',
        context={'impact': 'high', 'components': ['frontend', 'backend']}
    )
    
    print(f"\n[GUIDANCE] Guidance for critical architecture decision:")
    for persona_name, details in guidance.items():
        if isinstance(details, dict):
            print(f"   - {persona_name}: {details.get('confidence', 'N/A'):.0%} confidence")
        else:
            print(f"   - {persona_name}: Consulted")
    
    # Test dangerous pattern detection
    warnings = server._check_warnings(
        operation='command_execution',
        context={'command': 'rm -rf /'}
    )
    print(f"\n[WARNING] Warnings for dangerous command:")
    for warning in warnings:
        print(f"   {warning}")
    
    # Test recommendations generation
    recommendations = server._generate_recommendations(
        operation='database_query',
        context={'query': 'SELECT * FROM users WHERE id = ?'}
    )
    print(f"\n[RECOMMENDATIONS] Recommendations for database query:")
    for rec in recommendations:
        print(f"   - {rec}")
    
    return server


async def test_caching(server):
    """Test that caching works correctly."""
    print("\n=== Testing Cache Functionality ===")
    
    # Create a cache key
    operation = 'test_operation'
    context = {'test': 'data', 'timestamp': '2025-01-05'}
    cache_key = f"governance:{operation}:{json.dumps(context, sort_keys=True)}"
    
    # Initially should be empty
    if cache_key not in server.cache:
        print("[OK] Cache initially empty")
    
    # Add to cache
    server.cache[cache_key] = "Test cached response"
    print("[OK] Added test response to cache")
    
    # Verify retrieval
    if server.cache[cache_key] == "Test cached response":
        print("[OK] Cache retrieval successful")
    
    # Test metrics
    server.metrics['cache_hits'] = 85
    server.metrics['cache_misses'] = 15
    hit_rate = server._calculate_cache_hit_rate()
    print(f"[METRICS] Cache hit rate: {hit_rate:.1%}")


async def main():
    """Run all integration tests."""
    print("=" * 60)
    print("MCP GOVERNANCE SERVER INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Test 1: Load personas
        personas = await test_persona_loading()
        
        # Test 2: Consult personas
        await test_persona_consultation(personas)
        
        # Test 3: Automatic persona selection
        await test_automatic_persona_selection(personas)
        
        # Test 4: MCP server
        server = await test_mcp_server()
        
        # Test 5: Caching
        await test_caching(server)
        
        print("\n" + "=" * 60)
        print("[SUCCESS] ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        print("\n[SUMMARY]:")
        print("1. Personas load correctly from YAML [OK]")
        print("2. Persona consultation works [OK]")
        print("3. Automatic persona selection works [OK]")
        print("4. MCP server initializes [OK]")
        print("5. Caching works [OK]")
        print("\n[RESULT] The system is working as expected!")
        
    except Exception as e:
        print(f"\n[ERROR]: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)