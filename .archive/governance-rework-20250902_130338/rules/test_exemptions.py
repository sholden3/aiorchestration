#!/usr/bin/env python3
"""
@fileoverview Test exemption rules for governance validation
@author Dr. Sarah Chen v1.2 - 2025-01-28
@architecture Backend - Test exemption engine
@responsibility Manage exemptions for test code validation
@dependencies re, typing
@integration_points Used by governance hooks for test file validation
@testing_strategy Unit tests for exemption logic
@governance Smart exemption handling for test files

Business Logic Summary:
- Identify test files and test code
- Allow dangerous patterns in test contexts
- Maintain security for non-test code

Architecture Integration:
- Part of governance validation pipeline
- Works with smart rules
- Provides context-aware validation
"""

import re
from typing import Dict, Any, List, Tuple, Optional


class TestExemptionRules:
    """
    @class TestExemptionRules
    @description Manages exemptions for test code
    @architecture_role Provide smart test exemptions
    @business_logic Allow test patterns while maintaining security
    """
    
    def __init__(self):
        """Initialize test exemption rules"""
        self.test_file_patterns = [
            r'test_.*\.py$',
            r'.*_test\.py$',
            r'.*\.test\.[jt]s$',
            r'.*\.spec\.[jt]s$',
            r'tests?/',
            r'__tests__/',
            r'spec/'
        ]
        
        self.test_metadata_markers = [
            '@testing_strategy',
            '@test',
            '@unittest',
            '@pytest',
            'class Test',
            'def test_',
            'describe(',
            'it(',
            'test(',
            'expect('
        ]
        
        self.allowed_in_tests = [
            'eval',
            'exec',
            '__import__',
            'compile',
            'globals',
            'locals',
            'setattr',
            'delattr'
        ]
    
    def is_test_file(self, file_path: str) -> bool:
        """
        Check if file is a test file
        
        @param file_path Path to check
        @returns True if test file
        """
        file_path_lower = file_path.lower()
        
        for pattern in self.test_file_patterns:
            if re.search(pattern, file_path_lower):
                return True
        
        return False
    
    def has_test_metadata(self, content: str) -> bool:
        """
        Check if content has test metadata
        
        @param content File content
        @returns True if has test markers
        """
        for marker in self.test_metadata_markers:
            if marker in content:
                return True
        
        return False
    
    def get_exemption_context(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Get exemption context for file
        
        @param file_path File path
        @param content File content
        @returns Exemption context
        """
        context = {
            'is_test_file': self.is_test_file(file_path),
            'has_test_metadata': self.has_test_metadata(content),
            'file_type': self._get_file_type(file_path),
            'exemptions': []
        }
        
        # If it's a test file with proper metadata, allow dangerous patterns
        if context['is_test_file'] and context['has_test_metadata']:
            context['exemptions'] = self.allowed_in_tests
            context['exemption_reason'] = 'Test file with proper metadata'
        elif context['is_test_file']:
            context['exemption_reason'] = 'Test file (metadata recommended)'
        else:
            context['exemption_reason'] = None
        
        return context
    
    def _get_file_type(self, file_path: str) -> str:
        """Get file type from extension"""
        if file_path.endswith('.py'):
            return 'python'
        elif file_path.endswith('.ts'):
            return 'typescript'
        elif file_path.endswith('.js'):
            return 'javascript'
        else:
            return 'unknown'
    
    def validate_test_patterns(
        self, 
        file_path: str, 
        content: str, 
        patterns: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if patterns are allowed in file
        
        @param file_path File path
        @param content File content
        @param patterns Patterns found
        @returns (is_valid, error_message)
        """
        context = self.get_exemption_context(file_path, content)
        
        # Check if all patterns are exempted
        non_exempted = [
            p for p in patterns 
            if p not in context.get('exemptions', [])
        ]
        
        if non_exempted and not context['is_test_file']:
            return False, f"Dangerous patterns in non-test file: {', '.join(non_exempted)}"
        
        if non_exempted and context['is_test_file'] and not context['has_test_metadata']:
            return False, f"Test file with dangerous patterns must have test metadata markers"
        
        return True, None
    
    def get_test_file_warnings(self, file_path: str, content: str) -> List[str]:
        """
        Get warnings for test files
        
        @param file_path File path
        @param content File content
        @returns List of warnings
        """
        warnings = []
        context = self.get_exemption_context(file_path, content)
        
        if context['is_test_file'] and not context['has_test_metadata']:
            warnings.append(
                f"{file_path}: Test file should include test metadata markers "
                f"(@testing_strategy, class Test*, def test_*, etc.)"
            )
        
        return warnings


class SmartExemptionEngine:
    """
    @class SmartExemptionEngine
    @description Smart exemption engine with context awareness
    @architecture_role Intelligent exemption management
    @business_logic Context-aware security validation
    """
    
    def __init__(self):
        """Initialize smart exemption engine"""
        self.test_rules = TestExemptionRules()
        
        # Additional context-aware exemptions
        self.context_exemptions = {
            'migration': ['DROP TABLE', 'ALTER TABLE'],
            'schema': ['CREATE TABLE', 'CREATE INDEX'],
            'fixture': ['INSERT INTO', 'DELETE FROM'],
            'mock': ['eval', 'exec']  # For mock implementations
        }
    
    def should_exempt(
        self, 
        file_path: str, 
        content: str, 
        violation_type: str,
        pattern: str
    ) -> Tuple[bool, str]:
        """
        Determine if violation should be exempted
        
        @param file_path File path
        @param content File content
        @param violation_type Type of violation
        @param pattern Pattern that triggered violation
        @returns (should_exempt, reason)
        """
        # Check test exemptions first
        context = self.test_rules.get_exemption_context(file_path, content)
        
        # Check if the pattern (or a simplified version) is in exemptions
        exemptions = context.get('exemptions', [])
        for exempted_pattern in exemptions:
            if exempted_pattern in pattern or pattern in exempted_pattern:
                return True, context['exemption_reason']
        
        # Check for context-based exemptions
        for context_type, allowed_patterns in self.context_exemptions.items():
            if context_type in file_path.lower():
                if any(allowed in pattern for allowed in allowed_patterns):
                    return True, f"Allowed in {context_type} context"
        
        # Check for explicit exemption comments
        exemption_pattern = rf'#\s*governance-exempt:\s*{re.escape(pattern)}'
        if re.search(exemption_pattern, content, re.IGNORECASE):
            return True, "Explicit exemption comment"
        
        return False, "No exemption found"
    
    def get_exemption_report(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate exemption report for files
        
        @param files List of file contexts
        @returns Exemption report
        """
        report = {
            'total_files': len(files),
            'test_files': 0,
            'exempted_files': 0,
            'exemptions_applied': [],
            'warnings': []
        }
        
        for file_context in files:
            file_path = file_context.get('path', '')
            content = file_context.get('content', '')
            
            if self.test_rules.is_test_file(file_path):
                report['test_files'] += 1
            
            context = self.test_rules.get_exemption_context(file_path, content)
            if context['exemptions']:
                report['exempted_files'] += 1
                report['exemptions_applied'].append({
                    'file': file_path,
                    'reason': context['exemption_reason'],
                    'exemptions': context['exemptions']
                })
            
            warnings = self.test_rules.get_test_file_warnings(file_path, content)
            if warnings:
                report['warnings'].extend(warnings)
        
        return report