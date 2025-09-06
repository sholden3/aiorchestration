"""
Code Quality Validator

Handles validation of code quality standards.
Checks for debug code, TODOs, security issues, and other quality problems.
"""

import re
from pathlib import Path
from typing import List, Dict
from datetime import datetime

try:
    from .base import ValidatorInterface, ValidationResult
except ImportError:
    from base import ValidatorInterface, ValidationResult


class CodeQualityValidator(ValidatorInterface):
    """Validates code quality standards"""
    
    def __init__(self, repo_root: Path, config: dict, changed_files: List[str], exemption_manager=None):
        super().__init__(repo_root, config, changed_files, exemption_manager)
        self.validator_name = "Code Quality"
    
    def validate(self) -> ValidationResult:
        """Check for debug code, TODOs, and other quality issues"""
        start_time = self.log_validation_start()
        result = self.create_result()
        
        # Get source files to check
        source_files = [
            f for f in self.changed_files 
            if self.is_source_file(f)
            and not self.should_skip_file(f)
        ]
        
        if not source_files:
            result.add_suggestion("No source files to check for quality issues")
            self.log_validation_end(result, start_time)
            return result
        
        patterns = self.config.get('security', {}).get('code_quality_patterns', [])
        if not patterns:
            patterns = self._get_default_patterns()
        
        quality_issues = []
        
        for file_path in source_files:
            result.files_checked.append(file_path)
            full_path = self.repo_root / file_path
            
            if not full_path.exists():
                continue
            
            try:
                content = full_path.read_text(errors='ignore')
            except Exception as e:
                result.add_warning(f"Could not read file '{file_path}': {e}")
                continue
            
            for pattern_config in patterns:
                pattern = pattern_config['pattern']
                message = pattern_config['message']
                severity = pattern_config.get('severity', 'medium')
                
                # Map pattern to rule ID for exemption checking
                rule_id = self._pattern_to_rule_id(pattern)
                
                # Check if file is exempt from this rule
                if self.is_exempt(file_path, rule_id):
                    continue  # Skip this check for exempt file
                
                if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    quality_issues.append({
                        'file': file_path,
                        'issue': message,
                        'severity': severity,
                        'pattern': pattern
                    })
                    
                    penalty = {
                        'critical': self.penalty_weights['CRITICAL'],
                        'high': self.penalty_weights['HIGH'],
                        'medium': self.penalty_weights['MEDIUM'],
                        'low': self.penalty_weights['LOW']
                    }.get(severity.lower(), self.penalty_weights['MEDIUM'])
                    
                    result.add_violation(
                        level=severity.upper(),
                        message=f"{file_path}: {message}",
                        penalty=penalty,
                        file_path=file_path
                    )
        
        # Additional quality checks
        self._check_complexity(result, source_files)
        self._check_security_patterns(result, source_files)
        self._check_performance_issues(result, source_files)
        
        # Set metadata
        result.metadata = {
            'files_checked': len(source_files),
            'quality_issues': len(quality_issues),
            'patterns_checked': len(patterns),
            'issue_types': list(set([issue['severity'] for issue in quality_issues]))
        }
        
        if not quality_issues:
            result.add_suggestion("Code quality standards met")
        
        self.log_validation_end(result, start_time)
        return result
    
    def _get_default_patterns(self) -> List[Dict]:
        """Get default code quality patterns if none configured"""
        return [
            {
                'pattern': r'console\.log\(',
                'message': 'Debug console.log statement found',
                'severity': 'medium'
            },
            {
                'pattern': r'print\(.*#.*DEBUG',
                'message': 'Debug print statement found',
                'severity': 'medium'
            },
            {
                'pattern': r'debugger;',
                'message': 'JavaScript debugger statement found',
                'severity': 'high'
            },
            {
                'pattern': r'TODO:|FIXME:|HACK:|XXX:',
                'message': 'TODO/FIXME comment found',
                'severity': 'low'
            },
            {
                'pattern': r'import pdb',
                'message': 'Python debugger import found',
                'severity': 'high'
            },
            {
                'pattern': r'pdb\.set_trace',
                'message': 'Python debugger breakpoint found',
                'severity': 'high'
            },
            {
                'pattern': r'eval\s*\(',
                'message': 'Dangerous eval() function usage',
                'severity': 'critical'
            },
            {
                'pattern': r'innerHTML\s*=',
                'message': 'Potential XSS vulnerability with innerHTML',
                'severity': 'high'
            }
        ]
    
    def _pattern_to_rule_id(self, pattern: str) -> str:
        """Map regex pattern to rule ID for exemptions"""
        pattern_map = {
            r"console\.log\(": "console_log_check",
            r"print\(.*#.*DEBUG": "debug_code_check",
            r"debugger;": "debug_code_check",
            r"TODO:|FIXME:|HACK:|XXX:": "todo_check",
            r"import pdb": "debug_code_check",
            r"pdb\.set_trace": "debug_code_check",
            r"eval\s*\(": "eval_usage_check",
            r"innerHTML\s*=": "xss_vulnerability_check"
        }
        
        for regex, rule_id in pattern_map.items():
            if regex in pattern:
                return rule_id
        
        # Default rule ID based on pattern
        return pattern.replace('\\', '').replace('.', '_').replace('(', '').replace(')', '').lower()
    
    def _check_complexity(self, result: ValidationResult, source_files: List[str]):
        """Check for overly complex code patterns"""
        complexity_patterns = [
            {
                'pattern': r'if\s+.*if\s+.*if\s+.*if\s+',
                'message': 'Deeply nested if statements (consider refactoring)',
                'severity': 'medium'
            },
            {
                'pattern': r'for\s+.*for\s+.*for\s+.*for\s+',
                'message': 'Deeply nested loops (consider refactoring)',
                'severity': 'medium'
            }
        ]
        
        for file_path in source_files:
            full_path = self.repo_root / file_path
            if not full_path.exists():
                continue
            
            try:
                content = full_path.read_text(errors='ignore')
                lines = content.split('\n')
                
                # Check line length
                max_line_length = self.config.get('code_quality', {}).get('max_line_length', 120)
                for i, line in enumerate(lines, 1):
                    if len(line) > max_line_length:
                        result.add_violation(
                            level="LOW",
                            message=f"{file_path}:{i} Line too long ({len(line)} > {max_line_length})",
                            penalty=self.penalty_weights['LOW'] * 0.5,  # Reduced penalty
                            file_path=file_path
                        )
                
                # Check complexity patterns
                for pattern_config in complexity_patterns:
                    if re.search(pattern_config['pattern'], content, re.MULTILINE):
                        if not self.is_exempt(file_path, 'complexity_check'):
                            result.add_violation(
                                level=pattern_config['severity'].upper(),
                                message=f"{file_path}: {pattern_config['message']}",
                                penalty=self.penalty_weights[pattern_config['severity'].upper()],
                                file_path=file_path
                            )
                
            except Exception as e:
                result.add_warning(f"Could not check complexity for '{file_path}': {e}")
    
    def _check_security_patterns(self, result: ValidationResult, source_files: List[str]):
        """Check for common security anti-patterns"""
        security_patterns = [
            {
                'pattern': r'password\s*=\s*[\'"][^\'"]+[\'"]',
                'message': 'Hardcoded password detected',
                'severity': 'critical'
            },
            {
                'pattern': r'api_key\s*=\s*[\'"][^\'"]+[\'"]',
                'message': 'Hardcoded API key detected',
                'severity': 'critical'
            },
            {
                'pattern': r'secret\s*=\s*[\'"][^\'"]+[\'"]',
                'message': 'Hardcoded secret detected',
                'severity': 'critical'
            },
            {
                'pattern': r'token\s*=\s*[\'"][^\'"]{20,}[\'"]',
                'message': 'Hardcoded token detected',
                'severity': 'high'
            }
        ]
        
        for file_path in source_files:
            full_path = self.repo_root / file_path
            if not full_path.exists():
                continue
            
            try:
                content = full_path.read_text(errors='ignore')
                
                for pattern_config in security_patterns:
                    rule_id = f"security_{pattern_config['message'].lower().replace(' ', '_')}"
                    if self.is_exempt(file_path, rule_id):
                        continue
                    
                    if re.search(pattern_config['pattern'], content, re.IGNORECASE):
                        result.add_violation(
                            level=pattern_config['severity'].upper(),
                            message=f"{file_path}: {pattern_config['message']}",
                            penalty=self.penalty_weights[pattern_config['severity'].upper()],
                            file_path=file_path
                        )
                        
            except Exception as e:
                result.add_warning(f"Could not check security patterns for '{file_path}': {e}")
    
    def _check_performance_issues(self, result: ValidationResult, source_files: List[str]):
        """Check for common performance anti-patterns"""
        performance_patterns = [
            {
                'pattern': r'\.find\(\)\s*\.find\(\)',
                'message': 'Multiple consecutive find() calls (inefficient)',
                'severity': 'low'
            },
            {
                'pattern': r'for\s+.*\s+in\s+.*\.keys\(\):',
                'message': 'Iterating over dict.keys() instead of dict (Python)',
                'severity': 'low'
            }
        ]
        
        for file_path in source_files:
            full_path = self.repo_root / file_path
            if not full_path.exists():
                continue
            
            try:
                content = full_path.read_text(errors='ignore')
                
                for pattern_config in performance_patterns:
                    rule_id = f"performance_{pattern_config['message'][:20].lower().replace(' ', '_')}"
                    if self.is_exempt(file_path, rule_id):
                        continue
                    
                    if re.search(pattern_config['pattern'], content):
                        result.add_violation(
                            level=pattern_config['severity'].upper(),
                            message=f"{file_path}: {pattern_config['message']}",
                            penalty=self.penalty_weights[pattern_config['severity'].upper()],
                            file_path=file_path
                        )
                        
            except Exception as e:
                result.add_warning(f"Could not check performance patterns for '{file_path}': {e}")
