#!/usr/bin/env python3
"""
@fileoverview Quick test utility for validating governance system and milestone completion
@author Dr. Sarah Chen v1.0 - 2025-08-29
@architecture Backend - Governance testing and validation script
@responsibility Validate governance system functionality and milestone completion status
@dependencies sys, pathlib, governance.core modules
@integration_points Governance engine, context system, milestone validation
@testing_strategy Self-validation through governance engine, file existence checks
@governance Uses governance to validate its own development progress

Business Logic Summary:
- Check milestone completion status
- Validate governance engine functionality
- Test rule addition and evaluation
- Verify core module existence
- Gate milestone progression

Architecture Integration:
- Uses governance engine for self-validation
- Checks core module availability
- Tests engine instantiation
- Validates milestone prerequisites
- Provides go/no-go decision

Sarah's Framework Check:
- What breaks first: Import failures if core modules missing
- How we know: Try/except blocks catch instantiation errors
- Plan B: File existence checks provide fallback validation
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from governance.core.engine import GovernanceEngine
from governance.core.context import GovernanceContext


def check_before_implementing_next_milestone():
    """
    Use governance to check if we should proceed with next milestone
    """
    engine = GovernanceEngine()
    
    print("=" * 50)
    print("GOVERNANCE CHECK: Can we implement Milestone 2?")
    print("=" * 50)
    
    # Add a rule for our own development
    engine.add_rule("requires_review", "implement_hook_system")
    
    context = GovernanceContext(
        operation_type="implement_hook_system",
        actor="developer",
        payload={
            "milestone": 2,
            "description": "Add hook system for extensibility",
            "prerequisites": ["milestone_1_complete"],
            "estimated_time": "2 hours"
        }
    )
    
    result = engine.evaluate(context)
    
    print(f"\nDecision: {result.decision}")
    print(f"Confidence: {result.confidence:.0%}")
    
    if result.reason:
        print(f"Reason: {result.reason}")
    
    if result.evidence:
        print(f"Evidence: {', '.join(result.evidence)}")
    
    if result.recommendations:
        print(f"Recommendations: {', '.join(result.recommendations)}")
    
    # Now check if we completed Milestone 1
    print("\n" + "=" * 50)
    print("VALIDATION: Is Milestone 1 Complete?")
    print("=" * 50)
    
    checks = []
    
    # Check if core modules exist
    core_files = [
        "governance/core/context.py",
        "governance/core/result.py",
        "governance/core/engine.py",
        "governance/core/exceptions.py"
    ]
    
    for file in core_files:
        if Path(file).exists():
            checks.append(f"[OK] {file} exists")
        else:
            checks.append(f"[MISSING] {file} not found")
    
    # Check if we can import and use
    try:
        from governance.core.engine import GovernanceEngine as GovEngine
        engine_test = GovEngine()
        checks.append("[OK] Engine can be instantiated")
    except Exception as e:
        checks.append(f"[ERROR] Engine failed: {e}")
    
    # Print checks
    for check in checks:
        print(check)
    
    # Final decision
    if all("[OK]" in check for check in checks):
        print("\n[APPROVED] Milestone 1 is complete - proceed with Milestone 2!")
    else:
        print("\n[BLOCKED] Milestone 1 incomplete - fix issues first")


if __name__ == "__main__":
    check_before_implementing_next_milestone()