"""
Validator Orchestrator

Coordinates execution of all governance validators.
Handles configuration loading, validator instantiation, result aggregation,
and maintains backward compatibility with the ExtremeGovernance interface.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Type, Set

# Import local modules
try:
    from .base import ValidatorInterface, ValidationResult
    from .readme_validator import ReadmeValidator
    from .code_doc_validator import CodeDocValidator
    from .naming_validator import NamingValidator
    from .file_creation_validator import FileCreationValidator
    from .test_coverage_validator import TestCoverageValidator
    from .code_quality_validator import CodeQualityValidator
except ImportError:
    # Fallback for direct execution
    from base import ValidatorInterface, ValidationResult
    from readme_validator import ReadmeValidator
    from code_doc_validator import CodeDocValidator
    from naming_validator import NamingValidator
    from file_creation_validator import FileCreationValidator
    from test_coverage_validator import TestCoverageValidator
    from code_quality_validator import CodeQualityValidator


class ValidatorOrchestrator:
    """
    Orchestrates execution of all governance validators
    
    This class maintains the same interface as ExtremeGovernance to ensure
    100% backward compatibility while providing modular validator execution.
    """
    
    def __init__(self):
        """Initialize the validator orchestrator"""
        self.repo_root = Path(subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True
        ).stdout.strip())
        
        self.config = self.load_config()
        self.violations = []
        self.compliance_score = 100.0
        self.changed_files = self.get_changed_files()
        self.all_directories = self.get_all_directories()
        
        # Initialize exemption manager
        self.exemption_manager = self._initialize_exemption_manager()
        
        # Register validators
        self.validators = self._register_validators()
        
        # Execution metadata
        self.execution_metadata = {
            'start_time': None,
            'end_time': None,
            'validators_run': [],
            'total_files_checked': 0,
            'fail_fast_triggered': False
        }
    
    def _register_validators(self) -> Dict[str, Type[ValidatorInterface]]:
        """Register all available validators"""
        return {
            'readme': ReadmeValidator,
            'code_doc': CodeDocValidator,
            'naming': NamingValidator,
            'file_creation': FileCreationValidator,
            'test_coverage': TestCoverageValidator,
            'code_quality': CodeQualityValidator
        }
    
    def _initialize_exemption_manager(self):
        """Initialize exemption manager with fallback logic"""
        try:
            # Import exemption manager
            repo_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(repo_root))
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from core.exemption_manager import ExemptionManager
            
            # Check new location first, then fall back to old
            config_path = self.repo_root / "config" / "governance" / "rules.yaml"
            if not config_path.exists():
                config_path = self.repo_root / "libs" / "governance" / "config.yaml"
                if not config_path.exists():
                    config_path = self.repo_root / "governance" / "config.yaml"
            
            return ExemptionManager(config_path)
        except ImportError:
            return None
    
    def load_config(self) -> dict:
        """Load governance configuration with fallback logic"""
        import yaml
        
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
        """Get list of changed files with skip patterns applied"""
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True, text=True
        )
        
        # Get skip patterns from config
        skip_patterns = self.config.get('documentation', {}).get('skip_directories', [])
        # Add trailing slash for directory matching
        skip_patterns = [p if p.endswith('/') else p + '/' for p in skip_patterns]
        
        files = []
        for f in result.stdout.strip().split('\n'):
            if f and not any(skip in f for skip in skip_patterns):
                files.append(f)
        return files
    
    def get_all_directories(self) -> Set[str]:
        """Get all directories in the project"""
        dirs = set()
        # Get skip paths from config
        skip_paths = self.config.get('documentation', {}).get('skip_directories', [])
        
        for root, directories, _ in os.walk(self.repo_root):
            # Skip if current path contains any skip pattern
            if any(skip in root for skip in skip_paths):
                continue
                
            for d in directories:
                if d not in skip_paths:
                    rel_path = Path(root) / d
                    rel_str = str(rel_path.relative_to(self.repo_root))
                    # Double check the relative path doesn't contain skip patterns
                    if not any(skip in rel_str for skip in skip_paths):
                        dirs.add(rel_str)
        return dirs
    
    def run_validator(self, validator_name: str, validator_class: Type[ValidatorInterface]) -> ValidationResult:
        """Run a specific validator"""
        try:
            # Create validator instance
            if validator_name == 'readme':
                validator = validator_class(
                    self.repo_root, self.config, self.changed_files, 
                    self.exemption_manager, self.all_directories
                )
            else:
                validator = validator_class(
                    self.repo_root, self.config, self.changed_files, 
                    self.exemption_manager
                )
            
            # Run validation
            result = validator.validate()
            
            # Update orchestrator state
            self.violations.extend(result.violations)
            self.compliance_score = max(0, self.compliance_score - sum(
                v.get('penalty', 0) for v in result.violations
            ))
            self.execution_metadata['validators_run'].append(validator_name)
            self.execution_metadata['total_files_checked'] += len(result.files_checked)
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Validator '{validator_name}' failed: {e}")
            # Create error result
            error_result = ValidationResult(
                validator_name=validator_name,
                success=False,
                score=0.0,
                violations=[{
                    'level': 'CRITICAL',
                    'message': f"Validator error: {str(e)}",
                    'penalty': 10,
                    'timestamp': datetime.now().isoformat()
                }],
                warnings=[f"Validator failed with error: {e}"],
                suggestions=[],
                execution_time=0.0,
                files_checked=[],
                metadata={'error': str(e)}
            )
            
            self.violations.extend(error_result.violations)
            self.compliance_score = max(0, self.compliance_score - 10)
            
            return error_result
    
    def run_all_validators(self, fail_fast: bool = False) -> Dict[str, ValidationResult]:
        """
        Run all validators and return results
        
        Args:
            fail_fast: Stop execution on first failure
            
        Returns:
            Dict mapping validator names to their results
        """
        self.execution_metadata['start_time'] = datetime.now()
        
        # Get validator configuration
        validator_config = self.config.get('validators', {})
        enabled_validators = validator_config.get('enabled', list(self.validators.keys()))
        
        results = {}
        
        for validator_name, validator_class in self.validators.items():
            if validator_name not in enabled_validators:
                continue
            
            print(f"\n[VALIDATOR] Running {validator_name}...")
            
            result = self.run_validator(validator_name, validator_class)
            results[validator_name] = result
            
            # Check fail-fast condition
            if fail_fast and not result.success:
                print(f"[FAIL-FAST] Stopping execution due to {validator_name} failure")
                self.execution_metadata['fail_fast_triggered'] = True
                break
        
        self.execution_metadata['end_time'] = datetime.now()
        return results
    
    def check_bypass_attempt(self):
        """Check if bypass was attempted"""
        if os.environ.get('GOVERNANCE_BYPASS'):
            self.add_violation(
                level="FATAL",
                message="BYPASS ATTEMPT DETECTED - This is not allowed in EXTREME mode",
                penalty=100
            )
            return False
        return True
    
    def check_temp_directory(self):
        """Check if temp directory is clean - for backward compatibility"""
        print("\n[CHECK] Temp Directory Status...")
        
        temp_dir = self.repo_root / 'temp'
        if not temp_dir.exists():
            return  # No temp directory, that's fine
        
        # Get all files in temp, excluding README.md and .gitignore
        temp_files = []
        for file in temp_dir.iterdir():
            if file.name not in ['README.md', '.gitignore']:
                temp_files.append(file)
        
        if temp_files:
            self.add_violation(
                "CRITICAL",
                f"Temp directory contains {len(temp_files)} file(s) - must be cleaned before commit",
                10.0  # High penalty
            )
            print(f"  [CRITICAL] Found {len(temp_files)} files in temp directory:")
            for f in temp_files[:5]:  # Show first 5
                print(f"    - {f.name}")
            if len(temp_files) > 5:
                print(f"    ... and {len(temp_files) - 5} more")
            print("  [ACTION] Clean temp directory before committing")
        else:
            print("  [OK] Temp directory is clean")
    
    def check_documentation_health(self):
        """Check overall documentation health - for backward compatibility"""
        print("\n[CHECK] Documentation Health...")
        print("-" * 40)
        
        # This is now handled by specialized validators, but we maintain the interface
        try:
            # Try to import documentation validator
            try:
                from validators.documentation_validator import DocumentationValidator
                validator = DocumentationValidator(self.repo_root)
                results = validator.validate_all()
                
                overall_score = results['overall_score']
                min_score = self.config.get('documentation_health', {}).get('minimum_score', 85)
                
                print(f"  Overall Score: {overall_score:.1f}%")
                print(f"  Required Score: {min_score}%")
                
                if overall_score < min_score:
                    self.add_violation(
                        level="HIGH",
                        message=f"Documentation health below {min_score}% (current: {overall_score:.1f}%)",
                        penalty=self.config['penalties']['high']
                    )
                else:
                    print(f"  [PASS] Documentation health acceptable")
                    
            except ImportError:
                print("  [SKIP] Documentation health validator not available")
                
        except Exception as e:
            print(f"  [WARN] Could not check documentation health: {e}")
    
    def add_violation(self, level: str, message: str, penalty: float):
        """Add violation and reduce compliance score - for backward compatibility"""
        violation = {
            'level': level,
            'message': message,
            'penalty': penalty,
            'timestamp': datetime.now().isoformat()
        }
        self.violations.append(violation)
        self.compliance_score = max(0, self.compliance_score - penalty)
    
    def fatal_error(self, message: str):
        """Unrecoverable error - for backward compatibility"""
        print(f"\n{'='*70}")
        print(f"[FATAL ERROR] {message}")
        print(f"{'='*70}")
        print("Governance system cannot continue")
        sys.exit(1)
    
    def log_activity(self, action: str, success: bool):
        """Log all governance activity - for backward compatibility"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user': subprocess.run(['git', 'config', 'user.name'], 
                                 capture_output=True, text=True).stdout.strip(),
            'action': action,
            'success': success,
            'files': self.changed_files,
            'violations': self.violations,
            'compliance_score': self.compliance_score,
            'execution_metadata': self.execution_metadata
        }
        
        log_dir = self.repo_root / ".governance" / "audit"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"extreme_governance_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def enforce(self):
        """
        Run all checks with zero tolerance - main entry point for backward compatibility
        
        This method maintains the exact same interface as the original ExtremeGovernance.enforce()
        """
        print("\n" + "="*70)
        print("EXTREME GOVERNANCE ENFORCEMENT v2.0 (MODULAR)")
        print("MODE: ZERO TOLERANCE - NO BYPASS ALLOWED")
        print("="*70)
        
        # Check for bypass attempt first
        if not self.check_bypass_attempt():
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
        
        # Run all modular validators
        fail_fast = self.config.get('enforcement', {}).get('fail_fast', False)
        results = self.run_all_validators(fail_fast=fail_fast)
        
        # Run additional checks for backward compatibility
        self.check_temp_directory()
        self.check_documentation_health()
        
        # Final verdict
        print("\n" + "="*70)
        print("GOVERNANCE VERDICT")
        print("="*70)
        
        if self.violations:
            print(f"\n[VIOLATIONS FOUND: {len(self.violations)}]")
            for v in self.violations[:10]:  # Show first 10
                print(f"  [{v['level']}] {v['message']}")
            if len(self.violations) > 10:
                print(f"  ... and {len(self.violations) - 10} more violations")
        
        print(f"\nCompliance Score: {self.compliance_score:.1f}%")
        print(f"Required Minimum: {self.config['enforcement']['compliance_minimum']}%")
        
        # Print execution summary
        print(f"\nExecution Summary:")
        print(f"  Validators run: {', '.join(self.execution_metadata['validators_run'])}")
        print(f"  Total files checked: {self.execution_metadata['total_files_checked']}")
        if self.execution_metadata['start_time'] and self.execution_metadata['end_time']:
            duration = (self.execution_metadata['end_time'] - self.execution_metadata['start_time']).total_seconds()
            print(f"  Execution time: {duration:.2f}s")
        
        if self.compliance_score < self.config['enforcement']['compliance_minimum']:
            print("\n" + "="*70)
            print("[BLOCKED] COMMIT REJECTED")
            print("FIX ALL VIOLATIONS - NO BYPASS AVAILABLE")
            print("="*70)
            self.log_activity("COMMIT_BLOCKED", False)
            sys.exit(1)
        else:
            print("\n" + "="*70)
            print("[APPROVED] Commit authorized")
            print(f"Compliance: {self.compliance_score:.1f}%")
            print("="*70)
            self.log_activity("COMMIT_APPROVED", True)
            sys.exit(0)


# Maintain backward compatibility by providing the ExtremeGovernance class name
ExtremeGovernance = ValidatorOrchestrator
