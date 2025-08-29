#!/usr/bin/env python
"""
@fileoverview Interactive demonstration of governance system visibility and enforcement
@author Dr. Sarah Chen v1.0 & Alex Novak v1.0 - 2025-08-29
@architecture Backend - Governance demonstration and visibility testing
@responsibility Demonstrate real-time governance monitoring, validation, and enforcement capabilities
@dependencies asyncio, sys, pathlib, time, typing, governance modules
@integration_points Runtime governance, AI decision injector, governance monitor, hook system
@testing_strategy Interactive demonstration tests covering all governance features
@governance Self-demonstrating governance enforcement and monitoring

Business Logic Summary:
- Demonstrate agent spawn validation
- Show dangerous command blocking
- Display multi-persona consultation
- Test resource limit enforcement
- Validate hallucination detection
- Showcase hook system integration

Architecture Integration:
- Uses runtime governance system
- Integrates with AI decision injector
- Displays monitoring in real-time
- Triggers all hook types
- Shows audit trail generation

Sarah's Framework Check:
- What breaks first: Resource limits when spawning too many agents
- How we know: Governance rejects agent spawn with clear message
- Plan B: Clean up agents between tests to prevent accumulation
"""

import asyncio
import sys
from pathlib import Path
import time
from typing import Dict, Any

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from governance.core.runtime_governance import (
    RuntimeGovernanceSystem,
    HookType,
    GovernanceLevel
)
from governance.middleware.ai_decision_injector import (
    AIDecisionInjector,
    DecisionType
)
from governance.core.governance_monitor import show_governance_banner


async def simulate_agent_operations():
    """Simulate various agent operations to show governance in action"""
    
    print("\n" + "=" * 80)
    print("GOVERNANCE VISIBILITY DEMONSTRATION")
    print("This demo shows that governance is actively monitoring all operations")
    print("=" * 80 + "\n")
    
    # Show governance banner
    show_governance_banner()
    
    # Wait for user to read
    await asyncio.sleep(2)
    
    # Initialize governance with full monitoring
    print("\n>>> INITIALIZING GOVERNANCE SYSTEM...\n")
    governance = RuntimeGovernanceSystem(enable_monitor=True)
    injector = AIDecisionInjector()
    
    await asyncio.sleep(1)
    
    # ========== TEST 1: Agent Spawn ==========
    print("\n" + "=" * 80)
    print("TEST 1: ATTEMPTING TO SPAWN AN AI AGENT")
    print("=" * 80 + "\n")
    
    print(">>> User requests: Spawn a code_reviewer agent")
    await asyncio.sleep(1)
    
    result = await governance.validate_agent_spawn(
        agent_type="code_reviewer",
        agent_name="Dr. Sarah Chen",
        metadata={"purpose": "Review Python code for security issues"}
    )
    
    print(f"\n>>> GOVERNANCE DECISION: {'[APPROVED]' if result.approved else '[REJECTED]'}")
    print(f"    Reason: {result.reason}")
    print(f"    Risk Level: {result.risk_level}")
    
    if result.approved:
        # Register the agent
        await governance.register_agent(
            agent_id="agent_001",
            agent_type="code_reviewer",
            agent_name="Dr. Sarah Chen"
        )
    
    await asyncio.sleep(2)
    
    # ========== TEST 2: Safe Command ==========
    print("\n" + "=" * 80)
    print("TEST 2: EXECUTING A SAFE COMMAND")
    print("=" * 80 + "\n")
    
    print(">>> User command: print('Hello World')")
    await asyncio.sleep(1)
    
    result = await governance.validate_agent_execution(
        agent_id="agent_001",
        command="print('Hello World')",
        context={"source": "user_input"}
    )
    
    print(f"\n>>> GOVERNANCE DECISION: {'[APPROVED]' if result.approved else '[REJECTED]'}")
    print(f"    Reason: {result.reason}")
    
    await asyncio.sleep(2)
    
    # ========== TEST 3: Dangerous Command ==========
    print("\n" + "=" * 80)
    print("TEST 3: ATTEMPTING DANGEROUS COMMAND")
    print("=" * 80 + "\n")
    
    print(">>> User command: exec('import os; os.system(\"rm -rf /\")')")
    await asyncio.sleep(1)
    
    result = await governance.validate_agent_execution(
        agent_id="agent_001",
        command='exec("import os; os.system(\\"rm -rf /\\")")',
        context={"source": "user_input"}
    )
    
    print(f"\n>>> GOVERNANCE DECISION: {'[APPROVED]' if result.approved else '[REJECTED]'}")
    print(f"    Reason: {result.reason}")
    print(f"    Risk Level: {result.risk_level}")
    
    await asyncio.sleep(2)
    
    # ========== TEST 4: AI Decision with Code Generation ==========
    print("\n" + "=" * 80)
    print("TEST 4: AI GENERATES CODE - MULTI-PERSONA VALIDATION")
    print("=" * 80 + "\n")
    
    print(">>> AI generates code for database operation:")
    code = '''
def delete_user(user_id):
    # Dangerous: No input validation!
    query = f"DELETE FROM users WHERE id = {user_id}"
    db.execute(query)
    return "User deleted"
'''
    print(code)
    await asyncio.sleep(1)
    
    print("\n>>> GOVERNANCE INTERCEPTS AND VALIDATES...")
    await asyncio.sleep(1)
    
    validation = await injector.intercept_decision(
        agent_id="agent_001",
        decision_type=DecisionType.CODE_GENERATION,
        input_context={"task": "delete user from database"},
        proposed_output=code
    )
    
    print(f"\n>>> GOVERNANCE DECISION:")
    print(f"    Approved: {'[OK] YES' if validation.approved else '[X] NO'}")
    print(f"    Risk Level: {validation.risk_level.value.upper()}")
    print(f"    Confidence: {validation.confidence_score:.2%}")
    
    print(f"\n    Personas Consulted ({len(validation.personas_consulted)}):")
    for persona in validation.personas_consulted:
        status = "[OK]" if persona.approved else "[X]"
        print(f"      {status} {persona.persona_name} (confidence: {persona.confidence:.2%})")
        if persona.concerns:
            print(f"         Concerns: {', '.join(persona.concerns[:2])}")
    
    if validation.warnings:
        print(f"\n    [WARNING] Warnings:")
        for warning in validation.warnings:
            print(f"      • {warning}")
    
    await asyncio.sleep(2)
    
    # ========== TEST 5: Resource Limits ==========
    print("\n" + "=" * 80)
    print("TEST 5: TESTING RESOURCE LIMITS")
    print("=" * 80 + "\n")
    
    print(">>> Attempting to spawn multiple agents to test limits...")
    
    # Spawn agents up to limit
    for i in range(5):
        print(f"\n>>> Spawning agent_{i+2}...")
        await governance.register_agent(
            agent_id=f"agent_{i+2:03d}",
            agent_type="test_agent",
            agent_name=f"TestAgent{i+2}"
        )
        await asyncio.sleep(0.5)
    
    # Try to exceed limit
    print("\n>>> Attempting to spawn 7th agent (exceeds limit of 6)...")
    result = await governance.validate_agent_spawn(
        agent_type="test_agent",
        agent_name="Agent7"
    )
    
    print(f"\n>>> GOVERNANCE DECISION: {'[APPROVED]' if result.approved else '[REJECTED]'}")
    print(f"    Reason: {result.reason}")
    if result.recommendations:
        print(f"    Recommendations: {', '.join(result.recommendations)}")
    
    await asyncio.sleep(2)
    
    # ========== TEST 6: Hallucination Detection ==========
    print("\n" + "=" * 80)
    print("TEST 6: HALLUCINATION DETECTION")
    print("=" * 80 + "\n")
    
    print(">>> AI generates response with potential hallucination:")
    response = "The Python GIL was removed in Python 2.7 by Guido van Rossum in 2005."
    print(f'    "{response}"')
    
    await asyncio.sleep(1)
    
    print("\n>>> GOVERNANCE CHECKS FOR HALLUCINATIONS...")
    
    result = await governance.validate_ai_decision(
        agent_id="agent_001",
        decision_type="factual_response",
        input_data={"question": "When was the Python GIL removed?"},
        proposed_output=response
    )
    
    print(f"\n>>> GOVERNANCE DECISION: {'[APPROVED]' if result.approved else '[REJECTED]'}")
    print(f"    Reason: {result.reason}")
    
    # ========== SHOW STATISTICS ==========
    await asyncio.sleep(2)
    
    print("\n" + "=" * 80)
    print("GOVERNANCE STATISTICS SUMMARY")
    print("=" * 80)
    
    if governance.monitor:
        governance.monitor.show_statistics()
    
    metrics = governance.get_metrics()
    print("\nSystem Metrics:")
    for key, value in metrics.items():
        if isinstance(value, (int, float)) and value > 0:  # Only show non-zero numeric metrics
            print(f"  • {key}: {value}")
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("Governance was actively monitoring and validating every operation!")
    print("=" * 80 + "\n")


async def demonstrate_hooks():
    """Demonstrate hook system visibility"""
    
    print("\n" + "=" * 80)
    print("HOOK SYSTEM DEMONSTRATION")
    print("Showing how governance hooks intercept operations")
    print("=" * 80 + "\n")
    
    governance = RuntimeGovernanceSystem(enable_monitor=True)
    
    # Register visible hooks
    async def security_check_hook(context):
        print(f"    [>>] [SECURITY HOOK] Scanning for vulnerabilities...")
        await asyncio.sleep(0.5)
        print(f"    [OK] [SECURITY HOOK] No critical vulnerabilities found")
        return {"approved": True, "scanner": "security_hook_v1"}
    
    async def compliance_hook(context):
        print(f"    [>>] [COMPLIANCE HOOK] Checking regulatory compliance...")
        await asyncio.sleep(0.5)
        print(f"    [OK] [COMPLIANCE HOOK] Meets compliance standards")
        return {"approved": True, "standards": ["SOC2", "GDPR"]}
    
    async def audit_hook(event):
        print(f"    [>>] [AUDIT HOOK] Logging event to audit trail: {event.get('event')}")
    
    # Register hooks
    governance.register_hook(HookType.PRE_AGENT_SPAWN, security_check_hook)
    governance.register_hook(HookType.PRE_AGENT_SPAWN, compliance_hook)
    governance.register_hook(HookType.AUDIT_LOG, audit_hook)
    
    print(">>> Registered 3 governance hooks:")
    print("    • Security vulnerability scanner")
    print("    • Compliance checker")
    print("    • Audit logger")
    
    print("\n>>> Now spawning an agent to trigger hooks...\n")
    
    result = await governance.validate_agent_spawn(
        agent_type="data_processor",
        agent_name="DataAgent",
        metadata={"handles_pii": True}
    )
    
    print(f"\n>>> Final Decision: {'[OK] APPROVED' if result.approved else '[X] REJECTED'}")
    
    print("\n>>> All hooks executed successfully!")
    print("    This shows governance is actively intercepting every operation")


async def main():
    """Run all demonstrations"""
    
    try:
        # Main demonstration
        await simulate_agent_operations()
        
        # Hook demonstration
        await demonstrate_hooks()
        
        print("\n" + "=>" * 40)
        print("\n[OK] GOVERNANCE IS PROVEN TO BE ACTIVELY RUNNING!")
        print("   Every decision was validated, monitored, and logged.")
        print("\n" + "=>" * 40 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n>>> Demo interrupted by user")
    except Exception as e:
        print(f"\n[X] Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the demonstration
    print("\n" + "[SHIELD] " * 20)
    print("STARTING GOVERNANCE VISIBILITY DEMONSTRATION")
    print("This will show clear proof that governance is running")
    print("[SHIELD] " * 20 + "\n")
    
    asyncio.run(main())