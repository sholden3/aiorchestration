#!/usr/bin/env python
"""
EXTREME GOVERNANCE PRE-COMMIT HOOK v2.0 (REFACTORED)
Zero-tolerance enforcement system with modular validators

This is the refactored version using the new modular validator system.
It maintains 100% backward compatibility while providing better maintainability,
testability, and separation of concerns.

@description: Enforces extreme governance with no bypass allowed using modular validators
@author: Governance System v2.0 (Refactored)
@version: 2.0.0-modular
@dependencies: yaml, pathlib, subprocess, json, validators package
@exports: ExtremeGovernance class (via ValidatorOrchestrator)
@testing: Improved with modular validator tests
@last_review: 2025-09-06
"""

import os
import sys
from pathlib import Path

# Add validators package to path
validators_path = Path(__file__).parent / "validators"
sys.path.insert(0, str(validators_path))

try:
    # Import the modular validator orchestrator
    from orchestrator import ValidatorOrchestrator, ExtremeGovernance
    
    # The ValidatorOrchestrator is aliased as ExtremeGovernance for backward compatibility
    MODULAR_SYSTEM_AVAILABLE = True
    
except ImportError as e:
    print(f"[WARN] Could not import modular validator system: {e}")
    print("[FALLBACK] Using original monolithic implementation...")
    MODULAR_SYSTEM_AVAILABLE = False
    
    # Fallback to original implementation if modular system is not available
    # This ensures we never break existing functionality
    exec(open(Path(__file__).parent / "pre-commit-original.py").read())


if __name__ == "__main__":
    # NO BYPASS CHECK - enforce immediately
    if os.environ.get('GOVERNANCE_BYPASS'):
        print("\n" + "="*70)
        print("BYPASS DETECTED AND BLOCKED")
        print("EXTREME GOVERNANCE DOES NOT ALLOW BYPASS")
        print("="*70)
        sys.exit(1)
    
    try:
        if MODULAR_SYSTEM_AVAILABLE:
            print("[INFO] Using modular validator system")
            governance = ValidatorOrchestrator()  # This is aliased as ExtremeGovernance
        else:
            print("[INFO] Using original monolithic system")
            governance = ExtremeGovernance()  # From fallback implementation
            
        governance.enforce()
        
    except Exception as e:
        print(f"\n[ERROR] Governance system error: {e}")
        print("Fix the error - NO BYPASS AVAILABLE")
        
        # In case of system errors, show helpful debugging information
        if MODULAR_SYSTEM_AVAILABLE:
            print("\n[DEBUG] Modular system was available but failed")
            print("Try running individual validators for debugging:")
            print("  python -m libs.governance.hooks.validators.readme_validator")
            print("  python -m libs.governance.hooks.validators.code_doc_validator")
            print("  etc.")
        else:
            print("\n[DEBUG] Fell back to original system but still failed")
            print("Check governance configuration and dependencies")
        
        sys.exit(1)
