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
    
    def check_test_execution(self):
        """Run tests and ensure they pass with coverage"""
        print("\n[CHECK] Test Execution & Coverage")
        print("-" * 40)
        
        if not self.config.get('testing', {}).get('execution_required', False):
            print("[SKIP] Test execution not required")
            return
        
        # Check for Python tests with coverage
        if any(f.endswith('.py') for f in self.changed_files if self.is_source_file(f)):
            print("Running Python tests with coverage...")
            
            # Run tests with coverage
            result = subprocess.run(
                ['python', '-m', 'pytest', '--cov=.', '--cov-report=term-missing', '--cov-fail-under=' + 
                 str(self.config.get('testing', {}).get('minimum_coverage', {}).get('python', 85))],
                capture_output=True, text=True, cwd=self.repo_root
            )
            
            if result.returncode != 0:
                # Check if it's test failure or coverage failure
                if 'FAILED' in result.stdout:
                    self.add_violation(
                        level="CRITICAL",
                        message="Python tests failed - fix before committing",
                        penalty=self.config['penalties']['critical']
                    )
                    print(f"[FAIL] Python tests failed")
                elif 'coverage' in result.stdout.lower():
                    self.add_violation(
                        level="HIGH",
                        message=f"Python coverage below {self.config.get('testing', {}).get('minimum_coverage', {}).get('python', 85)}%",
                        penalty=self.config['penalties']['high']
                    )
                    print(f"[FAIL] Insufficient test coverage")
                
                # Show relevant output
                print(result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout)
                return
            else:
                print(f"[PASS] Python tests passing with sufficient coverage")
        
        # Check for TypeScript/JavaScript tests with coverage
        if any(f.endswith(('.ts', '.tsx', '.js', '.jsx')) for f in self.changed_files if self.is_source_file(f)):
            if (self.repo_root / 'package.json').exists():
                print("Running JavaScript/TypeScript tests with coverage...")
                
                # Run tests with coverage
                result = subprocess.run(
                    ['npm', 'test', '--', '--coverage', '--passWithNoTests'],
                    capture_output=True, text=True, cwd=self.repo_root
                )
                
                if result.returncode != 0:
                    self.add_violation(
                        level="CRITICAL",
                        message="JavaScript/TypeScript tests failed",
                        penalty=self.config['penalties']['critical']
                    )
                    print(f"[FAIL] JavaScript/TypeScript tests failed")
                    return
                else:
                    print(f"[PASS] JavaScript/TypeScript tests passing")
        
        print("[PASS] All tests passing with coverage")
    
    def check_file_creation(self):
        """Check that only allowed files are being created"""
        print("\n[CHECK] File Creation Rules")
        print("-" * 40)
        
        forbidden_files = []
        suspicious_files = []
        
        file_config = self.config.get('file_creation', {})
        allowed = file_config.get('allowed_patterns', [])
        forbidden = file_config.get('forbidden_patterns', [])
        
        for file_path in self.changed_files:
            filename = Path(file_path).name
            
            # Check forbidden patterns
            for pattern in forbidden:
                if self.matches_pattern(filename, pattern):
                    forbidden_files.append(file_path)
                    self.add_violation(
                        level="CRITICAL",
                        message=f"Forbidden file pattern: '{file_path}'",
                        penalty=self.config['penalties']['critical']
                    )
                    break
            
            # Check if file matches allowed patterns
            if not any(self.matches_pattern(filename, p) for p in allowed):
                suspicious_files.append(file_path)
                self.add_violation(
                    level="HIGH",
                    message=f"Suspicious file type: '{file_path}'",
                    penalty=self.config['penalties']['high']
                )
        
        if forbidden_files or suspicious_files:
            print(f"[FAIL] {len(forbidden_files)} forbidden, {len(suspicious_files)} suspicious files")
        else:
            print("[PASS] All files follow creation rules")
    
    def check_code_quality(self):
        """Check for debug code, TODOs, and other quality issues"""
        print("\n[CHECK] Code Quality")
        print("-" * 40)
        
        quality_issues = []
        
        patterns = self.config.get('security', {}).get('code_quality_patterns', [])
        
        for file_path in self.changed_files:
            if self.is_source_file(file_path):
                full_path = self.repo_root / file_path
                if full_path.exists():
                    content = full_path.read_text(errors='ignore')
                    
                    for pattern_config in patterns:
                        pattern = pattern_config['pattern']
                        if re.search(pattern, content):
                            quality_issues.append({
                                'file': file_path,
                                'issue': pattern_config['message'],
                                'severity': pattern_config.get('severity', 'medium')
                            })
                            
                            penalty = {
                                'critical': self.config['penalties']['critical'],
                                'high': self.config['penalties']['high'],
                                'medium': self.config['penalties']['medium'],
                                'low': self.config['penalties']['low']
                            }.get(pattern_config.get('severity', 'medium'), 5)
                            
                            self.add_violation(
                                level=pattern_config.get('severity', 'MEDIUM').upper(),
                                message=f"{file_path}: {pattern_config['message']}",
                                penalty=penalty
                            )
        
        if quality_issues:
            print(f"[FAIL] {len(quality_issues)} code quality issues found")
            for issue in quality_issues[:5]:  # Show first 5
                print(f"  - {issue['file']}: {issue['issue']}")
        else:
            print("[PASS] Code quality standards met")
    
    def check_documentation_sync(self):
        """Ensure documentation is updated when code changes"""
        print("\n[CHECK] Documentation Sync")
        print("-" * 40)
        
        # Check if significant code changes require doc updates
        code_files = [f for f in self.changed_files if self.is_source_file(f)]
        doc_files = [f for f in self.changed_files if f.endswith('.md')]
        
        if len(code_files) > 3 and not doc_files:
            self.add_violation(
                level="MEDIUM",
                message="Significant code changes without documentation updates",
                penalty=self.config['penalties']['medium']
            )
            print(f"[WARN] {len(code_files)} code files changed without documentation")
        else:
            print("[PASS] Documentation appears in sync")
    
    def matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches a pattern (supports wildcards)"""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
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
        self.check_file_creation()
        self.check_test_coverage()
        self.check_code_quality()
        self.check_documentation_sync()
        
        # Run tests last (they take the longest)
        if self.config.get('testing', {}).get('execution_required', False):
            self.check_test_execution()
        
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