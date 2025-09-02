#!/usr/bin/env python
"""
EXTREME GOVERNANCE PRE-COMMIT HOOK v2.0
Zero-tolerance enforcement system

@description: Enforces extreme governance with no bypass allowed
@author: Governance System v2.0
@version: 2.0.0
@dependencies: yaml, pathlib, subprocess, json
@exports: ExtremeGovernance class
@testing: 0% (needs implementation)
@last_review: 2025-09-02
"""

import yaml
import sys
import os
import re
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Set

class ExtremeGovernance:
    """Zero-tolerance governance enforcement"""
    
    def __init__(self):
        self.repo_root = Path(subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True
        ).stdout.strip())
        self.config = self.load_config()
        self.violations = []
        self.compliance_score = 100.0
        self.changed_files = self.get_changed_files()
        self.all_directories = self.get_all_directories()
        
    def load_config(self) -> dict:
        """Load governance configuration"""
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
        skip_patterns = ['node_modules/', '.git/', '__pycache__/', '.archive/', 'htmlcov/', 'dist/', 'build/', 'coverage/']
        files = []
        for f in result.stdout.strip().split('\n'):
            if f and not any(skip in f for skip in skip_patterns):
                files.append(f)
        return files
    
    def get_all_directories(self) -> Set[str]:
        """Get all directories in the project"""
        dirs = set()
        skip_paths = ['node_modules', '.git', '__pycache__', '.archive', 'htmlcov', 'dist', 'build', 'coverage']
        
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
    
    def check_readme_files(self):
        """Check README.md based on config rules"""
        print("\n[CHECK] README.md Files")
        print("-" * 40)
        
        max_depth = self.config['documentation']['directories'].get('readme_max_depth', 999)
        required_parents = self.config['documentation']['directories'].get('readme_required_parents', [])
        
        dirs_without_readme = []
        for dir_path in self.all_directories:
            # Check depth
            depth = len(Path(dir_path).parts)
            
            # Skip if deeper than max_depth and not in required_parents
            if depth > max_depth and dir_path not in required_parents:
                continue
            
            # Check if this directory or its parent is in required list
            should_check = False
            if depth <= max_depth:
                should_check = True
            else:
                for parent in required_parents:
                    if dir_path.startswith(parent + '/') or dir_path == parent:
                        should_check = True
                        break
            
            if should_check:
                readme_path = self.repo_root / dir_path / "README.md"
                if not readme_path.exists():
                    dirs_without_readme.append(dir_path)
                    self.add_violation(
                        level="CRITICAL",
                        message=f"Directory '{dir_path}' missing README.md",
                        penalty=self.config['penalties']['high']
                    )
                else:
                    # Check README quality
                    try:
                        content = readme_path.read_text(encoding='utf-8', errors='ignore')
                    except:
                        content = readme_path.read_text(errors='ignore')
                    required = self.config['documentation']['directories']['readme_min_sections']
                    missing = [s for s in required if s not in content]
                    if missing:
                        self.add_violation(
                            level="HIGH",
                            message=f"README in '{dir_path}' missing sections: {', '.join(missing)}",
                            penalty=self.config['penalties']['medium']
                        )
        
        if dirs_without_readme:
            print(f"[FAIL] {len(dirs_without_readme)} directories missing README.md")
        else:
            print("[PASS] All directories have README.md")
    
    def check_source_documentation(self):
        """Every source file MUST have complete documentation"""
        print("\n[CHECK] Source Code Documentation")
        print("-" * 40)
        
        poorly_documented = []
        for file_path in self.changed_files:
            full_path = self.repo_root / file_path
            if self.is_source_file(file_path) and full_path.exists():
                content = full_path.read_text(errors='ignore')
                required_tags = self.config['documentation']['source_code']['required_tags']
                
                missing_tags = []
                for tag in required_tags:
                    if tag not in content:
                        missing_tags.append(tag)
                
                if missing_tags:
                    poorly_documented.append(file_path)
                    self.add_violation(
                        level="CRITICAL",
                        message=f"File '{file_path}' missing tags: {', '.join(missing_tags)}",
                        penalty=self.config['penalties']['medium'] * len(missing_tags)
                    )
        
        if poorly_documented:
            print(f"[FAIL] {len(poorly_documented)} files poorly documented")
        else:
            print("[PASS] All source files properly documented")
    
    def check_naming_standards(self):
        """Enforce universal naming standards"""
        print("\n[CHECK] Naming Standards")
        print("-" * 40)
        
        standard_files = self.config['naming']['standard_files']
        violations_found = False
        
        # Check for non-standard tracker files
        for file_path in self.changed_files:
            filename = Path(file_path).name.lower()
            
            # Check various naming patterns
            if 'tracker' in filename and filename != 'tracker.md':
                violations_found = True
                self.add_violation(
                    level="CRITICAL",
                    message=f"Non-standard tracker: '{file_path}' should be 'TRACKER.md'",
                    penalty=self.config['penalties']['high']
                )
            
            if 'status' in filename and 'status.md' not in filename.lower():
                violations_found = True
                self.add_violation(
                    level="HIGH",
                    message=f"Non-standard status file: '{file_path}' should be 'STATUS.md'",
                    penalty=self.config['penalties']['high']
                )
        
        if not violations_found:
            print("[PASS] All files follow naming standards")
        else:
            print("[FAIL] Naming standard violations found")
    
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
    
    def check_test_coverage(self):
        """Check if code has tests"""
        print("\n[CHECK] Test Coverage")
        print("-" * 40)
        
        files_without_tests = []
        for file_path in self.changed_files:
            if self.is_source_file(file_path) and not self.is_test_file(file_path):
                # Look for corresponding test file
                test_exists = self.find_test_file(file_path)
                if not test_exists:
                    files_without_tests.append(file_path)
                    self.add_violation(
                        level="HIGH",
                        message=f"No test file for '{file_path}'",
                        penalty=self.config['penalties']['high']
                    )
        
        if files_without_tests:
            print(f"[FAIL] {len(files_without_tests)} files without tests")
        else:
            print("[PASS] All code files have tests")
    
    def is_source_file(self, file_path: str) -> bool:
        """Check if file is source code"""
        extensions = ['.py', '.ts', '.js', '.tsx', '.jsx']
        return any(file_path.endswith(ext) for ext in extensions)
    
    def is_test_file(self, file_path: str) -> bool:
        """Check if file is a test file"""
        return 'test' in file_path.lower() or 'spec' in file_path.lower()
    
    def find_test_file(self, file_path: str) -> bool:
        """Find if test file exists for given source file - fully config-driven"""
        import subprocess
        
        # Get all tracked AND staged files
        # ls-files shows committed files
        result1 = subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
        tracked_files = result1.stdout.strip().split('\n') if result1.returncode == 0 else []
        
        # diff --cached shows staged files
        result2 = subprocess.run(['git', 'diff', '--cached', '--name-only'], capture_output=True, text=True)
        staged_files = result2.stdout.strip().split('\n') if result2.returncode == 0 else []
        
        # Combine both lists
        all_files = list(set(tracked_files + staged_files))
        
        # Get file extension and base name
        path_obj = Path(file_path)
        base_name = path_obj.stem
        extension = path_obj.suffix
        
        # Get test patterns from config based on file extension
        test_patterns_config = self.config.get('testing', {}).get('test_file_patterns', {})
        
        # Check if this file extension is in config
        if extension not in test_patterns_config:
            # File type not configured - log warning but don't require tests
            if self.config.get('testing', {}).get('warn_unconfigured_extensions', True):
                print(f"[WARN] File extension '{extension}' not configured in test_file_patterns")
            return True  # Don't block for unconfigured file types
        
        # Get patterns for this file extension
        pattern_templates = test_patterns_config[extension]
        
        # Generate test patterns from config templates
        test_patterns = []
        for template in pattern_templates:
            # Replace placeholders with actual values
            pattern = template.replace('{name}', base_name)
            pattern = pattern.replace('{name_underscore}', base_name.replace('-', '_'))
            pattern = pattern.replace('{name_hyphen}', base_name.replace('_', '-'))
            test_patterns.append(pattern.lower())
        
        # Look for test files in all tracked files
        for test_file in all_files:
            test_file_lower = test_file.lower()
            for pattern in test_patterns:
                if pattern in test_file_lower:
                    return True
        
        return False
    
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
        """Log all governance activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user': subprocess.run(['git', 'config', 'user.name'], 
                                 capture_output=True, text=True).stdout.strip(),
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
        """Run all checks with zero tolerance"""
        print("\n" + "="*70)
        print("EXTREME GOVERNANCE ENFORCEMENT v2.0")
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
        
        # Run all checks
        self.check_readme_files()
        self.check_source_documentation()
        self.check_naming_standards()
        self.check_test_coverage()
        
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

if __name__ == "__main__":
    # NO BYPASS CHECK - enforce immediately
    if os.environ.get('GOVERNANCE_BYPASS'):
        print("\n" + "="*70)
        print("BYPASS DETECTED AND BLOCKED")
        print("EXTREME GOVERNANCE DOES NOT ALLOW BYPASS")
        print("="*70)
        sys.exit(1)
    
    try:
        governance = ExtremeGovernance()
        governance.enforce()
    except Exception as e:
        print(f"\n[ERROR] Governance system error: {e}")
        print("Fix the error - NO BYPASS AVAILABLE")
        sys.exit(1)