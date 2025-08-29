#!/usr/bin/env python3
"""
@fileoverview Test script for Milestone 1 basic governance core validation
@author Dr. Sarah Chen v1.0 - 2025-08-29
@architecture Backend - Milestone 1 validation tests
@responsibility Validate basic governance implementation functionality
@dependencies pathlib, governance.core modules
@integration_points Governance engine, context, result structures
@testing_strategy End-to-end validation of governance pipeline
@governance Tests governance system milestone 1 requirements

Business Logic Summary:
- Test basic governance evaluation
- Validate dangerous code detection
- Test result structure
- Verify engine initialization
- Validate context flow

Architecture Integration:
- Tests core governance components
- Validates milestone 1 requirements
- Ensures basic functionality works
- Tests integration between modules

Sarah's Framework Check:
- What breaks first: Engine initialization or rule loading
- How we know: Test output and assertions
- Plan B: Detailed error reporting for debugging
"""

import sys
from pathlib import Path

# Add governance module to path
sys.path.insert(0, str(Path(__file__).parent))

from governance.core.engine import GovernanceEngine
from governance.core.context import GovernanceContext
from governance.core.result import GovernanceResult


def test_basic_evaluation():
    """Test basic governance evaluation"""
    print("=" * 50)
    print("Testing Milestone 1: Basic Governance Core")
    print("=" * 50)
    
    engine = GovernanceEngine()
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Simple approval
    print("\n1. Testing simple approval...")
    context = GovernanceContext(
        operation_type="safe_operation",
        actor="test_user",
        payload={"description": "This is a safe operation"}
    )
    result = engine.evaluate(context)
    
    if result.is_approved():
        print(f"   [PASS] Basic approval works: {result}")
        tests_passed += 1
    else:
        print(f"   [FAIL] Basic approval failed: {result}")
        tests_failed += 1
    
    # Test 2: Dangerous operation rejection
    print("\n2. Testing dangerous operation rejection...")
    context = GovernanceContext(
        operation_type="drop_database",
        actor="test_user",
        payload={"database": "production"}
    )
    result = engine.evaluate(context)
    
    if result.is_rejected():
        print(f"   [PASS] Dangerous operation rejected: {result}")
        print(f"   Reason: {result.reason}")
        tests_passed += 1
    else:
        print(f"   [FAIL] Dangerous operation not rejected: {result}")
        tests_failed += 1
    
    # Test 3: Review required
    print("\n3. Testing review requirement...")
    context = GovernanceContext(
        operation_type="architecture_change",
        actor="developer",
        payload={"component": "core_system"}
    )
    result = engine.evaluate(context)
    
    if result.decision == "review":
        print(f"   [PASS] Review requirement detected: {result}")
        print(f"   Recommendations: {result.recommendations}")
        tests_passed += 1
    else:
        print(f"   [FAIL] Review requirement not detected: {result}")
        tests_failed += 1
    
    # Test 4: Auto-approve
    print("\n4. Testing auto-approval...")
    context = GovernanceContext(
        operation_type="documentation",
        actor="developer",
        payload={"file": "README.md"}
    )
    result = engine.evaluate(context)
    
    if result.is_approved() and result.confidence == 1.0:
        print(f"   [PASS] Auto-approval works: {result}")
        tests_passed += 1
    else:
        print(f"   [FAIL] Auto-approval failed: {result}")
        tests_failed += 1
    
    # Test 5: Test operation detection
    print("\n5. Testing test operation detection...")
    context = GovernanceContext(
        operation_type="test_deployment",
        actor="ci_system",
        payload={"environment": "staging"}
    )
    result = engine.evaluate(context)
    
    if result.is_approved():
        print(f"   [PASS] Test operation approved: {result}")
        tests_passed += 1
    else:
        print(f"   [FAIL] Test operation not approved: {result}")
        tests_failed += 1
    
    # Test 6: Evaluation metrics
    print("\n6. Testing metrics...")
    metrics = engine.get_metrics()
    
    if metrics['evaluation_count'] == 5:
        print(f"   [PASS] Evaluation count correct: {metrics['evaluation_count']}")
        tests_passed += 1
    else:
        print(f"   [FAIL] Evaluation count wrong: {metrics['evaluation_count']}")
        tests_failed += 1
    
    print(f"\n   Metrics: {metrics}")
    
    # Test 7: Dynamic rule addition
    print("\n7. Testing dynamic rule addition...")
    engine.add_rule("dangerous_operations", "custom_danger")
    
    context = GovernanceContext(
        operation_type="custom_danger",
        actor="test_user"
    )
    result = engine.evaluate(context)
    
    if result.is_rejected():
        print(f"   [PASS] Dynamic rule addition works: {result}")
        tests_passed += 1
    else:
        print(f"   [FAIL] Dynamic rule addition failed: {result}")
        tests_failed += 1
    
    # Test 8: Rule removal
    print("\n8. Testing rule removal...")
    engine.remove_rule("dangerous_operations", "custom_danger")
    
    context = GovernanceContext(
        operation_type="custom_danger",
        actor="test_user"
    )
    result = engine.evaluate(context)
    
    if result.is_approved():
        print(f"   [PASS] Rule removal works: {result}")
        tests_passed += 1
    else:
        print(f"   [FAIL] Rule removal failed: {result}")
        tests_failed += 1
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"[PASS] Tests Passed: {tests_passed}")
    print(f"[FAIL] Tests Failed: {tests_failed}")
    print(f"[STATS] Success Rate: {(tests_passed/(tests_passed+tests_failed))*100:.1f}%")
    
    if tests_failed == 0:
        print("\n[SUCCESS] MILESTONE 1 COMPLETE: Basic governance core is working!")
        return 0
    else:
        print("\n[WARNING] Some tests failed. Please review and fix.")
        return 1


def test_context_serialization():
    """Test context serialization"""
    print("\n" + "=" * 50)
    print("Testing Context Serialization")
    print("=" * 50)
    
    context = GovernanceContext(
        operation_type="test",
        actor="user",
        payload={"key": "value"}
    )
    
    # Test to_dict
    context_dict = context.to_dict()
    print(f"Context dict keys: {list(context_dict.keys())}")
    
    # Test from_dict
    context2 = GovernanceContext.from_dict(context_dict)
    
    if context.operation_type == context2.operation_type:
        print("[PASS] Context serialization works")
    else:
        print("[FAIL] Context serialization failed")


def demonstrate_usage():
    """Demonstrate how to use the governance system"""
    print("\n" + "=" * 50)
    print("Demonstration: How to Use Governance")
    print("=" * 50)
    
    # Create engine
    engine = GovernanceEngine()
    
    # Example: Check before making a code change
    print("\n[EXAMPLE] Checking a code change...")
    context = GovernanceContext(
        operation_type="code_change",
        actor="developer_jane",
        payload={
            "files": ["main.py", "config.py"],
            "description": "Update configuration handling",
            "has_tests": True
        }
    )
    
    result = engine.evaluate(context)
    
    print(f"Decision: {result.decision}")
    print(f"Confidence: {result.confidence:.0%}")
    if result.evidence:
        print(f"Evidence: {result.evidence}")
    if result.recommendations:
        print(f"Recommendations: {result.recommendations}")
    
    # Example: Use for git commit validation
    print("\n[EXAMPLE] Git commit validation...")
    context = GovernanceContext(
        operation_type="git_commit",
        actor="john_doe",
        payload={
            "message": "Fix: Resolve memory leak in service",
            "changed_files": ["service.py", "test_service.py"],
            "branch": "feature/memory-fix"
        }
    )
    
    result = engine.evaluate(context)
    
    if result.is_approved():
        print("[PASS] Commit approved - proceeding with git commit")
    else:
        print(f"[FAIL] Commit blocked: {result.reason}")


if __name__ == "__main__":
    # Run tests
    exit_code = test_basic_evaluation()
    
    # Test serialization
    test_context_serialization()
    
    # Show usage examples
    demonstrate_usage()
    
    print("\n" + "=" * 50)
    print("Next Step: Implement Milestone 2 - Hook System")
    print("This will add extensibility to our governance")
    print("=" * 50)
    
    sys.exit(exit_code)