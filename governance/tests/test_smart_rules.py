#!/usr/bin/env python3
"""
@fileoverview Unit tests for smart rules and rule enhancement
@author Dr. Sarah Chen v1.2 - 2025-01-28
@architecture Testing - Unit tests for smart rules
@responsibility Validate intelligent rule application
@dependencies pytest, unittest, re
@integration_points Tests smart_rules module
@testing_strategy Full coverage of rule patterns and enhancement
@governance Test file following governance requirements

Business Logic Summary:
- Test dangerous pattern detection
- Test secret detection
- Test rule enhancement

Architecture Integration:
- Part of governance test suite
- Validates security rules
- Tests pattern matching
"""

import pytest
import unittest
from unittest.mock import Mock, patch
from pathlib import Path
import sys

# Add governance module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from governance.rules.smart_rules import SmartRules, RuleEnhancer


class TestSmartRules(unittest.TestCase):
    """
    @class TestSmartRules
    @description Test smart rule application
    @architecture_role Validate rule pattern matching
    @business_logic Test security and quality rules
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.smart_rules = SmartRules()
    
    def test_contains_dangerous_patterns_eval(self):
        """Test detection of eval patterns"""
        dangerous_code = {
            'content': 'result = eval(user_input)'
        }
        
        self.assertTrue(
            self.smart_rules.contains_dangerous_patterns(dangerous_code)
        )
    
    def test_contains_dangerous_patterns_exec(self):
        """Test detection of exec patterns"""
        dangerous_code = {
            'content': 'exec(f"print({variable})")'
        }
        
        self.assertTrue(
            self.smart_rules.contains_dangerous_patterns(dangerous_code)
        )
    
    def test_contains_dangerous_patterns_import(self):
        """Test detection of __import__ patterns"""
        dangerous_code = {
            'content': 'module = __import__(user_module)'
        }
        
        self.assertTrue(
            self.smart_rules.contains_dangerous_patterns(dangerous_code)
        )
    
    def test_safe_code_no_dangerous_patterns(self):
        """Test safe code passes dangerous pattern check"""
        safe_code = {
            'content': '''
def safe_function():
    """Safe function with no dangerous patterns"""
    return "Hello, World!"
'''
        }
        
        self.assertFalse(
            self.smart_rules.contains_dangerous_patterns(safe_code)
        )
    
    def test_check_for_secrets_api_key(self):
        """Test detection of API keys"""
        code_with_secret = {
            'content': 'api_key = "sk-1234567890abcdef"'
        }
        
        self.assertTrue(
            self.smart_rules.check_for_secrets(code_with_secret)
        )
    
    def test_check_for_secrets_password(self):
        """Test detection of passwords"""
        code_with_secret = {
            'content': 'password = "super_secret_123"'
        }
        
        self.assertTrue(
            self.smart_rules.check_for_secrets(code_with_secret)
        )
    
    def test_check_for_secrets_token(self):
        """Test detection of tokens"""
        code_with_secret = {
            'content': 'auth_token = "ghp_abcdefghijklmnopqrstuvwxyz"'
        }
        
        self.assertTrue(
            self.smart_rules.check_for_secrets(code_with_secret)
        )
    
    def test_check_for_secrets_environment_var(self):
        """Test environment variables are allowed"""
        safe_code = {
            'content': 'api_key = os.environ.get("API_KEY")'
        }
        
        self.assertFalse(
            self.smart_rules.check_for_secrets(safe_code)
        )
    
    def test_check_complexity_high(self):
        """Test detection of high complexity"""
        complex_code = {
            'content': '''
def complex_function(a, b, c, d, e):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        for i in range(10):
                            for j in range(10):
                                if i == j:
                                    return True
    return False
'''
        }
        
        result = self.smart_rules.check_complexity(complex_code)
        self.assertTrue(result)  # Should detect high complexity
    
    def test_check_complexity_acceptable(self):
        """Test acceptable complexity passes"""
        simple_code = {
            'content': '''
def simple_function(value):
    if value > 0:
        return value * 2
    return 0
'''
        }
        
        result = self.smart_rules.check_complexity(simple_code)
        self.assertFalse(result)  # Should not detect high complexity
    
    def test_validate_documentation_missing(self):
        """Test detection of missing documentation"""
        code = {
            'content': '''
def undocumented_function():
    return 42
''',
            'path': 'test.py'
        }
        
        issues = self.smart_rules.validate_documentation(code)
        self.assertIsNotNone(issues)
        self.assertIn('missing', issues.lower())
    
    def test_validate_documentation_present(self):
        """Test proper documentation passes"""
        code = {
            'content': '''
"""
@fileoverview Test module
@author Test Author
"""

def documented_function():
    """This function is documented"""
    return 42
''',
            'path': 'test.py'
        }
        
        issues = self.smart_rules.validate_documentation(code)
        self.assertIsNone(issues)
    
    def test_apply_rules_all_checks(self):
        """Test applying all rules to code"""
        code_context = {
            'content': '''
"""
@fileoverview Good file
@author Test
"""

def safe_function():
    """Safe documented function"""
    return "safe"
''',
            'path': 'safe.py'
        }
        
        results = self.smart_rules.apply_rules(code_context)
        
        self.assertIn('dangerous_patterns', results)
        self.assertIn('secrets_detected', results)
        self.assertIn('high_complexity', results)
        self.assertIn('documentation_issues', results)
        
        # Should pass all checks
        self.assertFalse(results['dangerous_patterns'])
        self.assertFalse(results['secrets_detected'])
        self.assertFalse(results['high_complexity'])
        self.assertIsNone(results['documentation_issues'])


class TestRuleEnhancer(unittest.TestCase):
    """
    @class TestRuleEnhancer
    @description Test rule enhancement system
    @architecture_role Validate rule improvement
    @business_logic Test context-aware rule enhancement
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.enhancer = RuleEnhancer()
    
    def test_enhance_rule_documentation(self):
        """Test enhancing documentation rules"""
        rule = {
            'id': 'documentation',
            'severity': 'warning'
        }
        
        context = {
            'files': ['critical_system.py'],
            'user': 'test_user',
            'branch': 'main'
        }
        
        enhanced = self.enhancer.enhance_rule(rule, context)
        
        self.assertIsNotNone(enhanced)
        self.assertIn('enhanced', enhanced)
        self.assertTrue(enhanced['enhanced'])
    
    def test_suggest_improvements_dangerous_code(self):
        """Test improvement suggestions for dangerous code"""
        results = {
            'dangerous_patterns': True,
            'pattern_details': 'eval() detected'
        }
        
        improvements = self.enhancer.suggest_improvements(results)
        
        self.assertIsNotNone(improvements)
        self.assertIsInstance(improvements, list)
        self.assertTrue(len(improvements) > 0)
        
        # Should suggest safer alternatives
        suggestion_text = ' '.join(improvements).lower()
        self.assertIn('eval', suggestion_text)
    
    def test_suggest_improvements_secrets(self):
        """Test improvement suggestions for secrets"""
        results = {
            'secrets_detected': True,
            'secret_type': 'api_key'
        }
        
        improvements = self.enhancer.suggest_improvements(results)
        
        self.assertIsNotNone(improvements)
        
        # Should suggest environment variables
        suggestion_text = ' '.join(improvements).lower()
        self.assertIn('environment', suggestion_text)
    
    def test_suggest_improvements_complexity(self):
        """Test improvement suggestions for complexity"""
        results = {
            'high_complexity': True,
            'complexity_score': 15
        }
        
        improvements = self.enhancer.suggest_improvements(results)
        
        self.assertIsNotNone(improvements)
        
        # Should suggest refactoring
        suggestion_text = ' '.join(improvements).lower()
        self.assertTrue(
            'refactor' in suggestion_text or 
            'simplify' in suggestion_text
        )
    
    def test_suggest_improvements_documentation(self):
        """Test improvement suggestions for documentation"""
        results = {
            'documentation_issues': 'Missing @fileoverview'
        }
        
        improvements = self.enhancer.suggest_improvements(results)
        
        self.assertIsNotNone(improvements)
        
        # Should suggest adding documentation
        suggestion_text = ' '.join(improvements).lower()
        self.assertIn('documentation', suggestion_text)
    
    def test_suggest_improvements_clean_code(self):
        """Test no improvements needed for clean code"""
        results = {
            'dangerous_patterns': False,
            'secrets_detected': False,
            'high_complexity': False,
            'documentation_issues': None
        }
        
        improvements = self.enhancer.suggest_improvements(results)
        
        self.assertIsNotNone(improvements)
        self.assertEqual(len(improvements), 1)
        self.assertIn('looks good', improvements[0].lower())
    
    def test_get_severity_level(self):
        """Test severity level calculation"""
        # Critical - dangerous patterns
        results = {'dangerous_patterns': True}
        self.assertEqual(
            self.enhancer.get_severity_level(results),
            'critical'
        )
        
        # High - secrets detected
        results = {'dangerous_patterns': False, 'secrets_detected': True}
        self.assertEqual(
            self.enhancer.get_severity_level(results),
            'high'
        )
        
        # Medium - complexity issues
        results = {
            'dangerous_patterns': False,
            'secrets_detected': False,
            'high_complexity': True
        }
        self.assertEqual(
            self.enhancer.get_severity_level(results),
            'medium'
        )
        
        # Low - documentation issues
        results = {
            'dangerous_patterns': False,
            'secrets_detected': False,
            'high_complexity': False,
            'documentation_issues': 'minor'
        }
        self.assertEqual(
            self.enhancer.get_severity_level(results),
            'low'
        )
        
        # None - all good
        results = {
            'dangerous_patterns': False,
            'secrets_detected': False,
            'high_complexity': False,
            'documentation_issues': None
        }
        self.assertIsNone(
            self.enhancer.get_severity_level(results)
        )


class TestSmartRulesIntegration(unittest.TestCase):
    """
    @class TestSmartRulesIntegration
    @description Integration tests for smart rules
    @architecture_role Test rule system integration
    @business_logic Validate end-to-end rule application
    """
    
    def test_full_validation_flow(self):
        """Test complete validation flow"""
        smart_rules = SmartRules()
        enhancer = RuleEnhancer()
        
        # Bad code example
        bad_code = {
            'content': '''
password = "hardcoded_password_123"
result = eval(user_input)

def complex_mess(a, b, c, d, e, f):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        if f:
                            return eval(str(a))
    return None
''',
            'path': 'bad_code.py'
        }
        
        # Apply rules
        results = smart_rules.apply_rules(bad_code)
        
        # Should detect all issues
        self.assertTrue(results['dangerous_patterns'])
        self.assertTrue(results['secrets_detected'])
        self.assertTrue(results['high_complexity'])
        self.assertIsNotNone(results['documentation_issues'])
        
        # Get suggestions
        improvements = enhancer.suggest_improvements(results)
        self.assertTrue(len(improvements) > 0)
        
        # Get severity
        severity = enhancer.get_severity_level(results)
        self.assertEqual(severity, 'critical')
    
    def test_good_code_validation(self):
        """Test validation of good code"""
        smart_rules = SmartRules()
        enhancer = RuleEnhancer()
        
        # Good code example
        good_code = {
            'content': '''
"""
@fileoverview Example of good code
@author Test Developer
@architecture Backend component
@responsibility Data processing
"""

import os
from typing import Optional

# Get config from environment
API_KEY = os.environ.get('API_KEY')


def process_data(data: dict) -> Optional[dict]:
    """
    Process data safely
    
    @param data Input data dictionary
    @returns Processed data or None
    """
    if not data:
        return None
    
    # Simple processing
    result = {
        'processed': True,
        'count': len(data)
    }
    
    return result
''',
            'path': 'good_code.py'
        }
        
        # Apply rules
        results = smart_rules.apply_rules(good_code)
        
        # Should pass all checks
        self.assertFalse(results['dangerous_patterns'])
        self.assertFalse(results['secrets_detected'])
        self.assertFalse(results['high_complexity'])
        self.assertIsNone(results['documentation_issues'])
        
        # Get suggestions
        improvements = enhancer.suggest_improvements(results)
        self.assertEqual(len(improvements), 1)
        self.assertIn('looks good', improvements[0].lower())
        
        # Get severity
        severity = enhancer.get_severity_level(results)
        self.assertIsNone(severity)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])