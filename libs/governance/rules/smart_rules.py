#!/usr/bin/env python3
"""
@fileoverview Enhanced smart rules with exemption support for intelligent governance
@author Dr. Sarah Chen v2.0 & Alex Novak v1.5 - 2025-01-28
@architecture Backend - Enhanced smart rule engine with context awareness
@responsibility Apply intelligent context-aware validation with exemption support
@dependencies datetime, re, typing, yaml, pathlib, fnmatch
@integration_points Used by governance hooks for multi-language validation
@testing_strategy Unit tests for all rule patterns and exemptions
@governance Core component implementing Phase 1.5 architectural change

Business Logic Summary:
- Context-aware pattern detection (not just simple matching)
- Multi-language exemption support
- Separate safe operations from dangerous patterns
- File, class, and context-based exemptions

Architecture Integration:
- Implements cross-language exemption architecture
- Part of Phase 1.5 governance enhancement
- Used by pre-commit hooks with reduced false positives
- Supports polyglot codebase governance

Sarah's Framework Check:
- What breaks first: False positives blocking legitimate code
- How we know: Exemption logs and pattern tracking
- Plan B: Override with documented exemptions
"""

from datetime import datetime
import re
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
import fnmatch

# Import hallucination detector if available
try:
    from libs.governance.validators.basic_hallucination_detector import (
        BasicHallucinationDetector,
        HallucinationSeverity,
        create_detector_for_smart_rules
    )
    HALLUCINATION_DETECTION_AVAILABLE = True
except ImportError:
    HALLUCINATION_DETECTION_AVAILABLE = False


class ExemptionManager:
    """
    @class ExemptionManager
    @description Manages exemptions for governance rules
    @architecture_role Handle context-aware exemptions across languages
    @business_logic Reduce false positives while maintaining security
    """
    
    def __init__(self, exemption_file: Optional[str] = None):
        """Initialize exemption manager"""
        self.exemptions = self._load_exemptions(exemption_file)
        self._cache = {}  # Cache exemption lookups
        
    def _load_exemptions(self, exemption_file: Optional[str]) -> Dict[str, Any]:
        """Load exemption configuration"""
        if not exemption_file:
            # Look for default locations
            search_paths = [
                Path('.governance/exemptions.yml'),
                Path('governance-config/exemptions.yml'),
                Path('exemptions.yml')
            ]
            
            for path in search_paths:
                if path.exists():
                    exemption_file = str(path)
                    break
        
        if not exemption_file or not Path(exemption_file).exists():
            # Return default exemptions if no file found
            return self._get_default_exemptions()
        
        try:
            with open(exemption_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load exemptions from {exemption_file}: {e}")
            return self._get_default_exemptions()
    
    def _get_default_exemptions(self) -> Dict[str, Any]:
        """Get default exemptions"""
        return {
            'global_safe_patterns': {
                'python': [
                    're.compile',
                    'ast.literal_eval', 
                    'json.loads',
                    'yaml.safe_load'
                ],
                'typescript': [
                    'JSON.parse',
                    'RegExp'
                ],
                'javascript': [
                    'JSON.parse',
                    'RegExp'
                ]
            },
            'file_exemptions': [],
            'class_exemptions': [],
            'context_exemptions': [],
            'temporary_exemptions': []
        }
    
    def is_pattern_exempt(
        self, 
        pattern: str, 
        file_path: str,
        content: str,
        language: str = 'python'
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a pattern is exempt in the given context
        
        @param pattern The pattern being checked
        @param file_path Path to the file
        @param content File content for context analysis
        @param language Programming language
        @returns (is_exempt, reason)
        """
        # Check cache first
        cache_key = f"{pattern}:{file_path}:{language}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # 1. Check global safe patterns for language
        safe_patterns = self.exemptions.get('global_safe_patterns', {}).get(language, [])
        for safe_pattern in safe_patterns:
            if safe_pattern.lower() in pattern.lower():
                result = (True, f"Globally safe pattern for {language}: {safe_pattern}")
                self._cache[cache_key] = result
                return result
        
        # 2. Check file-specific exemptions
        for exemption in self.exemptions.get('file_exemptions', []):
            if self._matches_file_pattern(file_path, exemption['path']):
                if pattern in exemption.get('patterns', []):
                    # Check expiration
                    if self._is_exemption_valid(exemption):
                        result = (True, f"File exemption: {exemption.get('reason', 'No reason provided')}")
                        self._cache[cache_key] = result
                        return result
        
        # 3. Check class-specific exemptions
        for exemption in self.exemptions.get('class_exemptions', []):
            class_name = exemption['name']
            if f"class {class_name}" in content:
                if pattern in exemption.get('patterns', []):
                    result = (True, f"Class exemption for {class_name}: {exemption.get('reason', 'No reason provided')}")
                    self._cache[cache_key] = result
                    return result
        
        # 4. Check context-based exemptions
        for exemption in self.exemptions.get('context_exemptions', []):
            context_pattern = exemption['context']
            if context_pattern in file_path or context_pattern in content:
                if pattern in exemption.get('patterns', []):
                    # Check additional requirements
                    requires = exemption.get('requires')
                    if requires and requires not in content:
                        continue
                    result = (True, f"Context exemption: {exemption.get('reason', 'No reason provided')}")
                    self._cache[cache_key] = result
                    return result
        
        # 5. Check temporary exemptions
        for exemption in self.exemptions.get('temporary_exemptions', []):
            if self._matches_file_pattern(file_path, exemption['path']):
                if pattern in exemption.get('patterns', []):
                    if self._is_exemption_valid(exemption):
                        result = (True, f"Temporary exemption (expires {exemption.get('expires', 'unknown')}): {exemption.get('reason', 'No reason provided')}")
                        self._cache[cache_key] = result
                        return result
        
        result = (False, None)
        self._cache[cache_key] = result
        return result
    
    def _matches_file_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches pattern (supports glob)"""
        # Normalize paths
        file_path = Path(file_path).as_posix()
        pattern = pattern.replace('\\', '/')
        
        # Direct match
        if pattern in file_path:
            return True
        
        # Glob match
        if '*' in pattern or '?' in pattern:
            return fnmatch.fnmatch(file_path, pattern)
        
        return False
    
    def _is_exemption_valid(self, exemption: Dict[str, Any]) -> bool:
        """Check if exemption is still valid (not expired)"""
        expires = exemption.get('expires')
        if not expires:
            return True
        
        try:
            expiry_date = datetime.strptime(expires, '%Y-%m-%d')
            return datetime.now() < expiry_date
        except:
            return True  # If can't parse date, assume valid
    
    def get_exemption_stats(self) -> Dict[str, Any]:
        """Get statistics about exemptions"""
        stats = {
            'total_exemptions': 0,
            'expired_exemptions': [],
            'expiring_soon': [],
            'by_type': {}
        }
        
        # Count exemptions by type
        for exemption_type in ['file_exemptions', 'class_exemptions', 
                               'context_exemptions', 'temporary_exemptions']:
            exemptions = self.exemptions.get(exemption_type, [])
            stats['by_type'][exemption_type] = len(exemptions)
            stats['total_exemptions'] += len(exemptions)
            
            # Check for expired or expiring
            for exemption in exemptions:
                expires = exemption.get('expires')
                if expires:
                    try:
                        expiry_date = datetime.strptime(expires, '%Y-%m-%d')
                        days_until = (expiry_date - datetime.now()).days
                        
                        if days_until < 0:
                            stats['expired_exemptions'].append({
                                'type': exemption_type,
                                'path': exemption.get('path', exemption.get('name', 'unknown')),
                                'expired': expires
                            })
                        elif days_until < 30:
                            stats['expiring_soon'].append({
                                'type': exemption_type,
                                'path': exemption.get('path', exemption.get('name', 'unknown')),
                                'expires': expires,
                                'days_remaining': days_until
                            })
                    except:
                        pass
        
        return stats


class SmartRules:
    """
    @class SmartRules
    @description Intelligent context-aware validation rules with exemptions
    @architecture_role Pattern detection and validation with reduced false positives
    @business_logic Security and quality enforcement with practical flexibility
    
    BACKWARD COMPATIBILITY: This class maintains the same interface as v1
    while adding enhanced capabilities internally.
    """
    
    def __init__(self, exemption_file: Optional[str] = None):
        """Initialize smart rules with patterns and exemption support"""
        # Initialize exemption manager
        self.exemption_manager = ExemptionManager(exemption_file)
        
        # Initialize hallucination detector if available
        self.hallucination_detector = None
        if HALLUCINATION_DETECTION_AVAILABLE:
            try:
                self.hallucination_detector = create_detector_for_smart_rules()
            except Exception:
                # Silently fail if detector can't be created
                pass
        
        # Keep backward compatible patterns for legacy code
        self.dangerous_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__\s*\(',
            r'compile\s*\(',
            r'globals\s*\(\)',
            r'locals\s*\(\)',
            r'setattr\s*\(',
            r'delattr\s*\('
        ]
        
        self.secret_patterns = [
            r'(?i)(api[_-]?key|apikey|secret|password|pwd|token|auth)\s*[:=]\s*["\'][^"\']+["\']',
            r'(?i)bearer\s+[a-zA-Z0-9_\-\.]+',
            r'(?i)(aws|amazon)[_-]?(secret|access)[_-]?key\s*[:=]\s*["\'][^"\']+["\']'
        ]
        
        # Enhanced pattern dictionaries for context-aware checking
        self.dangerous_pattern_dict = {
            'eval': r'eval\s*\(',
            'exec': r'exec\s*\(',
            '__import__': r'__import__\s*\(',
            'globals': r'globals\s*\(\)',
            'locals': r'locals\s*\(\)'
        }
        
        self.context_dependent_patterns = {
            'compile': r'compile\s*\(',
            'setattr': r'setattr\s*\(',
            'delattr': r'delattr\s*\(',
            'getattr': r'getattr\s*\('
        }
    
    @staticmethod
    def is_risky_time() -> bool:
        """Check if current time is risky for changes"""
        hour = datetime.now().hour
        day = datetime.now().weekday()
        
        # Late night/early morning (10 PM - 6 AM)
        if hour < 6 or hour >= 22:
            return True
            
        # Friday afternoon (after 2 PM on Friday)
        if day == 4 and hour >= 14:  # 4 = Friday
            return True
            
        # Sunday (preparing for Monday)
        if day == 6:  # 6 = Sunday
            return True
            
        return False
    
    @staticmethod
    def is_friday_afternoon() -> bool:
        """Check if it's Friday afternoon"""
        now = datetime.now()
        return now.weekday() == 4 and now.hour >= 14
    
    def contains_dangerous_patterns(self, context: Dict[str, Any]) -> bool:
        """
        Check for dangerous patterns with context awareness
        
        @param context Code context with 'content' and optionally 'path' keys
        @returns True if dangerous patterns found
        
        BACKWARD COMPATIBLE: Works with old code passing just 'content'
        """
        content = context.get('content', '')
        file_path = context.get('path', 'unknown.py')
        
        # Use enhanced checking if possible
        dangerous, _ = self._check_patterns_with_context(content, file_path)
        return len(dangerous) > 0
    
    def get_dangerous_patterns(self, context: Dict[str, Any]) -> List[str]:
        """
        Get list of dangerous patterns found with context awareness
        
        @param context Code context with 'content' and optionally 'path' keys
        @returns List of patterns found
        """
        content = context.get('content', '')
        file_path = context.get('path', 'unknown.py')
        
        dangerous, _ = self._check_patterns_with_context(content, file_path)
        return dangerous
    
    def check_for_secrets(self, context: Dict[str, Any]) -> bool:
        """
        Check for potential secrets in code
        
        @param context Code context with 'content' key
        @returns True if potential secrets found
        """
        content = context.get('content', '')
        
        # Check for hardcoded secrets
        for pattern in self.secret_patterns:
            if re.search(pattern, content):
                # Allow environment variable usage
                if 'os.environ' not in content and 'process.env' not in content:
                    return True
        
        return False
    
    def check_complexity(self, context: Dict[str, Any]) -> bool:
        """
        Check code complexity
        
        @param context Code context with 'content' key
        @returns True if complexity is high
        """
        content = context.get('content', '')
        
        # Simple heuristic: count nested indentation levels
        lines = content.split('\n')
        max_indent = 0
        current_indent = 0
        
        for line in lines:
            # Count leading spaces (assuming 4-space indent)
            stripped = line.lstrip()
            if stripped:
                indent = (len(line) - len(stripped)) // 4
                if indent > current_indent:
                    current_indent = indent
                    max_indent = max(max_indent, current_indent)
                elif indent < current_indent:
                    current_indent = indent
        
        # High complexity if more than 4 levels of nesting
        return max_indent > 4
    
    def validate_documentation(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Validate documentation requirements
        
        @param context Code context with 'content' and 'path' keys
        @returns Issue description or None if valid
        """
        content = context.get('content', '')
        path = context.get('path', '')
        
        # Skip documentation checks for markdown files
        if path.endswith('.md'):
            return None
        
        # Check for file-level documentation
        if path.endswith(('.py', '.ts', '.js')):
            if '@fileoverview' not in content and '"""' not in content[:200]:
                return f"Missing file documentation in {path}"
        
        return None
    
    def apply_rules(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply all rules to context (with hallucination detection)
        
        @param context Code context
        @returns Results dictionary including hallucination detection
        """
        results = {
            'dangerous_patterns': self.contains_dangerous_patterns(context),
            'secrets_detected': self.check_for_secrets(context),
            'high_complexity': self.check_complexity(context),
            'documentation_issues': self.validate_documentation(context)
        }
        
        # Add hallucination detection if available (Phase 1.5b)
        if self.hallucination_detector:
            hallucination_results = self.check_for_hallucinations(context)
            results['hallucinations_detected'] = hallucination_results.get('has_hallucinations', False)
            results['hallucination_details'] = hallucination_results
        
        return results
    
    @staticmethod
    def check_file_patterns(files: List[str]) -> Dict[str, List[str]]:
        """
        Analyze file patterns for risks
        """
        results = {
            'test_files': [],
            'config_files': [],
            'sensitive_files': [],
            'documentation': [],
            'governance_files': []
        }
        
        for file in files:
            file_lower = file.lower()
            
            # Test files
            if 'test' in file_lower or 'spec' in file_lower:
                results['test_files'].append(file)
            
            # Config files
            if any(ext in file_lower for ext in ['.env', '.config', '.yaml', '.yml', '.json']):
                results['config_files'].append(file)
            
            # Sensitive files
            if any(sensitive in file_lower for sensitive in ['password', 'secret', 'key', 'token', 'credential']):
                results['sensitive_files'].append(file)
            
            # Documentation
            if any(ext in file_lower for ext in ['.md', '.rst', '.txt', 'readme']):
                results['documentation'].append(file)
            
            # Governance files
            if 'governance' in file_lower:
                results['governance_files'].append(file)
        
        return results
    
    @staticmethod
    def analyze_commit_message(message: str) -> Dict[str, Any]:
        """
        Analyze commit message for patterns
        """
        analysis = {
            'has_type': False,
            'has_description': False,
            'is_wip': False,
            'is_emergency': False,
            'has_issue_ref': False
        }
        
        message_lower = message.lower()
        
        # Check for conventional commit types
        commit_types = ['feat:', 'fix:', 'docs:', 'style:', 'refactor:', 
                       'test:', 'chore:', 'perf:', 'build:', 'ci:']
        analysis['has_type'] = any(message.startswith(t) for t in commit_types)
        
        # Check description length
        analysis['has_description'] = len(message) > 10
        
        # Check for WIP
        analysis['is_wip'] = 'wip' in message_lower or 'work in progress' in message_lower
        
        # Check for emergency
        analysis['is_emergency'] = any(word in message_lower for word in 
                                      ['emergency', 'urgent', 'hotfix', 'critical'])
        
        # Check for issue reference
        analysis['has_issue_ref'] = bool(re.search(r'#\d+', message))
        
        return analysis
    
    @staticmethod
    def calculate_risk_score(context) -> float:
        """
        Calculate overall risk score (0.0 - 1.0)
        """
        risk_score = 0.0
        
        # Time-based risk
        if SmartRules.is_risky_time():
            risk_score += 0.3
        
        # Check payload for dangerous patterns (if context has appropriate methods)
        if hasattr(context, 'payload'):
            smart_rules = SmartRules()  # Create instance for checking
            dangerous = smart_rules.contains_dangerous_patterns({'content': str(context.payload)})
            if dangerous:
                risk_score += 0.3
            
            secrets = smart_rules.check_for_secrets({'content': str(context.payload)})
            if secrets:
                risk_score += 0.5  # High risk for secrets
        
        # Check operation type
        risky_operations = ['delete', 'drop', 'remove', 'disable', 'force']
        if hasattr(context, 'operation_type'):
            op_lower = context.operation_type.lower()
            for risky_op in risky_operations:
                if risky_op in op_lower:
                    risk_score += 0.2
                    break
        
        # Cap at 1.0
        return min(risk_score, 1.0)
    
    # Enhanced methods (new functionality)
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.ts': 'typescript',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp'
        }
        
        return language_map.get(ext, 'unknown')
    
    def _check_patterns_with_context(
        self, 
        content: str, 
        file_path: str
    ) -> Tuple[List[str], List[str]]:
        """
        Check for dangerous patterns with context and exemptions
        
        @param content File content
        @param file_path File path for context
        @returns (dangerous_patterns_found, exemption_reasons)
        """
        dangerous = []
        exemptions = []
        language = self._detect_language(file_path)
        
        # Check truly dangerous patterns
        for pattern_name, pattern_regex in self.dangerous_pattern_dict.items():
            if re.search(pattern_regex, content):
                is_exempt, reason = self.exemption_manager.is_pattern_exempt(
                    pattern_name, file_path, content, language
                )
                
                if not is_exempt:
                    dangerous.append(pattern_name)
                elif reason:
                    exemptions.append(f"{pattern_name}: {reason}")
        
        # Check context-dependent patterns
        for pattern_name, pattern_regex in self.context_dependent_patterns.items():
            if re.search(pattern_regex, content):
                is_exempt, reason = self.exemption_manager.is_pattern_exempt(
                    pattern_name, file_path, content, language
                )
                
                if not is_exempt:
                    # Additional context checking
                    if pattern_name == 'compile' and 're.compile' in content:
                        exemptions.append(f"{pattern_name}: Regular expression compilation")
                    elif pattern_name == 'setattr' and '@dataclass' in content:
                        exemptions.append(f"{pattern_name}: Dataclass attribute update")
                    else:
                        dangerous.append(pattern_name)
                elif reason:
                    exemptions.append(f"{pattern_name}: {reason}")
        
        return dangerous, exemptions
    
    def validate_file(
        self, 
        file_path: str, 
        content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate a file with enhanced rules
        
        @param file_path Path to file
        @param content Optional content
        @returns Validation results
        """
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                return {
                    'valid': False,
                    'errors': [f"Could not read file: {e}"],
                    'warnings': [],
                    'exemptions': []
                }
        
        errors = []
        warnings = []
        
        # Check dangerous patterns with context
        dangerous, exemptions = self._check_patterns_with_context(content, file_path)
        
        if dangerous:
            errors.append(f"Dangerous patterns found: {', '.join(dangerous)}")
        
        # Check for secrets
        if self.check_for_secrets({'content': content}):
            errors.append("Potential secrets detected in code")
        
        # Documentation checks (skip for markdown)
        if not file_path.endswith('.md'):
            doc_issue = self.validate_documentation({'content': content, 'path': file_path})
            if doc_issue:
                warnings.append(doc_issue)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'exemptions': exemptions,
            'dangerous_patterns': dangerous
        }
    
    def check_for_hallucinations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check content for potential hallucinations
        
        @param context Code context with 'content' and optionally 'path' keys
        @returns Hallucination detection results
        
        Phase 1.5b implementation - basic pattern detection
        """
        # Default result if detector not available
        default_result = {
            'has_hallucinations': False,
            'critical_count': 0,
            'findings': [],
            'detector_available': False
        }
        
        if not self.hallucination_detector:
            return default_result
        
        content = context.get('content', '')
        file_path = context.get('path', '')
        
        # Skip certain file types
        if file_path:
            skip_extensions = ['.json', '.yml', '.yaml', '.lock', '.min.js', '.min.css']
            if any(file_path.endswith(ext) for ext in skip_extensions):
                return default_result
        
        try:
            # Detect hallucinations
            findings = self.hallucination_detector.detect(content, file_path)
            
            # Calculate metrics
            critical_count = sum(
                1 for f in findings 
                if f.severity == HallucinationSeverity.CRITICAL
            )
            error_count = sum(
                1 for f in findings 
                if f.severity == HallucinationSeverity.ERROR
            )
            
            return {
                'has_hallucinations': len(findings) > 0,
                'has_critical_hallucinations': critical_count > 0,
                'critical_count': critical_count,
                'error_count': error_count,
                'total_findings': len(findings),
                'findings': [f.to_dict() for f in findings],
                'detector_available': True
            }
            
        except Exception as e:
            # Return default on any error
            return default_result
    
    def get_exemption_report(self) -> str:
        """Generate exemption status report"""
        stats = self.exemption_manager.get_exemption_stats()
        
        report = ["Exemption Status Report", "=" * 50, ""]
        report.append(f"Total exemptions: {stats['total_exemptions']}")
        report.append("")
        
        # By type
        if stats['by_type']:
            report.append("Exemptions by type:")
            for exemption_type, count in stats['by_type'].items():
                report.append(f"  {exemption_type}: {count}")
            report.append("")
        
        # Expired
        if stats.get('expired_exemptions'):
            report.append(f"EXPIRED exemptions ({len(stats['expired_exemptions'])}):")
            for item in stats['expired_exemptions']:
                report.append(f"  - {item['path']} (expired: {item['expired']})")
            report.append("")
        
        # Expiring soon
        if stats.get('expiring_soon'):
            report.append(f"Expiring soon ({len(stats['expiring_soon'])}):")
            for item in stats['expiring_soon']:
                report.append(f"  - {item['path']} ({item['days_remaining']} days left)")
            report.append("")
        
        return "\n".join(report)


class RuleEnhancer:
    """
    @class RuleEnhancer
    @description Enhances rules with context-aware intelligence
    @architecture_role Rule improvement and suggestion engine
    @business_logic Provide context-aware rule enhancement
    """
    
    def __init__(self):
        """Initialize rule enhancer"""
        self.smart_rules = SmartRules()
    
    def enhance_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance rule based on context
        
        @param rule Rule to enhance
        @param context Current context
        @returns Enhanced rule
        """
        enhanced = rule.copy()
        enhanced['enhanced'] = True
        
        # Enhance based on context
        if 'critical' in str(context.get('files', [])).lower():
            enhanced['severity'] = 'error'
        
        if context.get('branch') == 'main':
            enhanced['strict_mode'] = True
        
        return enhanced
    
    def suggest_improvements(self, results: Dict[str, Any]) -> List[str]:
        """
        Suggest improvements based on rule results
        
        @param results Rule application results
        @returns List of improvement suggestions
        """
        suggestions = []
        
        if results.get('dangerous_patterns'):
            suggestions.append("Replace eval/exec with safer alternatives like ast.literal_eval")
            suggestions.append("Consider using a sandboxed execution environment")
        
        if results.get('secrets_detected'):
            suggestions.append("Use environment variables for sensitive configuration")
            suggestions.append("Consider using a secrets management service")
            suggestions.append("Never commit credentials to version control")
        
        if results.get('high_complexity'):
            suggestions.append("Refactor complex functions into smaller, focused functions")
            suggestions.append("Consider extracting nested logic into separate methods")
            suggestions.append("Simplify conditional logic using early returns")
        
        if results.get('documentation_issues'):
            suggestions.append("Add comprehensive documentation to all modules")
            suggestions.append("Include @fileoverview, @author, and other required headers")
            suggestions.append("Document all public methods and classes")
        
        if not suggestions:
            suggestions.append("Code looks good! No immediate improvements needed")
        
        return suggestions
    
    def get_severity_level(self, results: Dict[str, Any]) -> Optional[str]:
        """
        Calculate severity level from results
        
        @param results Rule application results
        @returns Severity level or None
        """
        if results.get('dangerous_patterns'):
            return 'critical'
        
        if results.get('secrets_detected'):
            return 'high'
        
        if results.get('high_complexity'):
            return 'medium'
        
        if results.get('documentation_issues'):
            return 'low'
        
        return None
    
    def enhance_evaluation(self, context, basic_result):
        """
        Enhance basic evaluation with smart analysis
        
        @param context Evaluation context
        @param basic_result Basic evaluation result
        @returns Enhanced result
        """
        risk_score = self.smart_rules.calculate_risk_score(context)
        
        # Add risk analysis to result
        if not hasattr(basic_result, 'metadata'):
            basic_result.metadata = {}
        
        # Ensure warnings and recommendations exist
        if not hasattr(basic_result, 'warnings'):
            basic_result.warnings = []
        if not hasattr(basic_result, 'recommendations'):
            basic_result.recommendations = []
        
        basic_result.metadata['risk_score'] = risk_score
        basic_result.metadata['is_risky_time'] = self.smart_rules.is_risky_time()
        
        # Check for dangerous patterns
        if hasattr(context, 'payload'):
            dangerous = self.smart_rules.contains_dangerous_patterns({'content': str(context.payload)})
            if dangerous:
                basic_result.metadata['dangerous_patterns'] = dangerous
                if not basic_result.warnings:
                    basic_result.warnings = []
                basic_result.warnings.append(f"Dangerous patterns detected")
            
            secrets = self.smart_rules.check_for_secrets({'content': str(context.payload)})
            if secrets:
                basic_result.metadata['potential_secrets'] = True
                # Override to reject if secrets found
                basic_result.decision = "rejected"
                basic_result.reason = "Potential secrets detected in payload"
        
        # Adjust confidence based on risk
        if risk_score > 0.7:
            basic_result.confidence *= 0.5  # Lower confidence for high-risk operations
        
        # Add recommendations based on time
        if self.smart_rules.is_friday_afternoon():
            if not basic_result.recommendations:
                basic_result.recommendations = []
            basic_result.recommendations.append("Consider waiting until Monday - it's Friday afternoon")
        
        return basic_result