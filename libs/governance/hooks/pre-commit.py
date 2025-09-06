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
    import yaml
    import re
    import subprocess
    import json
    from datetime import datetime
    from typing import List, Dict, Tuple, Set

    # Import unified validator and exemption manager
    repo_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(repo_root))
    sys.path.insert(0, str(Path(__file__).parent.parent))
    try:
        from core.exemption_manager import ExemptionManager
    except ImportError:
        ExemptionManager = None
    try:
        from validators.unified_doc_validator import UnifiedDocumentValidator
        UNIFIED_VALIDATOR_AVAILABLE = True
    except ImportError:
        UNIFIED_VALIDATOR_AVAILABLE = False

    # Import documentation health validator
    try:
        from validators.documentation_validator import DocumentationValidator
        DOCUMENTATION_VALIDATOR_AVAILABLE = True
    except ImportError:
        DOCUMENTATION_VALIDATOR_AVAILABLE = False

    
    # Fallback implementation - simplified version of original ExtremeGovernance
    class ExtremeGovernance:
        """Fallback ExtremeGovernance class for when modular system is not available"""
        
        def __init__(self):
            self.repo_root = Path(subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True, text=True
            ).stdout.strip())
            self.config = self.load_config()
            self.violations = []
            self.compliance_score = 100.0
            self.changed_files = self.get_changed_files()
            
        def load_config(self) -> dict:
            """Load governance configuration"""
            # Check new location first, then fall back to old
            config_path = self.repo_root / "config" / "governance" / "rules.yaml"
            if not config_path.exists():
                config_path = self.repo_root / "libs" / "governance" / "config.yaml"
                if not config_path.exists():
                    config_path = self.repo_root / "governance" / "config.yaml"
                    if not config_path.exists():
                        self.fatal_error("GOVERNANCE CONFIG MISSING - Cannot proceed")
            
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        
        def get_changed_files(self) -> List[str]:
            """Get list of changed files"""
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True, text=True
            )
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        def add_violation(self, level: str, message: str, penalty: float):
            """Add violation and reduce compliance score"""
            self.violations.append({
                'level': level,
                'message': message,
                'penalty': penalty,
                'timestamp': datetime.now().isoformat()
            })
            self.compliance_score = max(0, self.compliance_score - penalty)
        
        def fatal_error(self, message: str):
            """Unrecoverable error"""
            print(f"\n{'='*70}")
            print(f"[FATAL ERROR] {message}")
            print(f"{'='*70}")
            print("Governance system cannot continue")
            sys.exit(1)
            
        def log_activity(self, action: str, success: bool):
            """Log activity"""
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'success': success,
                'files': self.changed_files,
                'violations': self.violations,
                'compliance_score': self.compliance_score
            }
            
            log_dir = self.repo_root / ".governance" / "audit"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = log_dir / f"extreme_governance_{datetime.now().strftime('%Y%m%d')}.jsonl"
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        
        def enforce(self):
            """Simplified enforcement for fallback"""
            print("\n" + "="*70)
            print("EXTREME GOVERNANCE ENFORCEMENT v2.0 (FALLBACK)")
            print("MODE: ZERO TOLERANCE - NO BYPASS ALLOWED")
            print("="*70)
            
            # Check for bypass attempt
            if os.environ.get('GOVERNANCE_BYPASS'):
                self.fatal_error("BYPASS IS NOT ALLOWED")
            
            # Get basic info
            user = subprocess.run(['git', 'config', 'user.name'], 
                                capture_output=True, text=True).stdout.strip()
            branch = subprocess.run(['git', 'branch', '--show-current'],
                                  capture_output=True, text=True).stdout.strip()
            
            print(f"\nUser: {user}")
            print(f"Branch: {branch}")
            print(f"Files changed: {len(self.changed_files)}")
            
            if not self.changed_files:
                print("\n[WARNING] No files staged for commit")
                sys.exit(1)
            
            # Basic checks
            print("\n[CHECK] Basic governance validation...")
            
            # Check for forbidden patterns
            for file_path in self.changed_files:
                if file_path.endswith(('.tmp', '.log', '.bak')):
                    self.add_violation("HIGH", f"Temporary file: {file_path}", 10)
            
            # Final verdict
            print(f"\nCompliance Score: {self.compliance_score:.1f}%")
            print(f"Required Minimum: {self.config.get('enforcement', {}).get('compliance_minimum', 95)}%")
            
            if self.compliance_score < self.config.get('enforcement', {}).get('compliance_minimum', 95):
                print("\n[BLOCKED] COMMIT REJECTED (Fallback mode)")
                self.log_activity("COMMIT_BLOCKED", False)
                sys.exit(1)
            else:
                print("\n[APPROVED] Commit authorized (Fallback mode)")
                self.log_activity("COMMIT_APPROVED", True)
                sys.exit(0)


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
            print("[INFO] Using fallback implementation")
            governance = ExtremeGovernance()  # From fallback implementation
            
        governance.enforce()
        
    except Exception as e:
        print(f"\n[ERROR] Governance system error: {e}")
        print("Fix the error - NO BYPASS AVAILABLE")
        
        # In case of system errors, show helpful debugging information
        if MODULAR_SYSTEM_AVAILABLE:
            print("\n[DEBUG] Modular system was available but failed")
            print("Try running individual validators for debugging:")
            print("  python -c \"from libs.governance.hooks.validators.readme_validator import ReadmeValidator\"")
        else:
            print("\n[DEBUG] Fell back to basic implementation but still failed")
            print("Check governance configuration and dependencies")
        
        sys.exit(1)