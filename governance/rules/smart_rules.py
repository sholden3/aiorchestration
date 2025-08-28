#!/usr/bin/env python3
"""
@fileoverview Smart rules for intelligent governance validation
@author Dr. Sarah Chen v1.2 - 2025-01-28
@architecture Backend - Smart rule engine
@responsibility Apply intelligent context-aware validation rules
@dependencies datetime, re, typing
@integration_points Used by governance hooks for validation
@testing_strategy Unit tests for all rule patterns
@governance Core component of validation pipeline

Business Logic Summary:
- Detect dangerous code patterns
- Find potential secrets
- Analyze code complexity
- Validate documentation

Architecture Integration:
- Part of governance validation pipeline
- Used by pre-commit hooks
- Provides intelligent pattern matching
"""

from datetime import datetime
import re
from typing import Dict, Any, List, Optional


class SmartRules:
    """
    @class SmartRules
    @description Intelligent context-aware validation rules
    @architecture_role Pattern detection and validation
    @business_logic Security and quality enforcement
    """
    
    def __init__(self):
        """Initialize smart rules with patterns"""
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
        Check for dangerous patterns in code
        
        @param context Code context with 'content' key
        @returns True if dangerous patterns found
        """
        content = context.get('content', '')
        
        for pattern in self.dangerous_patterns:
            if re.search(pattern, content):
                return True
        
        return False
    
    def get_dangerous_patterns(self, context: Dict[str, Any]) -> List[str]:
        """
        Get list of dangerous patterns found in code
        
        @param context Code context with 'content' key
        @returns List of patterns found
        """
        content = context.get('content', '')
        found_patterns = []
        
        for pattern in self.dangerous_patterns:
            if re.search(pattern, content):
                # Extract the actual pattern name from regex
                pattern_name = pattern.replace(r'\s*\(', '').replace('\\', '')
                found_patterns.append(pattern_name)
        
        return found_patterns
    
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
        
        # Check for file-level documentation
        if path.endswith(('.py', '.ts', '.js')):
            if '@fileoverview' not in content and '"""' not in content[:200]:
                return f"Missing file documentation in {path}"
        
        return None
    
    def apply_rules(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply all rules to context
        
        @param context Code context
        @returns Results dictionary
        """
        return {
            'dangerous_patterns': self.contains_dangerous_patterns(context),
            'secrets_detected': self.check_for_secrets(context),
            'high_complexity': self.check_complexity(context),
            'documentation_issues': self.validate_documentation(context)
        }
    
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
        
        # Check payload for dangerous patterns
        if hasattr(context, 'payload'):
            dangerous = SmartRules.contains_dangerous_patterns(context.payload)
            if dangerous:
                risk_score += 0.1 * len(dangerous)
            
            secrets = SmartRules.check_for_secrets(context.payload)
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
            dangerous = self.smart_rules.contains_dangerous_patterns(context.payload)
            if dangerous:
                basic_result.metadata['dangerous_patterns'] = dangerous
                if not basic_result.warnings:
                    basic_result.warnings = []
                basic_result.warnings.append(f"Dangerous patterns detected: {', '.join(dangerous)}")
            
            secrets = self.smart_rules.check_for_secrets(context.payload)
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