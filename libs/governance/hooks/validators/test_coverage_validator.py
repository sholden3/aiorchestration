"""
Test Coverage Validator

Handles validation of test coverage requirements.
Ensures all source code has corresponding test files.
"""

import subprocess
from pathlib import Path
from typing import List, Dict
from datetime import datetime

try:
    from .base import ValidatorInterface, ValidationResult
except ImportError:
    from base import ValidatorInterface, ValidationResult


class TestCoverageValidator(ValidatorInterface):
    """Validates test coverage requirements"""
    
    def __init__(self, repo_root: Path, config: dict, changed_files: List[str], exemption_manager=None):
        super().__init__(repo_root, config, changed_files, exemption_manager)
        self.validator_name = "Test Coverage"
    
    def validate(self) -> ValidationResult:
        """Check if code has tests and optionally run them"""
        start_time = self.log_validation_start()
        result = self.create_result()
        
        # Get source files that need tests
        source_files = [
            f for f in self.changed_files 
            if self.is_source_file(f) 
            and not self.is_test_file(f)
            and not self.should_skip_file(f)
        ]
        
        if not source_files:
            result.add_suggestion("No source files to check for tests")
            self.log_validation_end(result, start_time)
            return result
        
        # Check for test files
        files_without_tests = []
        for file_path in source_files:
            result.files_checked.append(file_path)
            
            # Check if exempt
            if self.is_exempt(file_path, 'test_coverage'):
                result.add_suggestion(f"File '{file_path}' is exempt from test requirements")
                continue
            
            # Look for corresponding test file
            test_exists = self._find_test_file(file_path)
            if not test_exists:
                files_without_tests.append(file_path)
                result.add_violation(
                    level="HIGH",
                    message=f"No test file for '{file_path}'",
                    penalty=self.penalty_weights['HIGH'],
                    file_path=file_path
                )
        
        # Optionally run tests
        testing_config = self.config.get('testing', {})
        if testing_config.get('execution_required', False):
            self._run_tests(result, source_files)
        
        # Set metadata
        result.metadata = {
            'source_files_checked': len(source_files),
            'files_without_tests': len(files_without_tests),
            'test_execution_required': testing_config.get('execution_required', False)
        }
        
        if not files_without_tests:
            result.add_suggestion("Consider running tests to verify they pass")
        
        self.log_validation_end(result, start_time)
        return result
    
    def _find_test_file(self, file_path: str) -> bool:
        """Find if test file exists for given source file - fully config-driven"""
        try:
            # Get all tracked AND staged files
            tracked_files = self._get_tracked_files()
            staged_files = self._get_staged_files()
            
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
            
        except Exception as e:
            print(f"[WARN] Error finding test file for '{file_path}': {e}")
            return True  # Don't block on errors
    
    def _get_tracked_files(self) -> List[str]:
        """Get all tracked files"""
        try:
            result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, cwd=self.repo_root)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
        except Exception:
            pass
        return []
    
    def _get_staged_files(self) -> List[str]:
        """Get all staged files"""
        try:
            result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                  capture_output=True, text=True, cwd=self.repo_root)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
        except Exception:
            pass
        return []
    
    def _run_tests(self, result: ValidationResult, source_files: List[str]):
        """Run tests and check coverage"""
        testing_config = self.config.get('testing', {})
        
        # Check for Python tests
        python_files = [f for f in source_files if f.endswith('.py')]
        if python_files:
            self._run_python_tests(result, testing_config)
        
        # Check for JavaScript/TypeScript tests
        js_files = [f for f in source_files if f.endswith(('.ts', '.tsx', '.js', '.jsx'))]
        if js_files:
            self._run_js_tests(result, testing_config)
    
    def _run_python_tests(self, result: ValidationResult, testing_config: Dict):
        """Run Python tests with coverage"""
        min_coverage = testing_config.get('minimum_coverage', {}).get('python', 85)
        
        try:
            cmd = [
                'python', '-m', 'pytest', 
                '--cov=.', 
                '--cov-report=term-missing', 
                f'--cov-fail-under={min_coverage}'
            ]
            
            test_result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.repo_root, timeout=300
            )
            
            if test_result.returncode != 0:
                # Check if it's test failure or coverage failure
                if 'FAILED' in test_result.stdout:
                    result.add_violation(
                        level="CRITICAL",
                        message="Python tests failed - fix before committing",
                        penalty=self.penalty_weights['CRITICAL']
                    )
                elif 'coverage' in test_result.stdout.lower():
                    result.add_violation(
                        level="HIGH",
                        message=f"Python coverage below {min_coverage}%",
                        penalty=self.penalty_weights['HIGH']
                    )
                
                # Store test output in metadata
                result.metadata['python_test_output'] = test_result.stdout[-1000:]
            else:
                result.add_suggestion("Python tests passing with sufficient coverage")
                
        except subprocess.TimeoutExpired:
            result.add_violation(
                level="HIGH",
                message="Python tests timed out (>5 minutes)",
                penalty=self.penalty_weights['HIGH']
            )
        except Exception as e:
            result.add_warning(f"Could not run Python tests: {e}")
    
    def _run_js_tests(self, result: ValidationResult, testing_config: Dict):
        """Run JavaScript/TypeScript tests with coverage"""
        package_json = self.repo_root / 'package.json'
        if not package_json.exists():
            result.add_warning("No package.json found for JavaScript/TypeScript tests")
            return
        
        try:
            cmd = ['npm', 'test', '--', '--coverage', '--passWithNoTests']
            
            test_result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.repo_root, timeout=300
            )
            
            if test_result.returncode != 0:
                result.add_violation(
                    level="CRITICAL",
                    message="JavaScript/TypeScript tests failed",
                    penalty=self.penalty_weights['CRITICAL']
                )
                
                # Store test output in metadata
                result.metadata['js_test_output'] = test_result.stdout[-1000:]
            else:
                result.add_suggestion("JavaScript/TypeScript tests passing")
                
        except subprocess.TimeoutExpired:
            result.add_violation(
                level="HIGH",
                message="JavaScript/TypeScript tests timed out (>5 minutes)",
                penalty=self.penalty_weights['HIGH']
            )
        except Exception as e:
            result.add_warning(f"Could not run JavaScript/TypeScript tests: {e}")
