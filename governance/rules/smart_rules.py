"""
Smart Rules Module
Intelligent rules based on patterns, time, and context
"""

from datetime import datetime
import re
from typing import Dict, Any, List


class SmartRules:
    """
    Smart rules that analyze context for risk patterns
    """
    
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
    
    @staticmethod
    def contains_dangerous_patterns(payload: Dict[str, Any]) -> List[str]:
        """
        Check for dangerous patterns in payload
        Returns list of found patterns
        """
        dangerous_patterns = [
            'force', 'skip', 'bypass', 'disable', 
            'remove_test', 'delete_test', 'skip_test',
            'todo_hack', 'fixme_later', 'temporary_workaround',
            'quick_fix', 'will_fix_later', 'ignore_error',
            'suppress_warning', 'disable_validation'
        ]
        
        payload_str = str(payload).lower()
        found_patterns = []
        
        for pattern in dangerous_patterns:
            if pattern in payload_str:
                found_patterns.append(pattern)
        
        return found_patterns
    
    @staticmethod
    def check_for_secrets(payload: Dict[str, Any]) -> List[str]:
        """
        Check for potential secrets in payload
        """
        secret_patterns = [
            r'password\s*=\s*["\'].*["\']',
            r'api[_-]?key\s*=\s*["\'].*["\']',
            r'secret\s*=\s*["\'].*["\']',
            r'token\s*=\s*["\'].*["\']',
            r'[a-zA-Z0-9]{40}',  # SHA1 like tokens
            r'[A-Z0-9]{20,}',    # AWS style keys
        ]
        
        payload_str = str(payload)
        found_secrets = []
        
        for pattern in secret_patterns:
            if re.search(pattern, payload_str, re.IGNORECASE):
                found_secrets.append(pattern)
        
        # Also check for obvious secret words
        secret_words = ['password', 'pwd', 'secret', 'key', 'token', 'credential']
        for word in secret_words:
            if word in payload_str.lower() and word not in found_secrets:
                found_secrets.append(word)
        
        return found_secrets
    
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
    Enhances basic rules with smart analysis
    """
    
    def __init__(self):
        self.smart_rules = SmartRules()
    
    def enhance_evaluation(self, context, basic_result):
        """
        Enhance basic evaluation with smart analysis
        """
        risk_score = self.smart_rules.calculate_risk_score(context)
        
        # Add risk analysis to result
        if not hasattr(basic_result, 'metadata'):
            basic_result.metadata = {}
        
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