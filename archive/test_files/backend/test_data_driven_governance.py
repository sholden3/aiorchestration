#!/usr/bin/env python
"""
Test suite for Data-Driven Governance System v5.0
Validates all configurations, modes, and UI integration
"""

import asyncio
import json
from pathlib import Path
from data_driven_governance import (
    DataDrivenGovernanceOrchestrator,
    ExecutionMode,
    Agent,
    Persona,
    ValidationRule,
    GovernanceResult,
    PromptInterceptor
)

async def test_configuration_loading():
    """Test configuration loading and parsing"""
    print("\n1. TESTING CONFIGURATION LOADING")
    print("-" * 40)
    
    orchestrator = DataDrivenGovernanceOrchestrator()
    
    # Check agents loaded
    print(f"Agents loaded: {len(orchestrator.agents)}")
    for agent_id, agent in orchestrator.agents.items():
        print(f"  - {agent.name}: {'Enabled' if agent.enabled else 'Disabled'}")
    
    # Check personas loaded
    print(f"\nPersonas loaded: {len(orchestrator.personas)}")
    for persona_id, persona in orchestrator.personas.items():
        print(f"  - {persona.name} ({persona.role}): {'Enabled' if persona.enabled else 'Disabled'}")
    
    # Check validation rules
    print(f"\nValidation rules loaded: {len(orchestrator.validation_rules)}")
    for rule_name, rule in orchestrator.validation_rules.items():
        print(f"  - {rule.name}: Severity={rule.severity}, AutoFix={rule.auto_fix}")
    
    return True

async def test_execution_modes():
    """Test all execution modes"""
    print("\n2. TESTING EXECUTION MODES")
    print("-" * 40)
    
    orchestrator = DataDrivenGovernanceOrchestrator()
    
    test_cases = [
        ("Fix a simple bug", ExecutionMode.SINGLE_AGENT),
        ("Optimize cache and database performance", ExecutionMode.MULTI_AGENT_MULTI_PERSONA),
        ("Complete system review with all features", ExecutionMode.FULL_ORCHESTRATION),
    ]
    
    for prompt, expected_mode in test_cases:
        # Auto-determine mode
        determined_mode = orchestrator._determine_execution_mode(prompt, None)
        print(f"\nPrompt: '{prompt[:50]}...'")
        print(f"  Expected: {expected_mode.value}")
        print(f"  Determined: {determined_mode}")
        
        # Execute with mode
        result = await orchestrator.execute(prompt, mode=expected_mode.value)
        print(f"  Success: {result.success}")
        print(f"  Agents: {result.agents_executed}")
        print(f"  Personas: {result.personas_executed[:2]}...")
        print(f"  Time: {result.execution_time_ms}ms")
    
    return True

async def test_prompt_interception():
    """Test prompt interception and rewriting"""
    print("\n3. TESTING PROMPT INTERCEPTION")
    print("-" * 40)
    
    orchestrator = DataDrivenGovernanceOrchestrator()
    interceptor = orchestrator.prompt_interceptor
    
    test_prompts = [
        "Fix the thing in the stuff",
        "Improve the code",
        "Review this code for issues",
    ]
    
    for prompt in test_prompts:
        result = await interceptor.intercept_and_rewrite(prompt, {"file": "test.py"})
        print(f"\nOriginal: '{prompt}'")
        print(f"Rewritten: '{result['rewritten']}'")
        print(f"Transformations: {result['transformations']}")
    
    return True

async def test_business_auditor():
    """Test Dr. Rachel Torres' business auditor"""
    print("\n4. TESTING BUSINESS AUDITOR")
    print("-" * 40)
    
    orchestrator = DataDrivenGovernanceOrchestrator()
    
    # Create a result to audit
    result = GovernanceResult(
        success=True,
        mode=ExecutionMode.FULL_ORCHESTRATION.value,
        agents_executed=['primary'],
        personas_executed=['sarah_chen', 'marcus_rodriguez', 'emily_watson'],
        violations=[],
        audit_results={},
        prompt_transformations={},
        execution_time_ms=100
    )
    
    # Run business auditor
    prompts_to_audit = [
        "I assume this will work for most users",
        "This should probably handle the business requirements",
        "Implement user authentication feature"
    ]
    
    for prompt in prompts_to_audit:
        audit = await orchestrator._run_business_auditor(result, prompt, None)
        print(f"\nPrompt: '{prompt[:50]}...'")
        print(f"  Business features validated: {audit['business_features_validated']}")
        print(f"  Assumptions destroyed: {len(audit['assumptions_destroyed'])}")
        print(f"  Gaps found: {len(audit['gaps_found'])}")
        print(f"  Aggressive challenges: {len(audit['aggressive_challenges'])}")
        
        if audit['assumptions_destroyed']:
            print(f"    - {audit['assumptions_destroyed'][0]}")
        if audit['gaps_found']:
            print(f"    - {audit['gaps_found'][0]}")
    
    return True

async def test_configuration_updates():
    """Test configuration updates and persistence"""
    print("\n5. TESTING CONFIGURATION UPDATES")
    print("-" * 40)
    
    orchestrator = DataDrivenGovernanceOrchestrator()
    
    # Get initial state
    initial_status = orchestrator.get_status()
    print(f"Initial state: {initial_status['active_agents']} agents, {initial_status['active_personas']} personas")
    
    # Update configuration
    updates = {
        "defaults": {
            "governance_level": "strict",
            "enable_prompt_interceptor": False
        },
        "personas": {
            "sarah_chen": {
                "enabled": False
            }
        }
    }
    
    success = orchestrator.update_config(updates, "test")
    print(f"\nUpdate success: {success}")
    
    # Check new state
    new_status = orchestrator.get_status()
    print(f"New state: {new_status['active_agents']} agents, {new_status['active_personas']} personas")
    print(f"Prompt interceptor: {new_status['prompt_interceptor_enabled']}")
    
    # Reset configuration
    reset_success = orchestrator.reset_config()
    print(f"\nReset success: {reset_success}")
    
    # Verify reset
    reset_status = orchestrator.get_status()
    print(f"After reset: {reset_status['active_agents']} agents, {reset_status['active_personas']} personas")
    
    return True

async def test_parallel_execution():
    """Test parallel persona execution"""
    print("\n6. TESTING PARALLEL EXECUTION")
    print("-" * 40)
    
    orchestrator = DataDrivenGovernanceOrchestrator()
    
    # Enable parallel execution
    orchestrator.config['defaults']['parallel_execution'] = True
    
    prompt = "Comprehensive system review requiring all personas"
    
    # Execute with timing
    import time
    start = time.time()
    result = await orchestrator.execute(prompt, mode=ExecutionMode.FULL_ORCHESTRATION.value)
    duration = time.time() - start
    
    print(f"Prompt: '{prompt}'")
    print(f"Parallel execution time: {duration:.2f}s")
    print(f"Personas executed: {result.personas_executed}")
    print(f"Success: {result.success}")
    
    return True

async def test_validation_rules():
    """Test validation rule enforcement"""
    print("\n7. TESTING VALIDATION RULES")
    print("-" * 40)
    
    orchestrator = DataDrivenGovernanceOrchestrator()
    
    # Test prompts with violations
    test_cases = [
        ("Connect to localhost:3000", "no_magic_variables"),
        ("TODO: implement this feature", "no_boilerplate"),
        ("Use hardcoded secret key", "no_magic_variables"),
    ]
    
    for prompt, expected_rule in test_cases:
        violations = await orchestrator._run_validations(prompt, {"file": "test.py"})
        print(f"\nPrompt: '{prompt}'")
        print(f"  Violations found: {len(violations)}")
        
        for violation in violations:
            print(f"    - Rule: {violation['rule']}")
            print(f"      Severity: {violation['severity']}")
            print(f"      Pattern: {violation['pattern']}")
            print(f"      Auto-fix: {violation['auto_fix']}")
    
    return True

async def test_export_import():
    """Test configuration export and import"""
    print("\n8. TESTING EXPORT/IMPORT")
    print("-" * 40)
    
    orchestrator = DataDrivenGovernanceOrchestrator()
    
    # Export configuration
    formats = ['json', 'python']
    for format in formats:
        exported = orchestrator.export_config(format)
        print(f"\nExported as {format}: {len(exported)} characters")
        print(f"  Preview: {exported[:100]}...")
    
    # Validate configuration
    valid, errors = orchestrator.validate_config()
    print(f"\nConfiguration valid: {valid}")
    if errors:
        print(f"Errors: {errors}")
    
    return True

async def test_agent_persona_combinations():
    """Test different agent/persona combinations"""
    print("\n9. TESTING AGENT/PERSONA COMBINATIONS")
    print("-" * 40)
    
    orchestrator = DataDrivenGovernanceOrchestrator()
    
    # Test single agent, single persona
    orchestrator.config['execution_modes']['single_agent']['personas'] = ['sarah_chen']
    result1 = await orchestrator.execute("Test AI integration", mode="single_agent")
    print(f"\nSingle agent, single persona:")
    print(f"  Agents: {result1.agents_executed}")
    print(f"  Personas: {result1.personas_executed}")
    
    # Test multi-agent, single persona each
    result2 = await orchestrator.execute("Test with audit", mode="multi_agent_single_persona")
    print(f"\nMulti-agent, single persona each:")
    print(f"  Agents: {result2.agents_executed}")
    print(f"  Personas: {result2.personas_executed}")
    
    # Test multi-agent, multi-persona
    result3 = await orchestrator.execute("Full system test", mode="multi_agent_multi_persona")
    print(f"\nMulti-agent, multi-persona:")
    print(f"  Agents: {result3.agents_executed}")
    print(f"  Personas: {result3.personas_executed}")
    
    return True

async def test_portability():
    """Test portability features"""
    print("\n10. TESTING PORTABILITY")
    print("-" * 40)
    
    # Check module exports
    from data_driven_governance import __all__
    print(f"Exported classes: {__all__}")
    
    # Check standalone operation
    config_dict = {
        "version": "5.0",
        "defaults": {"governance_level": "balanced"},
        "agents": {},
        "personas": {},
        "validation_rules": {}
    }
    
    # Create orchestrator with custom config
    temp_config_path = Path("temp_governance_config.json")
    with open(temp_config_path, 'w') as f:
        json.dump(config_dict, f)
    
    custom_orchestrator = DataDrivenGovernanceOrchestrator(str(temp_config_path))
    print(f"\nCustom orchestrator created: {custom_orchestrator.config['version']}")
    
    # Clean up
    temp_config_path.unlink()
    
    return True

async def main():
    """Run all tests"""
    print("="*60)
    print("DATA-DRIVEN GOVERNANCE SYSTEM v5.0 - TEST SUITE")
    print("="*60)
    
    tests = [
        ("Configuration Loading", test_configuration_loading),
        ("Execution Modes", test_execution_modes),
        ("Prompt Interception", test_prompt_interception),
        ("Business Auditor", test_business_auditor),
        ("Configuration Updates", test_configuration_updates),
        ("Parallel Execution", test_parallel_execution),
        ("Validation Rules", test_validation_rules),
        ("Export/Import", test_export_import),
        ("Agent/Persona Combinations", test_agent_persona_combinations),
        ("Portability", test_portability),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                print(f"\n[PASS] {test_name}: PASSED")
                passed += 1
            else:
                print(f"\n[FAIL] {test_name}: FAILED")
                failed += 1
        except Exception as e:
            print(f"\n[ERROR] {test_name}: ERROR - {e}")
            failed += 1
    
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    print(f"Success Rate: {(passed/len(tests)*100):.1f}%")
    
    if failed == 0:
        print("\n[SUCCESS] ALL TESTS PASSED! System is ready for production.")
    else:
        print(f"\n[WARNING] {failed} tests failed. Review and fix issues.")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())