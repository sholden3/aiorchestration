# Git Hooks for Governance: Complete Implementation Guide

A comprehensive guide to implementing Git hooks as a governance layer, covering all hook types, implementation patterns, pain points, and Python-based solutions for enterprise-grade code quality control.

## Quick Reference: Git Hook Types

| Hook | Trigger | Can Block? | Primary Use Case | Governance Level |
|------|---------|------------|------------------|------------------|
| **pre-commit** | Before commit creation | ✅ Yes | Code quality, security validation | **HIGH** |
| **prepare-commit-msg** | Before commit message editor | ❌ No | Message templates, automation | LOW |
| **commit-msg** | After commit message written | ✅ Yes | Message format validation | MEDIUM |
| **post-commit** | After commit created | ❌ No | Notifications, logging | LOW |
| **pre-push** | Before push to remote | ✅ Yes | Integration tests, security scans | **HIGH** |
| **post-receive** | After push received (server) | ❌ No | Deployment, notifications | MEDIUM |
| **pre-receive** | Before push accepted (server) | ✅ Yes | Authorization, policy enforcement | **CRITICAL** |
| **post-update** | After refs updated (server) | ❌ No | CI/CD triggers, notifications | LOW |

---

## Hook 1: pre-commit - The Quality Gatekeeper

**Trigger**: Before commit object is created  
**Can Block**: ✅ Yes (non-zero exit code)  
**Primary Purpose**: Code quality validation, security scanning, formatting

### Implementation Strategy

```python
#!/usr/bin/env python3
"""
Enterprise Pre-Commit Hook
Comprehensive code quality and security validation
"""
import os
import sys
import json
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib

@dataclass
class ValidationResult:
    passed: bool
    message: str
    suggestion: str = ""
    severity: str = "error"  # error, warning, info
    rule_id: str = ""
    file_path: str = ""

class PreCommitGovernanceHook:
    def __init__(self, config_path: str = ".governance/pre-commit.json"):
        self.config = self.load_config(config_path)
        self.results: List[ValidationResult] = []
        self.staged_files = self.get_staged_files()
        
        # Initialize validation modules
        self.validators = {
            'security': SecurityValidator(self.config.get('security', {})),
            'quality': CodeQualityValidator(self.config.get('quality', {})),
            'format': FormatValidator(self.config.get('format', {})),
            'business': BusinessRuleValidator(self.config.get('business', {})),
            'compliance': ComplianceValidator(self.config.get('compliance', {}))
        }
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load governance configuration"""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        
        # Default configuration
        return {
            'security': {
                'scan_secrets': True,
                'check_dependencies': True,
                'validate_permissions': True
            },
            'quality': {
                'min_coverage': 80,
                'max_complexity': 10,
                'enforce_typing': True
            },
            'format': {
                'auto_fix': True,
                'enforce_style': True
            },
            'business': {
                'require_documentation': True,
                'enforce_naming': True
            },
            'enforcement': {
                'fail_on_warning': False,
                'bypass_keyword': 'GOVERNANCE_BYPASS',
                'max_violations': 5
            }
        }
    
    def get_staged_files(self) -> List[str]:
        """Get list of staged files"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True, text=True, check=True
            )
            return [f for f in result.stdout.strip().split('\n') if f]
        except subprocess.CalledProcessError:
            return []
    
    def run_validation(self) -> bool:
        """Run all validations and return success status"""
        print("🔍 Running Pre-Commit Governance Validation...")
        print("=" * 60)
        
        if not self.staged_files:
            print("ℹ️  No files staged for commit")
            return True
        
        print(f"📁 Validating {len(self.staged_files)} staged files")
        
        # Run each validator
        for validator_name, validator in self.validators.items():
            print(f"\n🔧 Running {validator_name.title()} Validation...")
            try:
                validator_results = validator.validate(self.staged_files)
                self.results.extend(validator_results)
                
                # Show immediate feedback
                passed = len([r for r in validator_results if r.passed])
                total = len(validator_results)
                if total > 0:
                    print(f"   ✅ {passed}/{total} checks passed")
            except Exception as e:
                self.results.append(ValidationResult(
                    passed=False,
                    message=f"{validator_name} validation failed: {e}",
                    severity="error",
                    rule_id=f"{validator_name}_exception"
                ))
        
        # Analyze results and make decision
        return self.make_governance_decision()
    
    def make_governance_decision(self) -> bool:
        """Analyze validation results and make commit decision"""
        errors = [r for r in self.results if not r.passed and r.severity == "error"]
        warnings = [r for r in self.results if not r.passed and r.severity == "warning"]
        
        print("\n" + "=" * 60)
        print("📊 GOVERNANCE VALIDATION RESULTS")
        print("=" * 60)
        
        # Show errors
        if errors:
            print(f"\n❌ {len(errors)} Critical Issues Found:")
            for error in errors:
                print(f"   • {error.message}")
                if error.suggestion:
                    print(f"     💡 {error.suggestion}")
        
        # Show warnings
        if warnings:
            print(f"\n⚠️  {len(warnings)} Warnings Found:")
            for warning in warnings[:5]:  # Limit output
                print(f"   • {warning.message}")
        
        # Check enforcement rules
        enforcement = self.config.get('enforcement', {})
        fail_on_warning = enforcement.get('fail_on_warning', False)
        max_violations = enforcement.get('max_violations', 5)
        
        # Make decision
        total_violations = len(errors) + (len(warnings) if fail_on_warning else 0)
        
        if total_violations == 0:
            print("\n✅ ALL VALIDATIONS PASSED")
            print("🚀 Commit approved by governance system")
            self.log_governance_decision("approved", "All validations passed")
            return True
        elif len(errors) > 0:
            print(f"\n🚫 COMMIT BLOCKED - {len(errors)} critical issues must be fixed")
            print("\n🔧 Quick fixes:")
            self.suggest_quick_fixes(errors)
            self.log_governance_decision("blocked", f"{len(errors)} critical issues")
            return False
        elif fail_on_warning and len(warnings) > max_violations:
            print(f"\n🚫 COMMIT BLOCKED - Too many warnings ({len(warnings)} > {max_violations})")
            self.log_governance_decision("blocked", f"Too many warnings: {len(warnings)}")
            return False
        else:
            print(f"\n⚠️  COMMIT ALLOWED WITH WARNINGS ({len(warnings)} warnings)")
            print("💡 Consider addressing warnings before pushing to main branch")
            self.log_governance_decision("approved_with_warnings", f"{len(warnings)} warnings")
            return True
    
    def suggest_quick_fixes(self, errors: List[ValidationResult]) -> None:
        """Suggest automated fixes for common issues"""
        fix_commands = []
        
        for error in errors:
            if 'formatting' in error.rule_id:
                fix_commands.append("Run: black . && isort .")
            elif 'security' in error.rule_id and 'secret' in error.message:
                fix_commands.append("Remove secrets and use environment variables")
            elif 'typing' in error.rule_id:
                fix_commands.append("Add type annotations with: mypy --install-types")
        
        if fix_commands:
            print("\n🛠️  Suggested fixes:")
            for cmd in set(fix_commands):  # Remove duplicates
                print(f"   {cmd}")
        
        print(f"\n🚨 To bypass governance (emergency only):")
        print(f"   git commit -m 'message' -m 'GOVERNANCE_BYPASS: emergency fix'")
    
    def log_governance_decision(self, decision: str, reason: str) -> None:
        """Log governance decision for audit trail"""
        log_dir = Path(".governance/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'hook': 'pre-commit',
            'decision': decision,
            'reason': reason,
            'files': self.staged_files,
            'user': self.get_git_user(),
            'commit_hash': self.get_current_commit_hash(),
            'validation_results': len(self.results),
            'errors': len([r for r in self.results if not r.passed and r.severity == "error"]),
            'warnings': len([r for r in self.results if not r.passed and r.severity == "warning"])
        }
        
        log_file = log_dir / "governance.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def get_git_user(self) -> str:
        """Get current git user"""
        try:
            result = subprocess.run(['git', 'config', 'user.name'], 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return 'unknown'
    
    def get_current_commit_hash(self) -> str:
        """Get current commit hash (for tracking)"""
        try:
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True)
            return result.stdout.strip()[:8]
        except:
            return 'unknown'

class SecurityValidator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.secret_patterns = [
            r'(?i)(api_key|apikey|api-key)\s*[=:]\s*["\']?([a-z0-9]{20,})["\']?',
            r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']?([^"\'\s]{8,})["\']?',
            r'(?i)(secret|token)\s*[=:]\s*["\']?([a-z0-9]{16,})["\']?',
            r'(?i)(private_key|privatekey)\s*[=:]\s*["\']?([a-z0-9+/=]{100,})["\']?',
            r'(?i)sk-[a-z0-9]{48}',  # OpenAI API keys
            r'(?i)xoxb-[0-9]{11}-[0-9]{11}-[a-zA-Z0-9]{24}',  # Slack tokens
            r'(?i)AKIA[0-9A-Z]{16}',  # AWS access keys
        ]
        
        self.dangerous_functions = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'subprocess\.call\s*\(',
            r'os\.system\s*\(',
            r'__import__\s*\(',
        ]
    
    def validate(self, files: List[str]) -> List[ValidationResult]:
        """Run security validation on files"""
        results = []
        
        if not self.config.get('scan_secrets', True):
            return results
        
        for file_path in files:
            if not Path(file_path).exists():
                continue
                
            try:
                results.extend(self.scan_file_for_secrets(file_path))
                results.extend(self.scan_dangerous_patterns(file_path))
                results.extend(self.check_file_permissions(file_path))
            except Exception as e:
                results.append(ValidationResult(
                    passed=False,
                    message=f"Security scan failed for {file_path}: {e}",
                    severity="warning",
                    rule_id="security_scan_error",
                    file_path=file_path
                ))
        
        return results
    
    def scan_file_for_secrets(self, file_path: str) -> List[ValidationResult]:
        """Scan file for potential secrets"""
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            for i, line in enumerate(content.split('\n'), 1):
                for pattern in self.secret_patterns:
                    if re.search(pattern, line):
                        # Skip obvious test/example patterns
                        if any(skip in line.lower() for skip in 
                              ['test', 'example', 'sample', 'demo', 'fake', 'mock', 'xxx']):
                            continue
                        
                        results.append(ValidationResult(
                            passed=False,
                            message=f"Potential secret detected in {file_path}:{i}",
                            suggestion="Use environment variables or secure credential storage",
                            severity="error",
                            rule_id="security_secret_detected",
                            file_path=file_path
                        ))
                        
        except UnicodeDecodeError:
            # Binary file, skip
            pass
        except Exception as e:
            results.append(ValidationResult(
                passed=False,
                message=f"Failed to scan {file_path} for secrets: {e}",
                severity="warning",
                rule_id="security_scan_error"
            ))
        
        return results
    
    def scan_dangerous_patterns(self, file_path: str) -> List[ValidationResult]:
        """Scan for dangerous code patterns"""
        results = []
        
        if not file_path.endswith(('.py', '.js', '.ts')):
            return results
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            for pattern in self.dangerous_functions:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    results.append(ValidationResult(
                        passed=False,
                        message=f"Dangerous function usage in {file_path}:{line_num}: {match.group()}",
                        suggestion="Use safer alternatives or add explicit security review",
                        severity="warning",
                        rule_id="security_dangerous_function",
                        file_path=file_path
                    ))
        except Exception:
            pass
        
        return results
    
    def check_file_permissions(self, file_path: str) -> List[ValidationResult]:
        """Check for overly permissive file permissions"""
        results = []
        
        try:
            file_stat = Path(file_path).stat()
            permissions = oct(file_stat.st_mode)[-3:]
            
            # Check for world-writable files
            if permissions.endswith('7') or permissions.endswith('6'):
                results.append(ValidationResult(
                    passed=False,
                    message=f"Overly permissive permissions on {file_path}: {permissions}",
                    suggestion="Remove world-write permissions: chmod 644 or chmod 755",
                    severity="warning",
                    rule_id="security_file_permissions",
                    file_path=file_path
                ))
        except Exception:
            pass
        
        return results

class CodeQualityValidator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.min_coverage = config.get('min_coverage', 80)
        self.max_complexity = config.get('max_complexity', 10)
        self.enforce_typing = config.get('enforce_typing', True)
    
    def validate(self, files: List[str]) -> List[ValidationResult]:
        """Run code quality validation"""
        results = []
        
        python_files = [f for f in files if f.endswith('.py')]
        if python_files:
            results.extend(self.check_python_quality(python_files))
            if self.config.get('check_coverage', True):
                results.extend(self.check_test_coverage(python_files))
        
        js_files = [f for f in files if f.endswith(('.js', '.ts'))]
        if js_files:
            results.extend(self.check_js_quality(js_files))
        
        return results
    
    def check_python_quality(self, files: List[str]) -> List[ValidationResult]:
        """Check Python code quality with multiple tools"""
        results = []
        
        # Run flake8 for style and complexity
        try:
            cmd = ['flake8', '--max-complexity', str(self.max_complexity)] + files
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        results.append(ValidationResult(
                            passed=False,
                            message=f"Style violation: {line}",
                            suggestion="Run: black . && isort . to auto-fix formatting",
                            severity="error",
                            rule_id="quality_style_violation"
                        ))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            results.append(ValidationResult(
                passed=True,
                message="flake8 not available, skipping style check",
                severity="info",
                rule_id="quality_tool_missing"
            ))
        
        # Check type annotations if required
        if self.enforce_typing:
            results.extend(self.check_type_annotations(files))
        
        return results
    
    def check_type_annotations(self, files: List[str]) -> List[ValidationResult]:
        """Check for type annotations in Python files"""
        results = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for function definitions without type hints
                func_pattern = r'^def\s+(\w+)\s*\([^)]*\)\s*:'
                functions = re.finditer(func_pattern, content, re.MULTILINE)
                
                missing_annotations = 0
                for func in functions:
                    func_name = func.group(1)
                    # Skip test functions and private methods
                    if func_name.startswith('test_') or func_name.startswith('_'):
                        continue
                    
                    # Check if function has return type annotation
                    func_line = func.group(0)
                    if '->' not in func_line:
                        missing_annotations += 1
                
                if missing_annotations > 0:
                    results.append(ValidationResult(
                        passed=False,
                        message=f"{file_path}: {missing_annotations} functions missing type annotations",
                        suggestion="Add type hints: def func(param: str) -> str:",
                        severity="warning",
                        rule_id="quality_missing_types",
                        file_path=file_path
                    ))
            except Exception:
                pass
        
        return results
    
    def check_test_coverage(self, files: List[str]) -> List[ValidationResult]:
        """Check test coverage for modified files"""
        results = []
        
        try:
            # Run coverage on modified files
            result = subprocess.run([
                'python', '-m', 'pytest', '--cov=.', '--cov-report=json',
                '--cov-fail-under=0'  # Don't fail, just generate report
            ], capture_output=True, text=True, timeout=120)
            
            # Parse coverage report
            coverage_file = Path('coverage.json')
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                
                total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
                
                if total_coverage < self.min_coverage:
                    results.append(ValidationResult(
                        passed=False,
                        message=f"Test coverage too low: {total_coverage:.1f}% < {self.min_coverage}%",
                        suggestion="Add more tests or adjust coverage threshold",
                        severity="warning",
                        rule_id="quality_low_coverage"
                    ))
                else:
                    results.append(ValidationResult(
                        passed=True,
                        message=f"Test coverage: {total_coverage:.1f}%",
                        severity="info",
                        rule_id="quality_coverage_check"
                    ))
                
                # Clean up
                coverage_file.unlink()
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            results.append(ValidationResult(
                passed=True,
                message="Coverage check skipped (pytest/coverage not available)",
                severity="info",
                rule_id="quality_coverage_skip"
            ))
        
        return results
    
    def check_js_quality(self, files: List[str]) -> List[ValidationResult]:
        """Check JavaScript/TypeScript quality"""
        results = []
        
        # Run ESLint if available
        try:
            cmd = ['npx', 'eslint'] + files
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                for line in result.stdout.split('\n'):
                    if 'error' in line or 'warning' in line:
                        results.append(ValidationResult(
                            passed=False,
                            message=f"ESLint: {line.strip()}",
                            suggestion="Fix linting errors or adjust ESLint config",
                            severity="warning",
                            rule_id="quality_js_lint"
                        ))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            results.append(ValidationResult(
                passed=True,
                message="ESLint not available, skipping JS quality check",
                severity="info",
                rule_id="quality_js_skip"
            ))
        
        return results

class FormatValidator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.auto_fix = config.get('auto_fix', True)
    
    def validate(self, files: List[str]) -> List[ValidationResult]:
        """Validate and optionally fix formatting"""
        results = []
        
        python_files = [f for f in files if f.endswith('.py')]
        if python_files:
            results.extend(self.format_python_files(python_files))
        
        js_files = [f for f in files if f.endswith(('.js', '.ts', '.json'))]
        if js_files:
            results.extend(self.format_js_files(js_files))
        
        return results
    
    def format_python_files(self, files: List[str]) -> List[ValidationResult]:
        """Format Python files with black and isort"""
        results = []
        
        if self.auto_fix:
            # Run black formatter
            try:
                result = subprocess.run(['black', '--check'] + files, 
                                      capture_output=True, text=True, timeout=60)
                
                if result.returncode != 0:
                    # Files need formatting, apply fixes
                    subprocess.run(['black'] + files, timeout=60)
                    subprocess.run(['isort'] + files, timeout=60)
                    
                    results.append(ValidationResult(
                        passed=True,
                        message=f"Auto-formatted {len(files)} Python files",
                        severity="info",
                        rule_id="format_python_fixed"
                    ))
                else:
                    results.append(ValidationResult(
                        passed=True,
                        message="Python formatting is correct",
                        severity="info",
                        rule_id="format_python_ok"
                    ))
            except (subprocess.TimeoutExpired, FileNotFoundError):
                results.append(ValidationResult(
                    passed=True,
                    message="Python formatting tools not available",
                    severity="info",
                    rule_id="format_python_skip"
                ))
        
        return results
    
    def format_js_files(self, files: List[str]) -> List[ValidationResult]:
        """Format JavaScript/TypeScript files with prettier"""
        results = []
        
        if self.auto_fix:
            try:
                result = subprocess.run(['npx', 'prettier', '--check'] + files,
                                      capture_output=True, text=True, timeout=60)
                
                if result.returncode != 0:
                    # Files need formatting, apply fixes
                    subprocess.run(['npx', 'prettier', '--write'] + files, timeout=60)
                    
                    results.append(ValidationResult(
                        passed=True,
                        message=f"Auto-formatted {len(files)} JS/TS files",
                        severity="info",
                        rule_id="format_js_fixed"
                    ))
                else:
                    results.append(ValidationResult(
                        passed=True,
                        message="JS/TS formatting is correct",
                        severity="info",
                        rule_id="format_js_ok"
                    ))
            except (subprocess.TimeoutExpired, FileNotFoundError):
                results.append(ValidationResult(
                    passed=True,
                    message="Prettier not available, skipping JS formatting",
                    severity="info",
                    rule_id="format_js_skip"
                ))
        
        return results

class BusinessRuleValidator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def validate(self, files: List[str]) -> List[ValidationResult]:
        """Validate business rules and documentation requirements"""
        results = []
        
        for file_path in files:
            if file_path.endswith('.py'):
                results.extend(self.check_documentation_requirements(file_path))
                results.extend(self.check_naming_conventions(file_path))
        
        return results
    
    def check_documentation_requirements(self, file_path: str) -> List[ValidationResult]:
        """Check for required documentation"""
        results = []
        
        if not self.config.get('require_documentation', True):
            return results
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for module docstring
            if not content.strip().startswith('"""') and not content.strip().startswith("'''"):
                results.append(ValidationResult(
                    passed=False,
                    message=f"{file_path}: Missing module docstring",
                    suggestion="Add module docstring at top of file",
                    severity="warning",
                    rule_id="business_missing_docstring",
                    file_path=file_path
                ))
            
            # Check for class docstrings
            class_pattern = r'class\s+\w+.*?:'
            classes = re.finditer(class_pattern, content)
            
            for class_match in classes:
                class_end = class_match.end()
                next_content = content[class_end:class_end+200]
                if not next_content.strip().startswith(('"""', "'''")):
                    results.append(ValidationResult(
                        passed=False,
                        message=f"{file_path}: Class missing docstring",
                        suggestion="Add docstring to class definition",
                        severity="warning",
                        rule_id="business_class_docstring",
                        file_path=file_path
                    ))
        
        except Exception:
            pass
        
        return results
    
    def check_naming_conventions(self, file_path: str) -> List[ValidationResult]:
        """Check naming conventions"""
        results = []
        
        if not self.config.get('enforce_naming', True):
            return results
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for camelCase in Python (should be snake_case)
            camel_case_pattern = r'\b[a-z]+[A-Z][a-zA-Z]*\b'
            camel_case_vars = re.findall(camel_case_pattern, content)
            
            # Filter out common exceptions
            exceptions = {'setUp', 'tearDown', 'assertTrue', 'assertEqual'}
            violations = [var for var in camel_case_vars if var not in exceptions]
            
            if violations:
                results.append(ValidationResult(
                    passed=False,
                    message=f"{file_path}: Found camelCase variables: {', '.join(violations[:5])}",
                    suggestion="Use snake_case naming convention for Python",
                    severity="warning",
                    rule_id="business_naming_convention",
                    file_path=file_path
                ))
        
        except Exception:
            pass
        
        return results

class ComplianceValidator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def validate(self, files: List[str]) -> List[ValidationResult]:
        """Validate compliance requirements"""
        results = []
        
        # Check for required license headers
        if self.config.get('require_license_header', False):
            results.extend(self.check_license_headers(files))
        
        # Check for prohibited content
        if self.config.get('scan_prohibited_content', True):
            results.extend(self.scan_prohibited_content(files))
        
        return results
    
    def check_license_headers(self, files: List[str]) -> List[ValidationResult]:
        """Check for required license headers"""
        results = []
        
        license_keywords = ['copyright', 'license', 'all rights reserved']
        
        for file_path in files:
            if not file_path.endswith(('.py', '.js', '.ts')):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    first_50_lines = '\n'.join(f.readlines()[:50]).lower()
                
                if not any(keyword in first_50_lines for keyword in license_keywords):
                    results.append(ValidationResult(
                        passed=False,
                        message=f"{file_path}: Missing license header",
                        suggestion="Add copyright/license header to file",
                        severity="warning",
                        rule_id="compliance_license_header",
                        file_path=file_path
                    ))
            except Exception:
                pass
        
        return results
    
    def scan_prohibited_content(self, files: List[str]) -> List[ValidationResult]:
        """Scan for prohibited content or patterns"""
        results = []
        
        prohibited_patterns = [
            r'(?i)(hack|workaround|todo|fixme|xxx)\s*:',
            r'(?i)temp(orary)?|tmp',
            r'(?i)(debug|test)\s*(print|console\.log)',
        ]
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for pattern in prohibited_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        results.append(ValidationResult(
                            passed=False,
                            message=f"{file_path}:{line_num}: Prohibited pattern: {match.group()}",
                            suggestion="Remove temporary/debug code before commit",
                            severity="warning",
                            rule_id="compliance_prohibited_content",
                            file_path=file_path
                        ))
            except Exception:
                pass
        
        return results

def main():
    """Main pre-commit hook execution"""
    # Check for bypass
    bypass_keyword = os.environ.get('GOVERNANCE_BYPASS')
    if bypass_keyword:
        print("🚨 GOVERNANCE BYPASSED - Proceeding without validation")
        return 0
    
    # Check commit message for bypass
    try:
        result = subprocess.run(['git', 'log', '-1', '--pretty=%B'], 
                              capture_output=True, text=True)
        if 'GOVERNANCE_BYPASS' in result.stdout:
            print("🚨 GOVERNANCE BYPASSED via commit message")
            return 0
    except:
        pass
    
    # Run governance validation
    hook = PreCommitGovernanceHook()
    success = hook.run_validation()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
```

### Common Pain Points

1. **Performance Issues**: Complex validation can slow commits significantly
2. **False Positives**: Overly strict rules can block legitimate commits
3. **Tool Dependencies**: Requires external tools (black, flake8, etc.)
4. **Configuration Complexity**: Many moving parts to configure properly
5. **Bypass Abuse**: Emergency bypass mechanisms can be overused

### Installation Script

```python
#!/usr/bin/env python3
"""Install pre-commit governance hook"""
import os
import stat
from pathlib import Path

def install_pre_commit_hook():
    """Install the pre-commit hook"""
    # Find .git directory
    git_dir = Path.cwd()
    while git_dir != git_dir.parent:
        if (git_dir / '.git').exists():
            break
        git_dir = git_dir.parent
    else:
        print("❌ Not in a git repository")
        return False
    
    # Create hooks directory
    hooks_dir = git_dir / '.git' / 'hooks'
    hooks_dir.mkdir(exist_ok=True)
    
    # Write hook script
    hook_path = hooks_dir / 'pre-commit'
    hook_content = f"""#!/usr/bin/env python3
import sys
sys.path.insert(0, '{Path(__file__).parent}')
from governance_pre_commit import main
sys.exit(main())
"""
    
    with open(hook_path, 'w') as f:
        f.write(hook_content)
    
    # Make executable
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
    
    print(f"✅ Pre-commit hook installed at {hook_path}")
    return True
```

---

## Hook 2: pre-push - Integration Gatekeeper

**Trigger**: Before push to remote repository  
**Can Block**: ✅ Yes  
**Primary Purpose**: Integration tests, security scans, deployment validation

### Implementation Example

```python
#!/usr/bin/env python3
"""
Pre-Push Hook - Integration and Security Validation
Runs comprehensive tests before code reaches remote repository
"""
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List

class PrePushGovernanceHook:
    def __init__(self):
        self.config = self.load_config()
        self.remote_name = sys.argv[1] if len(sys.argv) > 1 else 'origin'
        self.remote_url = sys.argv[2] if len(sys.argv) > 2 else ''
        
    def load_config(self) -> Dict[str, Any]:
        """Load pre-push configuration"""
        config_file = Path('.governance/pre-push.json')
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        
        return {
            'run_integration_tests': True,
            'security_scan': True,
            'dependency_check': True,
            'performance_baseline': True,
            'branch_protection': {
                'main': {'require_tests': True, 'require_review': True},
                'develop': {'require_tests': True},
                'feature/*': {'require_tests': False}
            }
        }
    
    def get_push_info(self) -> Dict[str, Any]:
        """Get information about the push"""
        # Read push information from stdin
        push_info = {'refs': []}
        
        for line in sys.stdin:
            if line.strip():
                local_ref, local_sha, remote_ref, remote_sha = line.strip().split()
                push_info['refs'].append({
                    'local_ref': local_ref,
                    'local_sha': local_sha,
                    'remote_ref': remote_ref,
                    'remote_sha': remote_sha,
                    'branch': local_ref.split('/')[-1]
                })
        
        return push_info
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration test suite"""
        if not self.config.get('run_integration_tests', True):
            return {'passed': True, 'message': 'Integration tests disabled'}
        
        print("🧪 Running integration test suite...")
        
        try:
            # Run pytest with integration markers
            result = subprocess.run([
                'python', '-m', 'pytest', 
                '-m', 'integration',
                '--tb=short',
                '--timeout=300'  # 5 minute timeout
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                return {
                    'passed': True, 
                    'message': 'All integration tests passed',
                    'output': result.stdout
                }
            else:
                return {
                    'passed': False,
                    'message': 'Integration tests failed',
                    'output': result.stdout + result.stderr
                }
        
        except subprocess.TimeoutExpired:
            return {
                'passed': False,
                'message': 'Integration tests timed out (>10 minutes)',
                'output': 'Tests exceeded maximum execution time'
            }
        except Exception as e:
            return {
                'passed': False,
                'message': f'Failed to run integration tests: {e}',
                'output': str(e)
            }
    
    def run_security_scan(self) -> Dict[str, Any]:
        """Run security vulnerability scan"""
        if not self.config.get('security_scan', True):
            return {'passed': True, 'message': 'Security scan disabled'}
        
        print("🔒 Running security vulnerability scan...")
        
        results = []
        
        # Run bandit for Python security issues
        try:
            result = subprocess.run([
                'bandit', '-r', '.', '-f', 'json',
                '-x', 'tests/,venv/,.venv/'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                results.append({
                    'tool': 'bandit',
                    'passed': True,
                    'message': 'No security issues found'
                })
            else:
                # Parse bandit results
                try:
                    bandit_data = json.loads(result.stdout)
                    high_severity = len([r for r in bandit_data.get('results', []) 
                                        if r.get('issue_severity') == 'HIGH'])
                    
                    if high_severity > 0:
                        results.append({
                            'tool': 'bandit',
                            'passed': False,
                            'message': f'Found {high_severity} high-severity security issues',
                            'output': result.stdout
                        })
                    else:
                        results.append({
                            'tool': 'bandit',
                            'passed': True,
                            'message': 'No high-severity security issues'
                        })
                except json.JSONDecodeError:
                    results.append({
                        'tool': 'bandit',
                        'passed': False,
                        'message': 'Failed to parse bandit output',
                        'output': result.stdout
                    })
        
        except subprocess.TimeoutExpired:
            results.append({
                'tool': 'bandit',
                'passed': False,
                'message': 'Security scan timed out'
            })
        except FileNotFoundError:
            results.append({
                'tool': 'bandit',
                'passed': True,
                'message': 'Bandit not installed, skipping Python security scan'
            })
        
        # Run npm audit for Node.js projects
        if Path('package.json').exists():
            try:
                result = subprocess.run([
                    'npm', 'audit', '--json'
                ], capture_output=True, text=True, timeout=60)
                
                audit_data = json.loads(result.stdout)
                vulnerabilities = audit_data.get('metadata', {}).get('vulnerabilities', {})
                critical = vulnerabilities.get('critical', 0)
                high = vulnerabilities.get('high', 0)
                
                if critical > 0 or high > 0:
                    results.append({
                        'tool': 'npm-audit',
                        'passed': False,
                        'message': f'Found {critical} critical and {high} high severity vulnerabilities',
                        'output': result.stdout
                    })
                else:
                    results.append({
                        'tool': 'npm-audit',
                        'passed': True,
                        'message': 'No high/critical vulnerabilities in dependencies'
                    })
            
            except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
                results.append({
                    'tool': 'npm-audit',
                    'passed': True,
                    'message': 'NPM audit unavailable or failed'
                })
        
        # Aggregate results
        failed_scans = [r for r in results if not r['passed']]
        if failed_scans:
            return {
                'passed': False,
                'message': f'Security issues found by {len(failed_scans)} tools',
                'details': failed_scans
            }
        else:
            return {
                'passed': True,
                'message': f'Security scans passed ({len(results)} tools)',
                'details': results
            }
    
    def check_branch_protection(self, push_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check branch protection rules"""
        protection_rules = self.config.get('branch_protection', {})
        
        for ref in push_info['refs']:
            branch = ref['branch']
            
            # Find matching protection rule
            rule = None
            if branch in protection_rules:
                rule = protection_rules[branch]
            else:
                # Check wildcard matches
                for pattern, pattern_rule in protection_rules.items():
                    if '*' in pattern:
                        if pattern.replace('*', '').strip('/') in branch:
                            rule = pattern_rule
                            break
            
            if rule:
                # Check if tests are required
                if rule.get('require_tests', False):
                    if not self.has_recent_test_run():
                        return {
                            'passed': False,
                            'message': f'Branch {branch} requires tests to be run before push',
                            'suggestion': 'Run: python -m pytest'
                        }
                
                # Check if review is required (simplified check)
                if rule.get('require_review', False):
                    if not self.has_approval_marker():
                        return {
                            'passed': False,
                            'message': f'Branch {branch} requires code review approval',
                            'suggestion': 'Add "Reviewed-by: <reviewer>" to commit message'
                        }
        
        return {'passed': True, 'message': 'Branch protection rules satisfied'}
    
    def has_recent_test_run(self) -> bool:
        """Check if tests have been run recently"""
        test_artifacts = [
            '.coverage',
            'pytest_cache/',
            'test-results.xml',
            '.pytest_cache/'
        ]
        
        return any(Path(artifact).exists() for artifact in test_artifacts)
    
    def has_approval_marker(self) -> bool:
        """Check if latest commit has approval marker"""
        try:
            result = subprocess.run([
                'git', 'log', '-1', '--pretty=%B'
            ], capture_output=True, text=True)
            
            commit_msg = result.stdout.lower()
            approval_markers = [
                'reviewed-by:',
                'approved-by:',
                'lgtm',
                'code-review: approved'
            ]
            
            return any(marker in commit_msg for marker in approval_markers)
        except:
            return False
    
    def run_performance_baseline(self) -> Dict[str, Any]:
        """Run performance baseline tests"""
        if not self.config.get('performance_baseline', False):
            return {'passed': True, 'message': 'Performance baseline disabled'}
        
        print("⚡ Running performance baseline tests...")
        
        try:
            # Run performance tests with pytest-benchmark
            result = subprocess.run([
                'python', '-m', 'pytest', 
                '-m', 'benchmark',
                '--benchmark-json=.benchmark.json'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Check if performance regression occurred
                if Path('.benchmark.json').exists():
                    with open('.benchmark.json') as f:
                        benchmark_data = json.load(f)
                    
                    # Simple regression check (you'd implement more sophisticated logic)
                    return {
                        'passed': True,
                        'message': 'Performance baseline tests passed',
                        'details': f"Ran {len(benchmark_data.get('benchmarks', []))} benchmarks"
                    }
                else:
                    return {
                        'passed': True,
                        'message': 'Performance tests completed (no baseline data)'
                    }
            else:
                return {
                    'passed': False,
                    'message': 'Performance baseline tests failed',
                    'output': result.stdout + result.stderr
                }
        
        except subprocess.TimeoutExpired:
            return {
                'passed': False,
                'message': 'Performance tests timed out'
            }
        except Exception as e:
            return {
                'passed': True,
                'message': f'Performance tests unavailable: {e}'
            }
    
    def run_validation(self) -> bool:
        """Run all pre-push validations"""
        print("🚀 Running Pre-Push Governance Validation")
        print("=" * 60)
        
        push_info = self.get_push_info()
        
        if not push_info['refs']:
            print("ℹ️  No refs to push")
            return True
        
        print(f"📤 Pushing to {self.remote_name}: {self.remote_url}")
        for ref in push_info['refs']:
            print(f"   {ref['local_ref']} -> {ref['remote_ref']}")
        
        # Run all validations
        validations = [
            ('Branch Protection', lambda: self.check_branch_protection(push_info)),
            ('Integration Tests', self.run_integration_tests),
            ('Security Scan', self.run_security_scan),
            ('Performance Baseline', self.run_performance_baseline)
        ]
        
        all_passed = True
        
        for name, validator in validations:
            print(f"\n🔍 {name}...")
            try:
                result = validator()
                
                if result['passed']:
                    print(f"✅ {result['message']}")
                else:
                    print(f"❌ {result['message']}")
                    if 'suggestion' in result:
                        print(f"💡 {result['suggestion']}")
                    if 'output' in result and result['output']:
                        print(f"📝 Output:\n{result['output'][:500]}")
                    all_passed = False
            
            except Exception as e:
                print(f"⚠️  {name} validation failed: {e}")
                all_passed = False
        
        print("\n" + "=" * 60)
        
        if all_passed:
            print("✅ ALL VALIDATIONS PASSED - Push approved")
            self.log_push_decision('approved', push_info)
        else:
            print("❌ PUSH BLOCKED - Fix issues above")
            print("\n🚨 To bypass (emergency only):")
            print("   git push --no-verify")
            self.log_push_decision('blocked', push_info)
        
        return all_passed
    
    def log_push_decision(self, decision: str, push_info: Dict[str, Any]) -> None:
        """Log push decision for audit"""
        log_dir = Path('.governance/logs')
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            'timestamp': subprocess.run(['date'], capture_output=True, text=True).stdout.strip(),
            'hook': 'pre-push',
            'decision': decision,
            'remote': self.remote_name,
            'refs': push_info['refs'],
            'user': subprocess.run(['git', 'config', 'user.name'], 
                                 capture_output=True, text=True).stdout.strip()
        }
        
        log_file = log_dir / 'governance.jsonl'
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

def main():
    """Main pre-push hook execution"""
    hook = PrePushGovernanceHook()
    success = hook.run_validation()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
```

### Common Pain Points

1. **Long Execution Time**: Integration tests can take 10+ minutes
2. **Network Dependencies**: Security scans may require internet access
3. **Test Environment**: May need specific test setup/databases
4. **Stdin Processing**: Reading push information from stdin is error-prone
5. **Resource Intensive**: Can consume significant CPU/memory

---

## Hook 3: commit-msg - Message Governance

**Trigger**: After commit message is written  
**Can Block**: ✅ Yes  
**Primary Purpose**: Enforce commit message standards, link to tickets

### Implementation Example

```python
#!/usr/bin/env python3
"""
Commit Message Governance Hook
Validates commit message format, content, and business rules
"""
import sys
import re
from pathlib import Path
from typing import List, Dict, Any
import json

class CommitMessageValidator:
    def __init__(self):
        self.config = self.load_config()
        self.commit_file = sys.argv[1] if len(sys.argv) > 1 else '.git/COMMIT_EDITMSG'
    
    def load_config(self) -> Dict[str, Any]:
        """Load commit message validation config"""
        config_file = Path('.governance/commit-msg.json')
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        
        return {
            'conventional_commits': True,
            'max_subject_length': 72,
            'min_subject_length': 10,
            'require_ticket_reference': True,
            'ticket_patterns': [
                r'JIRA-\d+',
                r'#\d+',
                r'TICKET-\d+'
            ],
            'forbidden_patterns': [
                r'(?i)\bwip\b',
                r'(?i)\bfixup\b',
                r'(?i)\bsquash\b'
            ],
            'required_sections': {
                'breaking_changes': r'BREAKING CHANGE:',
                'closes_issues': r'(?i)(?:closes?|fixes?|resolves?)\s+#\d+'
            }
        }
    
    def read_commit_message(self) -> str:
        """Read the commit message from file"""
        try:
            with open(self.commit_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"❌ Failed to read commit message: {e}")
            return ""
    
    def validate_conventional_commits(self, message: str) -> List[Dict[str, Any]]:
        """Validate conventional commit format"""
        if not self.config.get('conventional_commits', True):
            return []
        
        errors = []
        lines = message.split('\n')
        subject = lines[0] if lines else ""
        
        # Conventional commit pattern: type(scope): description
        pattern = r'^(feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert)(\(.+\))?: .+'
        
        if not re.match(pattern, subject):
            errors.append({
                'type': 'format',
                'message': 'Subject must follow conventional commits format',
                'suggestion': 'Use: type(scope): description (e.g., "feat(auth): add OAuth login")',
                'line': 1
            })
        
        # Check for valid types
        valid_types = {
            'feat': 'A new feature',
            'fix': 'A bug fix',
            'docs': 'Documentation only changes',
            'style': 'Changes that do not affect code meaning',
            'refactor': 'Code change that neither fixes a bug nor adds a feature',
            'perf': 'A code change that improves performance',
            'test': 'Adding missing tests or correcting existing tests',
            'chore': 'Changes to build process or auxiliary tools',
            'ci': 'Changes to CI configuration files and scripts',
            'build': 'Changes that affect the build system',
            'revert': 'Reverts a previous commit'
        }
        
        type_match = re.match(r'^(\w+)', subject)
        if type_match and type_match.group(1) not in valid_types:
            errors.append({
                'type': 'format',
                'message': f'Invalid commit type: {type_match.group(1)}',
                'suggestion': f'Valid types: {", ".join(valid_types.keys())}',
                'line': 1
            })
        
        return errors
    
    def validate_message_length(self, message: str) -> List[Dict[str, Any]]:
        """Validate message length constraints"""
        errors = []
        lines = message.split('\n')
        subject = lines[0] if lines else ""
        
        max_length = self.config.get('max_subject_length', 72)
        min_length = self.config.get('min_subject_length', 10)
        
        if len(subject) > max_length:
            errors.append({
                'type': 'length',
                'message': f'Subject too long: {len(subject)} > {max_length} characters',
                'suggestion': 'Keep subject line under 72 characters',
                'line': 1
            })
        
        if len(subject) < min_length:
            errors.append({
                'type': 'length',
                'message': f'Subject too short: {len(subject)} < {min_length} characters',
                'suggestion': 'Subject should be descriptive (at least 10 characters)',
                'line': 1
            })
        
        # Check body line lengths
        for i, line in enumerate(lines[1:], 2):
            if line and len(line) > 80:
                errors.append({
                    'type': 'length',
                    'message': f'Body line too long: {len(line)} > 80 characters',
                    'suggestion': 'Wrap body lines at 80 characters',
                    'line': i
                })
        
        return errors
    
    def validate_ticket_reference(self, message: str) -> List[Dict[str, Any]]:
        """Validate ticket/issue reference"""
        if not self.config.get('require_ticket_reference', True):
            return []
        
        errors = []
        ticket_patterns = self.config.get('ticket_patterns', [])
        
        has_ticket = False
        for pattern in ticket_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                has_ticket = True
                break
        
        if not has_ticket:
            errors.append({
                'type': 'business',
                'message': 'Commit must reference a ticket/issue',
                'suggestion': f'Add ticket reference (patterns: {", ".join(ticket_patterns)})',
                'line': 0
            })
        
        return errors
    
    def validate_forbidden_patterns(self, message: str) -> List[Dict[str, Any]]:
        """Check for forbidden patterns in commit message"""
        errors = []
        forbidden = self.config.get('forbidden_patterns', [])
        
        for pattern in forbidden:
            if re.search(pattern, message):
                errors.append({
                    'type': 'policy',
                    'message': f'Forbidden pattern detected: {pattern}',
                    'suggestion': 'Remove or reword the forbidden content',
                    'line': 0
                })
        
        return errors
    
    def validate_required_sections(self, message: str) -> List[Dict[str, Any]]:
        """Validate required sections based on commit type"""
        errors = []
        required = self.config.get('required_sections', {})
        
        # Check for breaking changes
        if 'BREAKING CHANGE' in message.upper() or '!' in message.split('\n')[0]:
            breaking_pattern = required.get('breaking_changes')
            if breaking_pattern and not re.search(breaking_pattern, message):
                errors.append({
                    'type': 'structure',
                    'message': 'Breaking changes must include BREAKING CHANGE: section',
                    'suggestion': 'Add "BREAKING CHANGE: description" to commit body',
                    'line': 0
                })
        
        return errors
    
    def validate_commit_message(self) -> bool:
        """Main validation logic"""
        print("💬 Validating commit message...")
        
        message = self.read_commit_message()
        if not message:
            print("❌ Empty commit message")
            return False
        
        # Run all validations
        all_errors = []
        all_errors.extend(self.validate_conventional_commits(message))
        all_errors.extend(self.validate_message_length(message))
        all_errors.extend(self.validate_ticket_reference(message))
        all_errors.extend(self.validate_forbidden_patterns(message))
        all_errors.extend(self.validate_required_sections(message))
        
        # Display results
        if not all_errors:
            print("✅ Commit message validation passed")
            return True
        
        print(f"❌ Found {len(all_errors)} commit message issues:")
        print()
        
        # Group errors by type
        error_groups = {}
        for error in all_errors:
            error_type = error['type']
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append(error)
        
        # Display grouped errors
        for error_type, errors in error_groups.items():
            print(f"🔍 {error_type.title()} Issues:")
            for error in errors:
                print(f"   • {error['message']}")
                if error.get('suggestion'):
                    print(f"     💡 {error['suggestion']}")
                if error.get('line') and error['line'] > 0:
                    print(f"     📍 Line {error['line']}")
            print()
        
        print("Current commit message:")
        print("-" * 40)
        for i, line in enumerate(message.split('\n'), 1):
            print(f"{i:2}: {line}")
        print("-" * 40)
        
        return False

def main():
    """Main commit message validation"""
    validator = CommitMessageValidator()
    success = validator.validate_commit_message()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
```

### Common Pain Points

1. **User Experience**: Blocking commits for message issues frustrates developers
2. **Ticket Integration**: Requires integration with ticketing systems
3. **Template Conflicts**: Can conflict with commit message templates
4. **Rebase Issues**: Messages change during interactive rebase
5. **Format Rigidity**: Overly strict rules can hamper productivity

---

## Hook 4: post-commit - Audit and Notifications

**Trigger**: After commit is created  
**Can Block**: ❌ No  
**Primary Purpose**: Logging, notifications, automated actions

### Implementation Example

```python
#!/usr/bin/env python3
"""
Post-Commit Hook - Audit Trail and Notifications
Logs commit information and triggers automated workflows
"""
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import requests
import smtplib
from email.mime.text import MIMEText

class PostCommitProcessor:
    def __init__(self):
        self.config = self.load_config()
        self.commit_info = self.get_commit_info()
    
    def load_config(self) -> Dict[str, Any]:
        """Load post-commit configuration"""
        config_file = Path('.governance/post-commit.json')
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        
        return {
            'audit_logging': True,
            'notifications': {
                'slack': {
                    'enabled': False,
                    'webhook_url': '',
                    'channel': '#commits'
                },
                'email': {
                    'enabled': False,
                    'smtp_server': 'smtp.gmail.com',
                    'recipients': []
                }
            },
            'triggers': {
                'ci_pipeline': True,
                'documentation_update': True,
                'metrics_collection': True
            },
            'filters': {
                'notify_branches': ['main', 'develop'],
                'significant_changes_threshold': 100  # lines
            }
        }
    
    def get_commit_info(self) -> Dict[str, Any]:
        """Extract commit information"""
        try:
            # Get commit details
            commit_sha = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                      capture_output=True, text=True).stdout.strip()
            
            commit_message = subprocess.run(['git', 'log', '-1', '--pretty=%B'], 
                                          capture_output=True, text=True).stdout.strip()
            
            author = subprocess.run(['git', 'log', '-1', '--pretty=%an <%ae>'], 
                                  capture_output=True, text=True).stdout.strip()
            
            timestamp = subprocess.run(['git', 'log', '-1', '--pretty=%ci'], 
                                     capture_output=True, text=True).stdout.strip()
            
            branch = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                                  capture_output=True, text=True).stdout.strip()
            
            # Get changed files
            changed_files = subprocess.run(['git', 'diff-tree', '--no-commit-id', 
                                          '--name-only', '-r', commit_sha], 
                                         capture_output=True, text=True).stdout.strip().split('\n')
            
            # Get diff stats
            diff_stats = subprocess.run(['git', 'diff-tree', '--no-commit-id', 
                                       '--numstat', '-r', commit_sha], 
                                      capture_output=True, text=True).stdout.strip()
            
            # Calculate total changes
            total_additions = 0
            total_deletions = 0
            
            for line in diff_stats.split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2 and parts[0] != '-' and parts[1] != '-':
                        total_additions += int(parts[0])
                        total_deletions += int(parts[1])
            
            return {
                'sha': commit_sha,
                'short_sha': commit_sha[:8],
                'message': commit_message,
                'author': author,
                'timestamp': timestamp,
                'branch': branch,
                'changed_files': [f for f in changed_files if f],
                'stats': {
                    'additions': total_additions,
                    'deletions': total_deletions,
                    'total_changes': total_additions + total_deletions
                }
            }
        
        except Exception as e:
            print(f"⚠️  Error getting commit info: {e}")
            return {}
    
    def log_audit_trail(self) -> None:
        """Log commit to audit trail"""
        if not self.config.get('audit_logging', True):
            return
        
        log_dir = Path('.governance/audit')
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create detailed audit entry
        audit_entry = {
            'event_type': 'commit_created',
            'timestamp': datetime.now().isoformat(),
            'commit': self.commit_info,
            'repository': self.get_repository_info(),
            'governance': {
                'hooks_executed': ['post-commit'],
                'compliance_status': 'logged'
            }
        }
        
        # Write to daily log file
        date_str = datetime.now().strftime('%Y-%m-%d')
        log_file = log_dir / f'commits-{date_str}.jsonl'
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(audit_entry) + '\n')
        
        # Update summary statistics
        self.update_commit_statistics()
        
        print(f"📝 Logged commit {self.commit_info.get('short_sha', 'unknown')} to audit trail")
    
    def get_repository_info(self) -> Dict[str, Any]:
        """Get repository context information"""
        try:
            remote_url = subprocess.run(['git', 'config', '--get', 'remote.origin.url'], 
                                      capture_output=True, text=True).stdout.strip()
            
            return {
                'remote_url': remote_url,
                'working_directory': str(Path.cwd()),
                'git_version': subprocess.run(['git', '--version'], 
                                            capture_output=True, text=True).stdout.strip()
            }
        except:
            return {}
    
    def update_commit_statistics(self) -> None:
        """Update running statistics"""
        stats_file = Path('.governance/stats/commit_stats.json')
        stats_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing stats
        if stats_file.exists():
            with open(stats_file) as f:
                stats = json.load(f)
        else:
            stats = {
                'total_commits': 0,
                'authors': {},
                'branches': {},
                'daily_commits': {},
                'file_changes': {}
            }
        
        # Update stats
        stats['total_commits'] += 1
        
        author = self.commit_info.get('author', 'Unknown')
        stats['authors'][author] = stats['authors'].get(author, 0) + 1
        
        branch = self.commit_info.get('branch', 'unknown')
        stats['branches'][branch] = stats['branches'].get(branch, 0) + 1
        
        today = datetime.now().strftime('%Y-%m-%d')
        stats['daily_commits'][today] = stats['daily_commits'].get(today, 0) + 1
        
        # Track file change patterns
        for file_path in self.commit_info.get('changed_files', []):
            extension = Path(file_path).suffix
            if extension:
                stats['file_changes'][extension] = stats['file_changes'].get(extension, 0) + 1
        
        # Save updated stats
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
    
    def send_notifications(self) -> None:
        """Send commit notifications based on configuration"""
        notifications_config = self.config.get('notifications', {})
        filters = self.config.get('filters', {})
        
        # Check if we should notify for this commit
        branch = self.commit_info.get('branch', '')
        notify_branches = filters.get('notify_branches', [])
        
        if notify_branches and branch not in notify_branches:
            print(f"ℹ️  Skipping notifications for branch '{branch}'")
            return
        
        # Check significance threshold
        total_changes = self.commit_info.get('stats', {}).get('total_changes', 0)
        threshold = filters.get('significant_changes_threshold', 100)
        
        is_significant = total_changes >= threshold
        
        # Send Slack notification
        slack_config = notifications_config.get('slack', {})
        if slack_config.get('enabled', False):
            self.send_slack_notification(slack_config, is_significant)
        
        # Send email notification
        email_config = notifications_config.get('email', {})
        if email_config.get('enabled', False):
            self.send_email_notification(email_config, is_significant)
    
    def send_slack_notification(self, config: Dict[str, Any], is_significant: bool) -> None:
        """Send notification to Slack"""
        webhook_url = config.get('webhook_url')
        if not webhook_url:
            return
        
        commit = self.commit_info
        stats = commit.get('stats', {})
        
        # Build message
        color = '#ff6b6b' if is_significant else '#4ecdc4'
        significance = " (Significant)" if is_significant else ""
        
        message = {
            "channel": config.get('channel', '#commits'),
            "attachments": [{
                "color": color,
                "title": f"New Commit{significance}",
                "title_link": f"https://github.com/repo/commit/{commit.get('sha', '')}",
                "fields": [
                    {"title": "Author", "value": commit.get('author', 'Unknown'), "short": True},
                    {"title": "Branch", "value": commit.get('branch', 'unknown'), "short": True},
                    {"title": "Files Changed", "value": str(len(commit.get('changed_files', []))), "short": True},
                    {"title": "Lines Changed", "value": f"+{stats.get('additions', 0)} -{stats.get('deletions', 0)}", "short": True}
                ],
                "text": commit.get('message', 'No message')[:200] + ('...' if len(commit.get('message', '')) > 200 else ''),
                "footer": f"Commit {commit.get('short_sha', 'unknown')}",
                "ts": datetime.now().timestamp()
            }]
        }
        
        try:
            response = requests.post(webhook_url, json=message, timeout=10)
            if response.status_code == 200:
                print("📱 Slack notification sent")
            else:
                print(f"⚠️  Slack notification failed: {response.status_code}")
        except Exception as e:
            print(f"⚠️  Slack notification error: {e}")
    
    def send_email_notification(self, config: Dict[str, Any], is_significant: bool) -> None:
        """Send email notification"""
        recipients = config.get('recipients', [])
        if not recipients:
            return
        
        commit = self.commit_info
        stats = commit.get('stats', {})
        
        subject = f"Commit: {commit.get('message', 'No message')[:50]}"
        if is_significant:
            subject = "[SIGNIFICANT] " + subject
        
        body = f"""
New commit in repository:

Commit: {commit.get('sha', 'unknown')}
Author: {commit.get('author', 'Unknown')}
Branch: {commit.get('branch', 'unknown')}
Date: {commit.get('timestamp', 'unknown')}

Message:
{commit.get('message', 'No message')}

Statistics:
- Files changed: {len(commit.get('changed_files', []))}
- Lines added: {stats.get('additions', 0)}
- Lines deleted: {stats.get('deletions', 0)}

Changed files:
{chr(10).join(commit.get('changed_files', []))}
"""
        
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = config.get('sender', 'git@localhost')
            msg['To'] = ', '.join(recipients)
            
            # This is a simplified example - you'd need proper SMTP configuration
            print(f"📧 Email notification prepared for {len(recipients)} recipients")
            
        except Exception as e:
            print(f"⚠️  Email notification error: {e}")
    
    def trigger_automated_workflows(self) -> None:
        """Trigger automated workflows based on commit"""
        triggers = self.config.get('triggers', {})
        
        # Trigger CI pipeline
        if triggers.get('ci_pipeline', True):
            self.trigger_ci_pipeline()
        
        # Update documentation if docs changed
        if triggers.get('documentation_update', True):
            self.check_documentation_updates()
        
        # Collect metrics
        if triggers.get('metrics_collection', True):
            self.collect_commit_metrics()
    
    def trigger_ci_pipeline(self) -> None:
        """Trigger CI/CD pipeline"""
        commit = self.commit_info
        branch = commit.get('branch', '')
        
        # Create trigger file for CI system to pick up
        trigger_file = Path('.governance/triggers/ci_trigger.json')
        trigger_file.parent.mkdir(parents=True, exist_ok=True)
        
        trigger_data = {
            'trigger_type': 'post_commit',
            'commit_sha': commit.get('sha'),
            'branch': branch,
            'timestamp': datetime.now().isoformat(),
            'changed_files': commit.get('changed_files', [])
        }
        
        with open(trigger_file, 'w') as f:
            json.dump(trigger_data, f, indent=2)
        
        print(f"🚀 CI pipeline trigger created for branch '{branch}'")
    
    def check_documentation_updates(self) -> None:
        """Check if documentation needs to be updated"""
        changed_files = self.commit_info.get('changed_files', [])
        
        # Check for code files that might need doc updates
        code_files = [f for f in changed_files if f.endswith(('.py', '.js', '.ts', '.java'))]
        doc_files = [f for f in changed_files if f.endswith(('.md', '.rst', '.txt'))]
        
        if code_files and not doc_files:
            print("📚 Consider updating documentation for code changes")
            
            # Create documentation reminder
            reminder_file = Path('.governance/reminders/doc_update.json')
            reminder_file.parent.mkdir(parents=True, exist_ok=True)
            
            reminder = {
                'type': 'documentation_update',
                'commit': self.commit_info.get('sha'),
                'files_needing_docs': code_files,
                'created': datetime.now().isoformat()
            }
            
            with open(reminder_file, 'w') as f:
                json.dump(reminder, f, indent=2)
    
    def collect_commit_metrics(self) -> None:
        """Collect detailed metrics about the commit"""
        metrics = {
            'commit_sha': self.commit_info.get('sha'),
            'timestamp': datetime.now().isoformat(),
            'complexity_metrics': self.analyze_code_complexity(),
            'security_metrics': self.analyze_security_changes(),
            'quality_metrics': self.analyze_quality_indicators()
        }
        
        # Save metrics
        metrics_dir = Path('.governance/metrics')
        metrics_dir.mkdir(parents=True, exist_ok=True)
        
        metrics_file = metrics_dir / f"commit_metrics_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with open(metrics_file, 'a') as f:
            f.write(json.dumps(metrics) + '\n')
        
        print("📊 Commit metrics collected")
    
    def analyze_code_complexity(self) -> Dict[str, Any]:
        """Analyze code complexity changes"""
        # Simplified complexity analysis
        changed_files = self.commit_info.get('changed_files', [])
        python_files = [f for f in changed_files if f.endswith('.py')]
        
        return {
            'files_analyzed': len(python_files),
            'estimated_complexity_change': len(python_files) * 0.1  # Placeholder
        }
    
    def analyze_security_changes(self) -> Dict[str, Any]:
        """Analyze security-related changes"""
        changed_files = self.commit_info.get('changed_files', [])
        
        security_files = [f for f in changed_files if any(sec in f.lower() 
                          for sec in ['auth', 'security', 'login', 'password'])]
        
        return {
            'security_files_changed': len(security_files),
            'requires_security_review': len(security_files) > 0
        }
    
    def analyze_quality_indicators(self) -> Dict[str, Any]:
        """Analyze code quality indicators"""
        commit_msg = self.commit_info.get('message', '').lower()
        
        quality_keywords = ['test', 'fix', 'refactor', 'improve', 'optimize']
        quality_score = sum(1 for keyword in quality_keywords if keyword in commit_msg)
        
        return {
            'quality_keywords_found': quality_score,
            'estimated_quality_impact': 'positive' if quality_score > 0 else 'neutral'
        }
    
    def process_commit(self) -> None:
        """Main post-commit processing"""
        print("🔄 Processing post-commit actions...")
        
        if not self.commit_info:
            print("⚠️  Could not get commit information")
            return
        
        # Execute all post-commit actions
        self.log_audit_trail()
        self.send_notifications()
        self.trigger_automated_workflows()
        
        print(f"✅ Post-commit processing complete for {self.commit_info.get('short_sha', 'unknown')}")

def main():
    """Main post-commit hook execution"""
    processor = PostCommitProcessor()
    processor.process_commit()
    return 0  # Post-commit hooks cannot fail

if __name__ == "__main__":
    sys.exit(main())
```

### Common Pain Points

1. **Performance Impact**: Can slow down commit operations
2. **Network Dependencies**: Notifications require internet access
3. **Error Handling**: Failures don't block commits but may go unnoticed
4. **Configuration Complexity**: Many notification channels to configure
5. **Noise**: Can generate too many notifications

---

## Hook 5: pre-receive (Server-Side) - Authorization Gateway

**Trigger**: Before push is accepted on server  
**Can Block**: ✅ Yes (critical for server protection)  
**Primary Purpose**: Authorization, policy enforcement, compliance

### Implementation Example

```python
#!/usr/bin/env python3
"""
Pre-Receive Hook (Server-Side)
Critical server-side governance and authorization
"""
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
import re
import requests
from datetime import datetime

class ServerSideGovernanceHook:
    def __init__(self):
        self.config = self.load_server_config()
        self.push_info = self.read_push_info()
        
    def load_server_config(self) -> Dict[str, Any]:
        """Load server-side governance configuration"""
        config_paths = [
            '/etc/git-governance/config.json',
            Path.home() / '.git-governance' / 'config.json',
            Path.cwd() / '.governance' / 'server.json'
        ]
        
        for config_path in config_paths:
            if Path(config_path).exists():
                with open(config_path) as f:
                    return json.load(f)
        
        # Default server configuration
        return {
            'authorization': {
                'required': True,
                'admin_users': ['admin', 'devops'],
                'branch_protection': {
                    'main': {
                        'required_reviewers': 2,
                        'admin_override': True,
                        'require_signed_commits': True
                    },
                    'release/*': {
                        'required_reviewers': 1,
                        'admin_override': True,
                        'block_force_push': True
                    }
                }
            },
            'compliance': {
                'scan_commits': True,
                'block_secrets': True,
                'require_signed_commits': False,
                'max_commit_size': 104857600,  # 100MB
                'prohibited_file_types': ['.exe', '.dll', '.so']
            },
            'integration': {
                'ldap_server': None,
                'approval_api': None,
                'audit_webhook': None
            }
        }
    
    def read_push_info(self) -> List[Dict[str, Any]]:
        """Read push information from stdin"""
        push_refs = []
        
        for line in sys.stdin:
            if line.strip():
                old_sha, new_sha, ref_name = line.strip().split()
                
                push_refs.append({
                    'old_sha': old_sha,
                    'new_sha': new_sha,
                    'ref_name': ref_name,
                    'branch': ref_name.split('/')[-1] if 'heads' in ref_name else ref_name,
                    'is_delete': new_sha == '0' * 40,
                    'is_create': old_sha == '0' * 40,
                    'is_force_push': self.is_force_push(old_sha, new_sha) if old_sha != '0' * 40 and new_sha != '0' * 40 else False
                })
        
        return push_refs
    
    def is_force_push(self, old_sha: str, new_sha: str) -> bool:
        """Detect if this is a force push"""
        try:
            # Check if old_sha is an ancestor of new_sha
            result = subprocess.run([
                'git', 'merge-base', '--is-ancestor', old_sha, new_sha
            ], capture_output=True, timeout=10)
            
            # If merge-base succeeds, it's not a force push
            return result.returncode != 0
        except:
            return False
    
    def get_pusher_info(self) -> Dict[str, Any]:
        """Get information about who is pushing"""
        return {
            'username': os.environ.get('REMOTE_USER', os.environ.get('USER', 'unknown')),
            'ip_address': os.environ.get('SSH_CLIENT', 'unknown').split()[0] if os.environ.get('SSH_CLIENT') else 'local',
            'timestamp': datetime.now().isoformat()
        }
    
    def validate_authorization(self) -> Dict[str, Any]:
        """Validate user authorization for push"""
        auth_config = self.config.get('authorization', {})
        
        if not auth_config.get('required', True):
            return {'authorized': True, 'reason': 'Authorization disabled'}
        
        pusher = self.get_pusher_info()
        username = pusher['username']
        
        # Check admin users
        admin_users = auth_config.get('admin_users', [])
        is_admin = username in admin_users
        
        # Check branch-specific permissions
        branch_protection = auth_config.get('branch_protection', {})
        
        authorization_results = []
        
        for push_ref in self.push_info:
            branch = push_ref['branch']
            
            # Find matching protection rule
            protection_rule = None
            if branch in branch_protection:
                protection_rule = branch_protection[branch]
            else:
                # Check wildcard patterns
                for pattern, rule in branch_protection.items():
                    if '*' in pattern and pattern.replace('*', '') in branch:
                        protection_rule = rule
                        break
            
            if protection_rule:
                result = self.validate_branch_protection(push_ref, protection_rule, is_admin)
                authorization_results.append(result)
                
                if not result['authorized']:
                    return {
                        'authorized': False,
                        'reason': result['reason'],
                        'branch': branch
                    }
        
        return {
            'authorized': True,
            'reason': f'User {username} authorized for all operations',
            'is_admin': is_admin,
            'results': authorization_results
        }
    
    def validate_branch_protection(self, push_ref: Dict[str, Any], 
                                 protection_rule: Dict[str, Any], 
                                 is_admin: bool) -> Dict[str, Any]:
        """Validate specific branch protection rules"""
        branch = push_ref['branch']
        
        # Check force push protection
        if push_ref['is_force_push'] and protection_rule.get('block_force_push', False):
            if not (is_admin and protection_rule.get('admin_override', False)):
                return {
                    'authorized': False,
                    'reason': f'Force push blocked on protected branch {branch}'
                }
        
        # Check required reviewers (simplified - would integrate with PR system)
        required_reviewers = protection_rule.get('required_reviewers', 0)
        if required_reviewers > 0:
            # In a real implementation, this would check PR approval status
            approval_status = self.check_approval_status(push_ref)
            if not approval_status['approved'] and not (is_admin and protection_rule.get('admin_override', False)):
                return {
                    'authorized': False,
                    'reason': f'Branch {branch} requires {required_reviewers} reviewers'
                }
        
        # Check signed commits
        if protection_rule.get('require_signed_commits', False):
            if not self.verify_signed_commits(push_ref):
                return {
                    'authorized': False,
                    'reason': f'Branch {branch} requires signed commits'
                }
        
        return {'authorized': True, 'reason': f'Branch {branch} protection satisfied'}
    
    def check_approval_status(self, push_ref: Dict[str, Any]) -> Dict[str, Any]:
        """Check if commits have required approvals"""
        # This would integrate with your PR/approval system
        # For now, return a placeholder
        return {
            'approved': True,  # Simplified
            'reviewers': [],
            'approval_method': 'commit_message'  # Could check commit messages for approval markers
        }
    
    def verify_signed_commits(self, push_ref: Dict[str, Any]) -> bool:
        """Verify that commits are cryptographically signed"""
        try:
            # Get commits in the push
            if push_ref['is_create']:
                # New branch, check all commits
                commit_range = push_ref['new_sha']
            else:
                # Existing branch, check new commits
                commit_range = f"{push_ref['old_sha']}..{push_ref['new_sha']}"
            
            result = subprocess.run([
                'git', 'rev-list', '--show-signature', commit_range
            ], capture_output=True, text=True, timeout=30)
            
            # Check if all commits have valid signatures
            # This is a simplified check - real implementation would be more thorough
            return 'gpg: Good signature' in result.stderr or result.returncode == 0
        
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False
    
    def validate_compliance(self) -> Dict[str, Any]:
        """Validate compliance requirements"""
        compliance_config = self.config.get('compliance', {})
        compliance_results = []
        
        for push_ref in self.push_info:
            if push_ref['is_delete']:
                continue
                
            # Get commits in push
            commits = self.get_push_commits(push_ref)
            
            for commit in commits:
                # Check commit size
                if compliance_config.get('max_commit_size'):
                    size_check = self.check_commit_size(commit, compliance_config['max_commit_size'])
                    if not size_check['compliant']:
                        return {
                            'compliant': False,
                            'violation': 'commit_size',
                            'details': size_check
                        }
                
                # Scan for secrets
                if compliance_config.get('block_secrets', True):
                    secret_check = self.scan_commit_for_secrets(commit)
                    if not secret_check['compliant']:
                        return {
                            'compliant': False,
                            'violation': 'secrets_detected',
                            'details': secret_check
                        }
                
                # Check prohibited file types
                prohibited_types = compliance_config.get('prohibited_file_types', [])
                if prohibited_types:
                    file_check = self.check_prohibited_files(commit, prohibited_types)
                    if not file_check['compliant']:
                        return {
                            'compliant': False,
                            'violation': 'prohibited_files',
                            'details': file_check
                        }
        
        return {
            'compliant': True,
            'message': 'All compliance checks passed',
            'checks_performed': len(compliance_results)
        }
    
    def get_push_commits(self, push_ref: Dict[str, Any]) -> List[str]:
        """Get list of commit SHAs in the push"""
        try:
            if push_ref['is_create']:
                # New branch - get all commits
                result = subprocess.run([
                    'git', 'rev-list', push_ref['new_sha']
                ], capture_output=True, text=True, timeout=30)
            else:
                # Existing branch - get new commits only
                result = subprocess.run([
                    'git', 'rev-list', f"{push_ref['old_sha']}..{push_ref['new_sha']}"
                ], capture_output=True, text=True, timeout=30)
            
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        except:
            return []
    
    def check_commit_size(self, commit_sha: str, max_size: int) -> Dict[str, Any]:
        """Check if commit size exceeds limit"""
        try:
            # Get commit size
            result = subprocess.run([
                'git', 'cat-file', '-s', commit_sha
            ], capture_output=True, text=True, timeout=10)
            
            commit_size = int(result.stdout.strip())
            
            return {
                'compliant': commit_size <= max_size,
                'commit': commit_sha,
                'size': commit_size,
                'limit': max_size,
                'message': f'Commit size: {commit_size} bytes (limit: {max_size})'
            }
        except:
            return {
                'compliant': True,
                'message': 'Could not determine commit size'
            }
    
    def scan_commit_for_secrets(self, commit_sha: str) -> Dict[str, Any]:
        """Scan commit for potential secrets"""
        try:
            # Get commit diff
            result = subprocess.run([
                'git', 'show', '--format=', commit_sha
            ], capture_output=True, text=True, timeout=30)
            
            diff_content = result.stdout
            
            # Secret patterns (simplified - use dedicated tools in production)
            secret_patterns = [
                r'(?i)(api_key|apikey|api-key)\s*[=:]\s*["\']?([a-z0-9]{20,})["\']?',
                r'(?i)sk-[a-z0-9]{48}',  # OpenAI keys
                r'(?i)AKIA[0-9A-Z]{16}',  # AWS access keys
                r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']?([^"\'\s]{8,})["\']?'
            ]
            
            violations = []
            for pattern in secret_patterns:
                matches = re.finditer(pattern, diff_content)
                for match in matches:
                    # Skip test/example patterns
                    if not any(skip in match.group().lower() for skip in 
                              ['test', 'example', 'sample', 'demo', 'fake']):
                        violations.append({
                            'pattern': pattern,
                            'match': match.group()[:50] + '...',  # Truncate for security
                            'line': diff_content[:match.start()].count('\n') + 1
                        })
            
            return {
                'compliant': len(violations) == 0,
                'commit': commit_sha,
                'violations': violations,
                'message': f'Found {len(violations)} potential secrets' if violations else 'No secrets detected'
            }
        
        except:
            return {
                'compliant': True,
                'message': 'Could not scan commit for secrets'
            }
    
    def check_prohibited_files(self, commit_sha: str, prohibited_types: List[str]) -> Dict[str, Any]:
        """Check for prohibited file types in commit"""
        try:
            # Get files changed in commit
            result = subprocess.run([
                'git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_sha
            ], capture_output=True, text=True, timeout=10)
            
            changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            prohibited_files = []
            for file_path in changed_files:
                for prohibited_type in prohibited_types:
                    if file_path.endswith(prohibited_type):
                        prohibited_files.append(file_path)
            
            return {
                'compliant': len(prohibited_files) == 0,
                'commit': commit_sha,
                'prohibited_files': prohibited_files,
                'message': f'Found {len(prohibited_files)} prohibited files' if prohibited_files else 'No prohibited files'
            }
        
        except:
            return {
                'compliant': True,
                'message': 'Could not check file types'
            }
    
    def log_server_audit(self, decision: str, details: Dict[str, Any]) -> None:
        """Log server-side governance decision"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'hook': 'pre-receive',
            'decision': decision,
            'pusher': self.get_pusher_info(),
            'push_info': self.push_info,
            'details': details
        }
        
        # Log to system location
        log_dir = Path('/var/log/git-governance')
        if not log_dir.exists() or not os.access(log_dir, os.W_OK):
            log_dir = Path.home() / '.git-governance' / 'logs'
        
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"server-governance-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(audit_entry) + '\n')
        
        # Send to audit webhook if configured
        webhook_url = self.config.get('integration', {}).get('audit_webhook')
        if webhook_url:
            try:
                requests.post(webhook_url, json=audit_entry, timeout=5)
            except:
                pass  # Don't fail hook if webhook fails
    
    def validate_push(self) -> bool:
        """Main server-side validation logic"""
        print("🛡️  Server-side governance validation")
        print("=" * 50)
        
        pusher = self.get_pusher_info()
        print(f"👤 User: {pusher['username']} from {pusher['ip_address']}")
        print(f"📥 Push operations: {len(self.push_info)}")
        
        for push_ref in self.push_info:
            operation = "delete" if push_ref['is_delete'] else "create" if push_ref['is_create'] else "update"
            print(f"   {operation}: {push_ref['ref_name']}")
        
        # Run authorization checks
        print("\n🔐 Checking authorization...")
        auth_result = self.validate_authorization()
        
        if not auth_result['authorized']:
            print(f"❌ AUTHORIZATION DENIED: {auth_result['reason']}")
            self.log_server_audit('denied', auth_result)
            return False
        else:
            print(f"✅ Authorization: {auth_result['reason']}")
        
        # Run compliance checks
        print("\n📋 Checking compliance...")
        compliance_result = self.validate_compliance()
        
        if not compliance_result['compliant']:
            print(f"❌ COMPLIANCE VIOLATION: {compliance_result['violation']}")
            print(f"   Details: {compliance_result['details']['message']}")
            self.log_server_audit('compliance_violation', compliance_result)
            return False
        else:
            print(f"✅ Compliance: {compliance_result['message']}")
        
        print("\n✅ ALL VALIDATIONS PASSED - Push accepted")
        self.log_server_audit('accepted', {
            'authorization': auth_result,
            'compliance': compliance_result
        })
        
        return True

def main():
    """Main server-side hook execution"""
    try:
        hook = ServerSideGovernanceHook()
        success = hook.validate_push()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Server-side governance error: {e}")
        # In server-side hooks, it's often better to fail safe
        return 1

if __name__ == "__main__":
    import os
    sys.exit(main())
```

### Common Pain Points

1. **Server Environment**: Runs in restricted server environment
2. **Performance Critical**: Any slowdown affects all pushes
3. **Error Recovery**: Failures can break repository access
4. **Configuration Management**: Server config is harder to update
5. **Integration Complexity**: Must integrate with auth systems, LDAP, etc.

---

## Hook Management and Installation

### Universal Hook Manager

```python
#!/usr/bin/env python3
"""
Universal Git Hook Manager
Installs, configures, and manages all governance hooks
"""
import os
import sys
import json
import shutil
import stat
from pathlib import Path
from typing import Dict, Any, List

class GitHookManager:
    def __init__(self):
        self.repo_root = self.find_git_root()
        self.hooks_dir = self.repo_root / '.git' / 'hooks'
        self.governance_dir = self.repo_root / '.governance'
        
    def find_git_root(self) -> Path:
        """Find the git repository root"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.git').exists():
                return current
            current = current.parent
        
        raise RuntimeError("Not in a git repository")
    
    def install_all_hooks(self) -> bool:
        """Install all governance hooks"""
        hooks_to_install = {
            'pre-commit': self.create_pre_commit_hook,
            'commit-msg': self.create_commit_msg_hook,
            'pre-push': self.create_pre_push_hook,
            'post-commit': self.create_post_commit_hook
        }
        
        print("🔧 Installing Git Governance Hooks")
        print("=" * 40)
        
        success_count = 0
        for hook_name, installer in hooks_to_install.items():
            try:
                if installer():
                    print(f"✅ {hook_name}: Installed")
                    success_count += 1
                else:
                    print(f"❌ {hook_name}: Failed")
            except Exception as e:
                print(f"❌ {hook_name}: Error - {e}")
        
        print(f"\n📊 Installed {success_count}/{len(hooks_to_install)} hooks")
        
        # Create default configurations
        self.create_default_configs()
        
        return success_count == len(hooks_to_install)
    
    def create_hook_script(self, hook_name: str, python_script: str) -> bool:
        """Create a hook script that calls Python implementation"""
        hook_path = self.hooks_dir / hook_name
        
        # Create hook content
        hook_content = f"""#!/usr/bin/env python3
# Git {hook_name} hook - Governance System
# Auto-generated by GitHookManager

import sys
import os
from pathlib import Path

# Add governance directory to Python path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / '.governance' / 'hooks'))

try:
    from {python_script} import main
    sys.exit(main())
except ImportError as e:
    print(f"❌ Governance hook error: {{e}}")
    print(f"💡 Run: python -m pip install -r .governance/requirements.txt")
    sys.exit(0)  # Don't block operations if governance system isn't set up
except Exception as e:
    print(f"❌ Hook execution error: {{e}}")
    sys.exit(0)
"""
        
        try:
            with open(hook_path, 'w') as f:
                f.write(hook_content)
            
            # Make executable
            hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
            
            return True
        except Exception:
            return False
    
    def create_python_hook_file(self, filename: str, content: str) -> bool:
        """Create the Python hook implementation file"""
        hooks_impl_dir = self.governance_dir / 'hooks'
        hooks_impl_dir.mkdir(parents=True, exist_ok=True)
        
        hook_file = hooks_impl_dir / f"{filename}.py"
        
        try:
            with open(hook_file, 'w') as f:
                f.write(content)
            return True
        except Exception:
            return False

    def create_pre_commit_hook(self) -> bool:
        """Install pre-commit hook"""
        # This would contain the full pre-commit implementation
        # For brevity, using a reference to the main implementation
        return (
            self.create_hook_script('pre-commit', 'pre_commit_governance') and
            self.create_python_hook_file('pre_commit_governance', """
# Pre-commit governance implementation would go here
# (Reference to the full implementation above)
def main():
    print("🔍 Pre-commit governance check...")
    return 0
""")
        )
    
    # Similar methods for other hooks...
    
    def create_default_configs(self) -> None:
        """Create default configuration files"""
        configs = {
            'pre-commit.json': {
                'security': {'scan_secrets': True},
                'quality': {'min_coverage': 80},
                'format': {'auto_fix': True}
            },
            'commit-msg.json': {
                'conventional_commits': True,
                'require_ticket_reference': True
            },
            'pre-push.json': {
                'run_integration_tests': True,
                'security_scan': True
            },
            'server.json': {
                'authorization': {'required': True},
                'compliance': {'block_secrets': True}
            }
        }
        
        for config_name, config_data in configs.items():
            config_file = self.governance_dir / config_name
            if not config_file.exists():
                with open(config_file, 'w') as f:
                    json.dump(config_data, f, indent=2)
    
    def uninstall_hooks(self) -> bool:
        """Remove all governance hooks"""
        hook_names = ['pre-commit', 'commit-msg', 'pre-push', 'post-commit', 'pre-receive']
        
        removed_count = 0
        for hook_name in hook_names:
            hook_path = self.hooks_dir / hook_name
            if hook_path.exists():
                try:
                    hook_path.unlink()
                    removed_count += 1
                    print(f"🗑️  Removed {hook_name}")
                except Exception as e:
                    print(f"❌ Failed to remove {hook_name}: {e}")
        
        print(f"📊 Removed {removed_count} hooks")
        return removed_count > 0

def main():
    """Main hook manager CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Git Hook Manager for Governance')
    parser.add_argument('action', choices=['install', 'uninstall', 'status'], 
                       help='Action to perform')
    
    args = parser.parse_args()
    
    manager = GitHookManager()
    
    if args.action == 'install':
        success = manager.install_all_hooks()
        sys.exit(0 if success else 1)
    elif args.action == 'uninstall':
        manager.uninstall_hooks()
    elif args.action == 'status':
        # Show status of installed hooks
        pass

if __name__ == "__main__":
    main()
```

## Summary and Integration Strategy

### Recommended Implementation Order

1. **Start with pre-commit**: Highest impact, catches issues early
2. **Add commit-msg**: Ensures consistent commit standards  
3. **Implement pre-push**: Comprehensive testing before sharing
4. **Add post-commit**: Audit trail and notifications
5. **Deploy pre-receive**: Server-side protection (if you control the server)

### Integration with Your Governance System

```python
# Bridge git hooks with your custom governance system
from governance.core.runtime_governance import RuntimeGovernanceSystem

class GitGovernanceBridge:
    def __init__(self):
        self.governance = RuntimeGovernanceSystem()
    
    async def validate_git_operation(self, operation_type: str, context: Dict[str, Any]) -> bool:
        """Bridge git hooks to custom governance"""
        governance_context = self.create_governance_context(operation_type, context)
        result = await self.governance.evaluate_decision(governance_context)
        return result.decision == "approved"
```

This comprehensive git hooks implementation provides multiple layers of governance that work together with your Claude Code hooks and custom governance system for complete development workflow control.