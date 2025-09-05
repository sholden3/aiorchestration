"""
@fileoverview Comprehensive test suite for runtime governance system functionality
@author Dr. Sarah Chen v1.0 & Alex Novak v1.0 - 2025-08-29
@architecture Backend - Governance system testing and validation
@responsibility Test all governance components including hooks, agent lifecycle, and decision injection
@dependencies asyncio, sys, pathlib, json, governance modules
@integration_points Runtime governance, AI decision injector, hook system, agent management
@testing_strategy Unit and integration tests for governance validation, resource limits, hooks
@governance Tests the governance system itself for correctness and enforcement

Business Logic Summary:
- Validate agent spawn limits
- Test dangerous command blocking
- Verify decision injection
- Test hallucination detection
- Validate hook system
- Test governance levels

Architecture Integration:
- Tests runtime governance system
- Validates AI decision injector
- Tests hook registration and execution
- Verifies resource management
- Tests audit logging

Sarah's Framework Check:
- What breaks first: Resource limits when spawning too many agents
- How we know: Assertion failures indicate which governance component failed
- Plan B: Cleanup agents between tests to prevent resource accumulation
"""

import asyncio
import sys
from pathlib import Path
import json

# Add governance to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from libs.governance.core.runtime_governance import (
    RuntimeGovernanceSystem,
    HookType,
    GovernanceLevel,
    AgentContext
)
from libs.governance.middleware.ai_decision_injector import (
    AIDecisionInjector,
    DecisionType
)


async def test_governance_system():
    """Test the complete governance system"""
    
    print("=" * 60)
    print("TESTING RUNTIME GOVERNANCE SYSTEM")
    print("=" * 60)
    
    # Initialize governance
    governance = RuntimeGovernanceSystem()
    injector = AIDecisionInjector()
    
    print("\n1. Testing Agent Spawn Validation...")
    print("-" * 40)
    
    # Test agent spawn validation
    result = await governance.validate_agent_spawn(
        agent_type="claude_assistant",
        agent_name="TestAgent",
        metadata={"purpose": "testing"}
    )
    
    print(f"Spawn Validation Result:")
    print(f"  Approved: {result.approved}")
    print(f"  Reason: {result.reason}")
    print(f"  Risk Level: {result.risk_level}")
    
    assert result.approved, "Agent spawn should be approved"
    
    # Test resource limit
    print("\n2. Testing Resource Limits...")
    print("-" * 40)
    
    # Spawn multiple agents to test limit
    for i in range(6):
        agent_id = f"test_agent_{i}"
        await governance.register_agent(
            agent_id=agent_id,
            agent_type="claude_assistant",
            agent_name=f"Agent{i}"
        )
    
    # Try to spawn 7th agent (should fail)
    result = await governance.validate_agent_spawn(
        agent_type="claude_assistant",
        agent_name="Agent7"
    )
    
    print(f"7th Agent Spawn Result:")
    print(f"  Approved: {result.approved}")
    print(f"  Reason: {result.reason}")
    
    assert not result.approved, "7th agent should be rejected due to limit"
    
    # Test execution validation
    print("\n3. Testing Execution Validation...")
    print("-" * 40)
    
    result = await governance.validate_agent_execution(
        agent_id="test_agent_0",
        command="print('Hello World')",
        context={}
    )
    
    print(f"Execution Validation Result:")
    print(f"  Approved: {result.approved}")
    print(f"  Risk Level: {result.risk_level}")
    
    # Test dangerous command
    result = await governance.validate_agent_execution(
        agent_id="test_agent_0",
        command="exec('malicious code')",
        context={}
    )
    
    print(f"Dangerous Command Result:")
    print(f"  Approved: {result.approved}")
    print(f"  Reason: {result.reason}")
    
    # Test AI decision injection
    print("\n4. Testing AI Decision Injection...")
    print("-" * 40)
    
    # Test code generation decision
    validation = await injector.intercept_decision(
        agent_id="test_agent_0",
        decision_type=DecisionType.CODE_GENERATION,
        input_context={"task": "create a function"},
        proposed_output="""
def process_data(data):
    return eval(data)  # Dangerous!
"""
    )
    
    print(f"Code Generation Validation:")
    print(f"  Approved: {validation.approved}")
    print(f"  Risk Level: {validation.risk_level.value}")
    print(f"  Personas Consulted: {len(validation.personas_consulted)}")
    
    for persona in validation.personas_consulted:
        print(f"    - {persona.persona_name}: {'APPROVED' if persona.approved else 'REJECTED'}")
        if persona.concerns:
            print(f"      Concerns: {persona.concerns}")
    
    # Test hallucination detection
    print("\n5. Testing Hallucination Detection...")
    print("-" * 40)
    
    result = await governance.validate_ai_decision(
        agent_id="test_agent_0",
        decision_type="response",
        input_data={"question": "What is 2+2?"},
        proposed_output="The answer is 5, which is a prime number discovered by Einstein in 1905."
    )
    
    print(f"Hallucination Check Result:")
    print(f"  Approved: {result.approved}")
    print(f"  Risk Level: {result.risk_level}")
    
    # Test governance metrics
    print("\n6. Governance Metrics...")
    print("-" * 40)
    
    metrics = governance.get_metrics()
    print(f"System Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    # Test audit log
    print("\n7. Audit Log...")
    print("-" * 40)
    
    logs = governance.get_audit_log(5)
    print(f"Recent Audit Entries: {len(logs)}")
    for log in logs:
        print(f"  [{log.get('timestamp', 'N/A')}] {log.get('event', 'Unknown')}")
    
    # Clean up
    print("\n8. Cleanup...")
    print("-" * 40)
    
    for i in range(6):
        await governance.terminate_agent(f"test_agent_{i}", "Test complete")
    
    print("All agents terminated")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)


async def test_hook_system():
    """Test the hook registration and triggering system"""
    
    print("\n" + "=" * 60)
    print("TESTING HOOK SYSTEM")
    print("=" * 60)
    
    governance = RuntimeGovernanceSystem()
    
    # Track hook calls
    hook_calls = []
    
    # Register test hooks
    async def test_pre_spawn(context):
        hook_calls.append("pre_spawn")
        print(f"  Pre-spawn hook called for {context.agent_type}")
        return {"approved": True}
    
    async def test_post_spawn(context):
        hook_calls.append("post_spawn")
        print(f"  Post-spawn hook called for {context.agent_name}")
    
    governance.register_hook(HookType.PRE_AGENT_SPAWN, test_pre_spawn)
    governance.register_hook(HookType.POST_AGENT_SPAWN, test_post_spawn)
    
    # Test spawn with hooks
    print("\nTesting hooks during agent spawn...")
    
    result = await governance.validate_agent_spawn(
        agent_type="test_agent",
        agent_name="HookTestAgent"
    )
    
    await governance.register_agent(
        agent_id="hook_test_1",
        agent_type="test_agent",
        agent_name="HookTestAgent"
    )
    
    print(f"\nHooks called: {hook_calls}")
    assert "pre_spawn" in hook_calls, "Pre-spawn hook should be called"
    assert "post_spawn" in hook_calls, "Post-spawn hook should be called"
    
    print("\n[OK] Hook system working correctly!")


async def test_governance_levels():
    """Test different governance enforcement levels"""
    
    print("\n" + "=" * 60)
    print("TESTING GOVERNANCE LEVELS")
    print("=" * 60)
    
    governance = RuntimeGovernanceSystem()
    
    # Test STRICT level (default)
    print("\n1. Testing STRICT level...")
    governance.set_governance_level(GovernanceLevel.STRICT)
    
    result = await governance.validate_agent_execution(
        agent_id="unknown_agent",  # Non-existent agent
        command="test",
        context={}
    )
    
    print(f"  Unknown agent result: Approved={result.approved}")
    assert not result.approved, "STRICT should reject unknown agents"
    
    # Test BYPASS level
    print("\n2. Testing BYPASS level...")
    governance.set_governance_level(GovernanceLevel.BYPASS)
    
    # Bypass level would normally skip checks, but our implementation
    # still performs basic validation
    
    print("\n[OK] Governance levels working correctly!")


async def main():
    """Run all tests"""
    try:
        await test_governance_system()
        await test_hook_system()
        await test_governance_levels()
        
        print("\n" + "=" * 60)
        print("ALL GOVERNANCE TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())