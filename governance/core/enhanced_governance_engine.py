#!/usr/bin/env python3
"""
@fileoverview Enhanced Governance Engine v2.0 - Comprehensive code quality enforcement
@author Sam Martinez v1.0 - 2025-08-29
@architecture Governance - Core engine for enhanced validation rules
@responsibility Enforce code quality, detect anti-patterns, track test execution
@dependencies re, ast, pathlib, sqlite3, datetime, yaml
@integration_points Git hooks, CI/CD, test runners, domain validators
@testing_strategy Unit tests for each validator, integration tests for engine
@governance Dr. Elena Vasquez framework - Quality and standards enforcement

Business Logic Summary:
- Detect magic variables with context awareness
- Find and prevent boilerplate code
- Track test execution and staleness
- Enforce domain-specific best practices
- Calculate risk scores for changes
- Provide actionable fix suggestions

Architecture Integration:
- Pluggable validator system
- Domain-specific rule engines
- Test execution database
- Dependency analysis
- Git hook integration
"""

import re
import ast
import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import yaml

# Business constants
MAX_ALLOWED_COMPLEXITY = 10
MIN_TEST_COVERAGE = 80
MAX_FILE_SIZE_LINES = 500
TEST_STALENESS_HOURS = 24
BOILERPLATE_THRESHOLD = 0.85

class Severity(Enum):
    """Violation severity levels"""
    CRITICAL = "CRITICAL"  # Blocks commit
    HIGH = "HIGH"          # Requires justification
    MEDIUM = "MEDIUM"      # Warning
    LOW = "LOW"            # Info
    INFO = "INFO"          # FYI only

@dataclass
class Violation:
    """Represents a governance violation"""
    rule: str
    message: str
    severity: Severity
    file: str
    line: int = 0
    column: int = 0
    suggestion: str = ""
    auto_fixable: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'rule': self.rule,
            'message': self.message,
            'severity': self.severity.value,
            'file': self.file,
            'line': self.line,
            'column': self.column,
            'suggestion': self.suggestion,
            'auto_fixable': self.auto_fixable
        }

class MagicVariableDetector:
    """
    Detects magic variables (unnamed constants) with context awareness.
    Implements Marcus Johnson's smart detection algorithm.
    """
    
    def __init__(self):
        # Load configuration
        self.config = self._load_config()
        
        # Universal allowed values
        self.allowed_numbers = {0, 1, -1, 2, 10, 100, 1000}
        self.http_codes = {200, 201, 204, 301, 302, 400, 401, 403, 404, 500, 502, 503}
        self.common_ports = {80, 443, 3000, 3306, 5432, 6379, 8000, 8080}
        self.time_values = {0, 100, 250, 500, 1000, 5000, 10000, 30000, 60000}
        
    def _load_config(self) -> Dict:
        """Load magic variable configuration"""
        config_path = Path(__file__).parent.parent / 'config' / 'magic-variables.yml'
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def detect(self, file_path: str, content: str) -> List[Violation]:
        """Detect magic variables in code"""
        violations = []
        
        # Skip test files
        if 'test' in file_path or 'spec' in file_path:
            return violations
        
        # Parse based on file type
        if file_path.endswith('.py'):
            violations.extend(self._detect_python(file_path, content))
        elif file_path.endswith(('.ts', '.js')):
            violations.extend(self._detect_javascript(file_path, content))
        elif file_path.endswith('.scss'):
            violations.extend(self._detect_scss(file_path, content))
            
        return violations
    
    def _detect_python(self, file_path: str, content: str) -> List[Violation]:
        """Detect magic variables in Python code"""
        violations = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant):
                    if isinstance(node.value, (int, float)):
                        if not self._is_allowed_number(node.value, content, node.lineno):
                            violations.append(Violation(
                                rule='MAGIC_NUMBER',
                                message=f'Magic number {node.value} should be a named constant',
                                severity=Severity.MEDIUM,
                                file=file_path,
                                line=node.lineno,
                                column=node.col_offset,
                                suggestion=f'Define as constant: {self._suggest_constant_name(node.value)}',
                                auto_fixable=True
                            ))
                    elif isinstance(node.value, str) and len(node.value) > 2:
                        if self._looks_like_config_value(node.value):
                            violations.append(Violation(
                                rule='MAGIC_STRING',
                                message=f'String "{node.value[:20]}..." should be in configuration',
                                severity=Severity.LOW,
                                file=file_path,
                                line=node.lineno,
                                column=node.col_offset,
                                suggestion='Move to configuration file'
                            ))
        except SyntaxError:
            pass  # Invalid Python, other validators will catch
            
        return violations
    
    def _detect_javascript(self, file_path: str, content: str) -> List[Violation]:
        """Detect magic variables in JavaScript/TypeScript"""
        violations = []
        
        # Regex patterns for common magic values
        patterns = [
            (r'setTimeout\([^,]+,\s*(\d+)', 'timeout'),
            (r'setInterval\([^,]+,\s*(\d+)', 'interval'),
            (r'port[\s:=]+(\d+)', 'port'),
            (r'limit[\s:=]+(\d+)', 'limit'),
            (r'max[A-Z][\w]*[\s:=]+(\d+)', 'max'),
            (r'min[A-Z][\w]*[\s:=]+(\d+)', 'min'),
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern, context in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    value = int(match.group(1))
                    if not self._is_allowed_in_context(value, context):
                        violations.append(Violation(
                            rule='MAGIC_NUMBER',
                            message=f'Magic {context} value {value} should be a constant',
                            severity=Severity.MEDIUM,
                            file=file_path,
                            line=line_num,
                            column=match.start(1),
                            suggestion=f'const {context.upper()}_{context.upper()} = {value};',
                            auto_fixable=True
                        ))
        
        return violations
    
    def _detect_scss(self, file_path: str, content: str) -> List[Violation]:
        """Detect magic values in SCSS"""
        violations = []
        
        # Magic colors (not black/white)
        color_pattern = r'#(?![0f]{3}|[0f]{6})[0-9a-f]{3,6}'
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip if line has variable definition
            if '$' in line or 'var(--' in line:
                continue
                
            colors = re.finditer(color_pattern, line, re.IGNORECASE)
            for color in colors:
                violations.append(Violation(
                    rule='MAGIC_COLOR',
                    message=f'Color {color.group()} should use a variable',
                    severity=Severity.HIGH,
                    file=file_path,
                    line=line_num,
                    column=color.start(),
                    suggestion='Use $color-primary or CSS custom property',
                    auto_fixable=False
                ))
            
            # Magic dimensions
            dimension_pattern = r'\b(\d+)(px|em|rem|%)'
            dimensions = re.finditer(dimension_pattern, line)
            for dim in dimensions:
                value = int(dim.group(1))
                unit = dim.group(2)
                if value not in {0, 1, 2, 50, 100} and unit == 'px' and value > 10:
                    violations.append(Violation(
                        rule='MAGIC_DIMENSION',
                        message=f'Dimension {dim.group()} should use a variable',
                        severity=Severity.LOW,
                        file=file_path,
                        line=line_num,
                        column=dim.start(),
                        suggestion='Use $spacing-* or $size-* variable'
                    ))
        
        return violations
    
    def _is_allowed_number(self, value: float, context: str, line_num: int) -> bool:
        """Check if a number is allowed in its context"""
        # Universal allowed
        if value in self.allowed_numbers:
            return True
            
        # HTTP status codes
        if value in self.http_codes and any(word in context.lower() 
                                           for word in ['status', 'code', 'response']):
            return True
            
        # Port numbers
        if value in self.common_ports and 'port' in context.lower():
            return True
            
        # Time values
        if value in self.time_values and any(word in context.lower() 
                                            for word in ['timeout', 'delay', 'interval']):
            return True
            
        # Array indices
        if 0 <= value < 10 and '[' in context:
            return True
            
        return False
    
    def _is_allowed_in_context(self, value: int, context: str) -> bool:
        """Check if value is allowed in specific context"""
        context_rules = {
            'timeout': self.time_values,
            'interval': self.time_values,
            'port': self.common_ports,
            'limit': {10, 50, 100, 1000},
            'max': {10, 50, 100, 1000, 10000},
            'min': {0, 1, 2, 5, 10}
        }
        
        return value in context_rules.get(context, set())
    
    def _suggest_constant_name(self, value: Any) -> str:
        """Suggest a constant name for a value"""
        if isinstance(value, int):
            if value in self.http_codes:
                return f'HTTP_STATUS_{value}'
            elif value in self.common_ports:
                return f'PORT_{value}'
            elif value in self.time_values:
                return f'TIMEOUT_{value}_MS'
            else:
                return f'CONSTANT_{value}'
        return 'CONFIG_VALUE'
    
    def _looks_like_config_value(self, value: str) -> bool:
        """Check if string looks like it should be in config"""
        # URLs, paths, keys, etc.
        patterns = [
            r'^https?://',
            r'^/[\w/]+',
            r'^[\w-]+\.[\w]+',  # domain-like
            r'^[A-Z_]{5,}',  # looks like env var
        ]
        
        return any(re.match(pattern, value) for pattern in patterns)


class TestExecutionTracker:
    """
    Tracks test execution history and determines when tests need to be run.
    Implements Priya Sharma's comprehensive test tracking.
    """
    
    def __init__(self, db_path: str = '.governance/test-execution.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize test execution database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    suite TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    commit_hash TEXT NOT NULL,
                    branch TEXT,
                    coverage REAL,
                    duration REAL,
                    passed INTEGER,
                    failed INTEGER,
                    skipped INTEGER,
                    files_covered TEXT,
                    risk_score INTEGER
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    change_time DATETIME NOT NULL,
                    commit_hash TEXT NOT NULL,
                    change_type TEXT,
                    lines_added INTEGER,
                    lines_removed INTEGER
                )
            """)
    
    def record_test_run(self, suite: str, results: Dict[str, Any]):
        """Record a test execution"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO test_runs 
                (suite, timestamp, commit_hash, branch, coverage, duration, 
                 passed, failed, skipped, files_covered, risk_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                suite,
                datetime.now().isoformat(),
                results.get('commit_hash', 'unknown'),
                results.get('branch', 'main'),
                results.get('coverage', 0),
                results.get('duration', 0),
                results.get('passed', 0),
                results.get('failed', 0),
                results.get('skipped', 0),
                json.dumps(results.get('files_covered', [])),
                self._calculate_risk_score(results)
            ))
    
    def get_test_status(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Get current test status and requirements"""
        with sqlite3.connect(self.db_path) as conn:
            # Get last test run
            cursor = conn.execute("""
                SELECT * FROM test_runs 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            
            last_run = cursor.fetchone()
            
            if not last_run:
                return {
                    'status': 'CRITICAL',
                    'message': 'No test runs recorded',
                    'required': True,
                    'suites': ['all'],
                    'risk_score': 100
                }
            
            # Calculate staleness
            last_run_time = datetime.fromisoformat(last_run[2])  # timestamp column
            hours_old = (datetime.now() - last_run_time).total_seconds() / 3600
            
            # Get changes since last run
            cursor = conn.execute("""
                SELECT COUNT(*) FROM file_changes 
                WHERE change_time > ?
            """, (last_run_time.isoformat(),))
            
            changes_count = cursor.fetchone()[0]
            
            # Determine requirements
            if hours_old > 48:
                status = 'CRITICAL'
                message = f'Tests are {hours_old:.1f} hours old'
                required = True
            elif hours_old > 24:
                status = 'HIGH'
                message = f'Tests are {hours_old:.1f} hours old'
                required = True
            elif changes_count > 10:
                status = 'HIGH'
                message = f'{changes_count} files changed since last test'
                required = True
            elif changes_count > 5:
                status = 'MEDIUM'
                message = f'{changes_count} files changed since last test'
                required = True
            else:
                status = 'OK'
                message = f'Tests current ({hours_old:.1f} hours old)'
                required = False
            
            return {
                'status': status,
                'message': message,
                'required': required,
                'last_run': last_run_time.isoformat(),
                'hours_old': hours_old,
                'changes_since': changes_count,
                'coverage': last_run[5],  # coverage column
                'risk_score': self._calculate_current_risk(hours_old, changes_count)
            }
    
    def record_file_change(self, file_path: str, change_type: str = 'modified'):
        """Record a file change for tracking"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO file_changes 
                (file_path, change_time, commit_hash, change_type)
                VALUES (?, ?, ?, ?)
            """, (
                file_path,
                datetime.now().isoformat(),
                self._get_current_commit(),
                change_type
            ))
    
    def _calculate_risk_score(self, results: Dict[str, Any]) -> int:
        """Calculate risk score for test results"""
        risk = 0
        
        # Coverage factor
        coverage = results.get('coverage', 0)
        if coverage < 80:
            risk += (80 - coverage) // 2
        
        # Failure factor
        failed = results.get('failed', 0)
        total = results.get('passed', 0) + failed
        if total > 0:
            failure_rate = (failed / total) * 100
            risk += int(failure_rate)
        
        # Duration factor (slow tests = risk)
        duration = results.get('duration', 0)
        if duration > 300:  # 5 minutes
            risk += 10
        
        return min(risk, 100)
    
    def _calculate_current_risk(self, hours_old: float, changes: int) -> int:
        """Calculate current risk score"""
        risk = 0
        
        # Time factor
        risk += min(int(hours_old * 2), 50)
        
        # Change factor
        risk += min(changes * 5, 40)
        
        # Add base risk for no recent tests
        if hours_old > 24:
            risk += 10
        
        return min(risk, 100)
    
    def _get_current_commit(self) -> str:
        """Get current git commit hash"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True
            )
            return result.stdout.strip()[:8]
        except:
            return 'unknown'


class BoilerplateDetector:
    """
    Detects boilerplate code patterns using fuzzy matching.
    Implements Sam Martinez's pattern detection algorithm.
    """
    
    def __init__(self, threshold: float = 0.85, min_lines: int = 5):
        self.threshold = threshold
        self.min_lines = min_lines
        self.patterns = {}
        self.exclusions = [
            'import', 'require', 'from',  # Import statements
            'Copyright', 'License',        # License headers
            'beforeEach', 'afterEach',     # Test setup
            'describe', 'it('              # Test structure
        ]
    
    def detect(self, files: List[Tuple[str, str]]) -> List[Violation]:
        """Detect boilerplate across multiple files"""
        violations = []
        code_blocks = {}
        
        # Extract and normalize code blocks
        for file_path, content in files:
            blocks = self._extract_code_blocks(file_path, content)
            for block in blocks:
                if len(block['lines']) < self.min_lines:
                    continue
                    
                if self._is_excluded(block['code']):
                    continue
                    
                normalized = self._normalize_code(block['code'])
                signature = self._generate_signature(normalized)
                
                if signature not in code_blocks:
                    code_blocks[signature] = []
                code_blocks[signature].append(block)
        
        # Find violations
        for signature, blocks in code_blocks.items():
            if len(blocks) >= 3:  # Pattern appears 3+ times
                violations.append(Violation(
                    rule='BOILERPLATE_DETECTED',
                    message=f'Code pattern repeated {len(blocks)} times across files',
                    severity=Severity.MEDIUM,
                    file=blocks[0]['file'],
                    line=blocks[0]['start_line'],
                    suggestion=self._suggest_refactoring(blocks[0]['code']),
                    auto_fixable=False
                ))
                
                # Add info about other occurrences
                for block in blocks[1:3]:  # Show first 2 duplicates
                    violations.append(Violation(
                        rule='BOILERPLATE_LOCATION',
                        message=f'Duplicate found in {block["file"]}:{block["start_line"]}',
                        severity=Severity.INFO,
                        file=block['file'],
                        line=block['start_line']
                    ))
        
        return violations
    
    def _extract_code_blocks(self, file_path: str, content: str) -> List[Dict]:
        """Extract meaningful code blocks from file"""
        blocks = []
        lines = content.split('\n')
        
        # Simple block extraction (can be improved with AST)
        current_block = []
        start_line = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Start new block on function/class definition
            if any(keyword in stripped for keyword in ['def ', 'class ', 'function ', 'const ', 'async ']):
                if len(current_block) >= self.min_lines:
                    blocks.append({
                        'file': file_path,
                        'start_line': start_line,
                        'lines': current_block,
                        'code': '\n'.join(current_block)
                    })
                current_block = [line]
                start_line = i
            elif stripped:
                current_block.append(line)
            elif len(current_block) >= self.min_lines:
                # Empty line, end block if it's long enough
                blocks.append({
                    'file': file_path,
                    'start_line': start_line,
                    'lines': current_block,
                    'code': '\n'.join(current_block)
                })
                current_block = []
        
        # Don't forget last block
        if len(current_block) >= self.min_lines:
            blocks.append({
                'file': file_path,
                'start_line': start_line,
                'lines': current_block,
                'code': '\n'.join(current_block)
            })
        
        return blocks
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code for comparison"""
        normalized = code
        
        # Replace variable names with placeholder
        normalized = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', 'VAR', normalized)
        
        # Replace string literals
        normalized = re.sub(r'["\'][^"^\']*["\']', 'STRING', normalized)
        
        # Replace numbers
        normalized = re.sub(r'\b\d+\b', 'NUM', normalized)
        
        # Remove comments
        normalized = re.sub(r'#.*$', '', normalized, flags=re.MULTILINE)
        normalized = re.sub(r'//.*$', '', normalized, flags=re.MULTILINE)
        normalized = re.sub(r'/\*.*?\*/', '', normalized, flags=re.DOTALL)
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized.strip()
    
    def _generate_signature(self, normalized: str) -> str:
        """Generate signature for normalized code"""
        # Use hash for efficient comparison
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _is_excluded(self, code: str) -> bool:
        """Check if code block should be excluded"""
        return any(exclusion in code for exclusion in self.exclusions)
    
    def _suggest_refactoring(self, code: str) -> str:
        """Suggest refactoring for boilerplate code"""
        if 'try' in code and 'except' in code:
            return 'Extract to error handling utility function'
        elif 'if' in code and 'validate' in code:
            return 'Create reusable validation helper'
        elif 'fetch' in code or 'axios' in code or 'http' in code:
            return 'Use centralized API client'
        elif 'connect' in code and 'database' in code:
            return 'Use database connection manager'
        elif 'createElement' in code or 'Component' in code:
            return 'Create reusable component'
        elif 'test' in code or 'expect' in code:
            return 'Extract to test utility function'
        else:
            return 'Extract to shared utility module'


class EnhancedGovernanceEngine:
    """
    Main governance engine that orchestrates all validators.
    Central coordination point for all governance rules.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path('.governance')
        self.magic_detector = MagicVariableDetector()
        self.test_tracker = TestExecutionTracker()
        self.boilerplate_detector = BoilerplateDetector()
        self.violations = []
        
    def validate_files(self, files: List[Tuple[str, str]]) -> Tuple[List[Violation], int]:
        """
        Validate multiple files and return violations with risk score.
        
        Args:
            files: List of (file_path, content) tuples
            
        Returns:
            Tuple of (violations, risk_score)
        """
        all_violations = []
        risk_score = 0
        
        # Check test execution status
        test_status = self.test_tracker.get_test_status()
        if test_status['required']:
            all_violations.append(Violation(
                rule='TESTS_REQUIRED',
                message=test_status['message'],
                severity=Severity[test_status['status']] if test_status['status'] != 'OK' else Severity.INFO,
                file='',
                suggestion='Run test suite before committing'
            ))
            risk_score += test_status.get('risk_score', 0)
        
        # Check individual files
        for file_path, content in files:
            # Track file change
            self.test_tracker.record_file_change(file_path)
            
            # Magic variables
            violations = self.magic_detector.detect(file_path, content)
            all_violations.extend(violations)
            
            # Add to risk score based on file criticality
            if any(critical in file_path for critical in ['service', 'manager', 'core', 'auth']):
                risk_score += 10
        
        # Check for boilerplate across all files
        boilerplate_violations = self.boilerplate_detector.detect(files)
        all_violations.extend(boilerplate_violations)
        
        # Cap risk score at 100
        risk_score = min(risk_score, 100)
        
        return all_violations, risk_score
    
    def format_report(self, violations: List[Violation], risk_score: int) -> str:
        """Format violations into readable report"""
        if not violations:
            return "✅ No governance violations found\n"
        
        report = []
        report.append("="*60)
        report.append("GOVERNANCE VALIDATION REPORT")
        report.append("="*60)
        report.append(f"\nRisk Score: {risk_score}/100")
        report.append(f"Total Violations: {len(violations)}\n")
        
        # Group by severity
        by_severity = {}
        for v in violations:
            if v.severity not in by_severity:
                by_severity[v.severity] = []
            by_severity[v.severity].append(v)
        
        # Report by severity
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            if severity in by_severity:
                report.append(f"\n{severity.value} ({len(by_severity[severity])})")
                report.append("-" * 40)
                
                for v in by_severity[severity][:5]:  # Show first 5 of each
                    if v.file:
                        report.append(f"  {v.file}:{v.line}")
                    report.append(f"  {v.rule}: {v.message}")
                    if v.suggestion:
                        report.append(f"  💡 {v.suggestion}")
                    report.append("")
                
                if len(by_severity[severity]) > 5:
                    report.append(f"  ... and {len(by_severity[severity]) - 5} more\n")
        
        # Summary
        critical_count = len(by_severity.get(Severity.CRITICAL, []))
        if critical_count > 0:
            report.append("\n❌ COMMIT BLOCKED: Fix CRITICAL violations")
        elif risk_score > 75:
            report.append("\n⚠️  HIGH RISK: Consider reviewing changes")
        else:
            report.append("\n✅ Commit allowed with warnings")
        
        report.append("="*60)
        
        return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    engine = EnhancedGovernanceEngine()
    
    # Test files
    test_files = [
        ("example.py", """def calculate_price(amount):
    tax = amount * 0.08  # Magic number!
    shipping = 5.99  # Another magic number
    if amount > 100:  # And another!
        discount = 10
    return amount + tax + shipping - discount
""")
    ]
    
    violations, risk = engine.validate_files(test_files)
    print(engine.format_report(violations, risk))
