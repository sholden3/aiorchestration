#!/usr/bin/env python
"""
Validation Rules for Documentation System
@description: Individual validation rule implementations for document checking
@author: Governance System v2.0
@version: 2.0.0
@dependencies: re, pathlib, typing, datetime
@exports: ValidationRule classes and registry
@testing: 0% (needs implementation)
@last_review: 2025-09-03
"""

import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RuleResult:
    """Result of applying a validation rule"""
    passed: bool
    message: str
    severity: str
    suggestions: List[str]
    auto_fixable: bool = False
    penalty_points: float = 0.0


class ValidationRule(ABC):
    """Abstract base class for validation rules"""
    
    def __init__(self, name: str, description: str, default_severity: str = "medium"):
        self.name = name
        self.description = description
        self.default_severity = default_severity
    
    @abstractmethod
    def validate(self, file_path: str, content: str, metadata: Dict[str, Any] = None) -> RuleResult:
        """
        Validate content against this rule
        
        Args:
            file_path: Path to the file being validated
            content: File content as string
            metadata: Document metadata from .meta.yaml file
            
        Returns:
            RuleResult with validation outcome
        """
        pass


class RequiredSectionsRule(ValidationRule):
    """Validates that required sections are present in the document"""
    
    def __init__(self):
        super().__init__(
            name="check_required_sections",
            description="Ensure all required sections are present",
            default_severity="high"
        )
    
    def validate(self, file_path: str, content: str, metadata: Dict[str, Any] = None) -> RuleResult:
        if not metadata or 'validation' not in metadata:
            return RuleResult(
                passed=True,
                message="No section requirements defined",
                severity="info",
                suggestions=[]
            )
        
        validation = metadata['validation']
        required_sections = validation.get('required_sections', [])
        
        if not required_sections:
            return RuleResult(
                passed=True,
                message="No required sections specified",
                severity="info",
                suggestions=[]
            )
        
        missing_sections = []
        
        for section_def in required_sections:
            if isinstance(section_def, str):
                section_name = section_def
                level = 2
            elif isinstance(section_def, dict):
                section_name = section_def.get('name', '')
                level = section_def.get('level', 2)
                if not section_def.get('required', True):
                    continue  # Skip optional sections
            else:
                continue
            
            # Create pattern for section header
            header_pattern = f"^{'#' * level}\\s+{re.escape(section_name)}"
            
            if not re.search(header_pattern, content, re.MULTILINE | re.IGNORECASE):
                missing_sections.append(f"{'#' * level} {section_name}")
        
        if missing_sections:
            return RuleResult(
                passed=False,
                message=f"Missing required sections: {', '.join([s.split(' ', 1)[1] for s in missing_sections])}",
                severity=self.default_severity,
                suggestions=[f"Add section: {section}" for section in missing_sections],
                penalty_points=len(missing_sections) * 3.0
            )
        
        return RuleResult(
            passed=True,
            message="All required sections present",
            severity="info",
            suggestions=[]
        )


class PlaceholderValidationRule(ValidationRule):
    """Validates that placeholders are filled correctly"""
    
    def __init__(self):
        super().__init__(
            name="check_placeholders",
            description="Validate that required placeholders are filled",
            default_severity="high"
        )
    
    def validate(self, file_path: str, content: str, metadata: Dict[str, Any] = None) -> RuleResult:
        # Find all unfilled placeholders [PLACEHOLDER_NAME]
        placeholder_pattern = r'\\[([A-Z_][A-Z0-9_]*)\\]'
        unfilled = re.findall(placeholder_pattern, content)
        
        if unfilled:
            unique_unfilled = list(set(unfilled))
            return RuleResult(
                passed=False,
                message=f"Unfilled placeholders: {', '.join(unique_unfilled)}",
                severity=self.default_severity,
                suggestions=[f"Fill placeholder [{p}] with appropriate value" for p in unique_unfilled],
                penalty_points=len(unique_unfilled) * 2.0
            )
        
        # If metadata defines specific placeholder requirements, validate formats
        if metadata and 'validation' in metadata:
            validation = metadata['validation']
            required_placeholders = validation.get('required_placeholders', [])
            
            format_violations = []
            for placeholder_def in required_placeholders:
                if isinstance(placeholder_def, dict):
                    name = placeholder_def.get('name', '')
                    format_pattern = placeholder_def.get('format')
                    
                    if format_pattern and name:
                        # Look for filled values of this placeholder
                        # This is more complex - would need to track filled values
                        # For now, skip format validation
                        pass
            
            if format_violations:
                return RuleResult(
                    passed=False,
                    message=f"Placeholder format violations: {', '.join(format_violations)}",
                    severity="medium",
                    suggestions=["Fix placeholder format according to requirements"],
                    penalty_points=len(format_violations) * 1.0
                )
        
        return RuleResult(
            passed=True,
            message="All placeholders are filled",
            severity="info",
            suggestions=[]
        )


class MetadataHeaderRule(ValidationRule):
    """Validates document metadata header format"""
    
    def __init__(self):
        super().__init__(
            name="check_metadata_header",
            description="Check document metadata header format",
            default_severity="medium"
        )
    
    def validate(self, file_path: str, content: str, metadata: Dict[str, Any] = None) -> RuleResult:
        lines = content.split('\\n')
        if len(lines) < 5:
            return RuleResult(
                passed=False,
                message="Document too short to contain metadata header",
                severity="low",
                suggestions=["Add document metadata at the top"],
                penalty_points=1.0
            )
        
        # Look for common metadata patterns in first 10 lines
        header_section = '\\n'.join(lines[:10]).lower()
        
        issues = []
        suggestions = []
        
        # Check for status indicator
        if 'status' not in header_section:
            issues.append("missing status")
            suggestions.append("Add status line (e.g., **Status**: Active)")
        
        # Check for last updated
        if 'updated' not in header_section and 'last' not in header_section:
            issues.append("missing update date")
            suggestions.append("Add last updated date")
        
        # Check for version (optional but recommended)
        if 'version' not in header_section and 'v' not in header_section:
            # This is just a suggestion, not a failure
            suggestions.append("Consider adding version information")
        
        if issues:
            return RuleResult(
                passed=False,
                message=f"Metadata header issues: {', '.join(issues)}",
                severity=self.default_severity,
                suggestions=suggestions,
                penalty_points=len(issues) * 1.5
            )
        
        return RuleResult(
            passed=True,
            message="Metadata header looks good",
            severity="info",
            suggestions=suggestions if suggestions else []
        )


class BasicStructureRule(ValidationRule):
    """Validates basic document structure"""
    
    def __init__(self):
        super().__init__(
            name="check_basic_structure",
            description="Basic markdown structure validation",
            default_severity="low"
        )
    
    def validate(self, file_path: str, content: str, metadata: Dict[str, Any] = None) -> RuleResult:
        lines = [line.strip() for line in content.split('\\n') if line.strip()]
        
        issues = []
        suggestions = []
        
        # Check minimum length
        if len(lines) < 3:
            issues.append("too short")
            suggestions.append("Add more content to the document")
        
        # Check for main title
        has_h1 = any(line.startswith('# ') for line in lines)
        if not has_h1:
            issues.append("missing main title")
            suggestions.append("Add a main title with # header")
        
        # Check for at least one section
        has_sections = any(line.startswith('## ') for line in lines)
        if not has_sections and len(lines) > 5:
            issues.append("no sections")
            suggestions.append("Add section headers with ## to organize content")
        
        # Check for empty content (just headers)
        non_header_lines = [line for line in lines if not line.startswith('#')]
        if len(non_header_lines) < 3:
            issues.append("mostly headers")
            suggestions.append("Add more descriptive content under headers")
        
        if issues:
            return RuleResult(
                passed=False,
                message=f"Structure issues: {', '.join(issues)}",
                severity=self.default_severity,
                suggestions=suggestions,
                penalty_points=len(issues) * 1.0
            )
        
        return RuleResult(
            passed=True,
            message="Document structure looks good",
            severity="info",
            suggestions=[]
        )


class MarkdownFormatRule(ValidationRule):
    """Validates markdown formatting standards"""
    
    def __init__(self):
        super().__init__(
            name="check_markdown_format",
            description="Markdown formatting standards",
            default_severity="low"
        )
    
    def validate(self, file_path: str, content: str, metadata: Dict[str, Any] = None) -> RuleResult:
        lines = content.split('\\n')
        issues = []
        suggestions = []
        
        for i, line in enumerate(lines, 1):
            # Check header spacing
            if line.strip().startswith('#') and not line.startswith('#'):
                # Headers without space after #
                if re.match(r'^#+[^\\s]', line.strip()):
                    issues.append(f"line {i}: header needs space")
                    suggestions.append(f"Line {i}: Add space after # in headers")
            
            # Check list formatting
            if re.match(r'^\\s*[-\\*\\+]\\S', line):
                issues.append(f"line {i}: list item needs space")
                suggestions.append(f"Line {i}: Add space after list marker")
            
            # Check excessive blank lines (more than 2 in a row)
            if i < len(lines) - 2:
                if (not line.strip() and 
                    not lines[i].strip() and 
                    not lines[i + 1].strip()):
                    issues.append(f"line {i}: too many blank lines")
                    suggestions.append(f"Line {i}: Remove excessive blank lines")
        
        # Limit reported issues
        if len(issues) > 10:
            issues = issues[:10]
            suggestions = suggestions[:10]
            suggestions.append("... and more formatting issues")
        
        if issues:
            return RuleResult(
                passed=False,
                message=f"Formatting issues found: {len(issues)}",
                severity=self.default_severity,
                suggestions=suggestions,
                penalty_points=min(len(issues) * 0.5, 5.0),  # Cap penalty
                auto_fixable=True
            )
        
        return RuleResult(
            passed=True,
            message="Markdown formatting looks good",
            severity="info",
            suggestions=[]
        )


class UpdateFrequencyRule(ValidationRule):
    """Validates document update frequency"""
    
    def __init__(self):
        super().__init__(
            name="check_update_frequency",
            description="Ensure documents are updated per schedule",
            default_severity="medium"
        )
    
    def validate(self, file_path: str, content: str, metadata: Dict[str, Any] = None) -> RuleResult:
        # This rule requires file system access to check modification times
        # For now, look for update frequency requirements in metadata
        
        if not metadata or 'validation' not in metadata:
            return RuleResult(
                passed=True,
                message="No update frequency requirements",
                severity="info",
                suggestions=[]
            )
        
        validation = metadata['validation']
        max_age_days = validation.get('max_age_days')
        
        if not max_age_days:
            return RuleResult(
                passed=True,
                message="No update frequency specified",
                severity="info",
                suggestions=[]
            )
        
        try:
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                mtime = datetime.fromtimestamp(file_path_obj.stat().st_mtime)
                age_days = (datetime.now() - mtime).days
                
                if age_days > max_age_days:
                    return RuleResult(
                        passed=False,
                        message=f"Document outdated: {age_days} days old (max: {max_age_days})",
                        severity=self.default_severity,
                        suggestions=[f"Update document content (last modified {age_days} days ago)"],
                        penalty_points=min(age_days - max_age_days, 10.0)
                    )
                elif age_days > max_age_days * 0.8:
                    return RuleResult(
                        passed=True,
                        message=f"Document approaching staleness: {age_days} days old",
                        severity="info",
                        suggestions=[f"Consider updating soon (will be stale in {max_age_days - age_days} days)"]
                    )
        except Exception as e:
            return RuleResult(
                passed=True,
                message=f"Could not check file age: {e}",
                severity="info",
                suggestions=[]
            )
        
        return RuleResult(
            passed=True,
            message="Document is current",
            severity="info",
            suggestions=[]
        )


# Rule registry for easy lookup
VALIDATION_RULES: Dict[str, ValidationRule] = {
    "check_required_sections": RequiredSectionsRule(),
    "check_placeholders": PlaceholderValidationRule(),
    "check_metadata_header": MetadataHeaderRule(),
    "check_basic_structure": BasicStructureRule(),
    "check_markdown_format": MarkdownFormatRule(),
    "check_update_frequency": UpdateFrequencyRule(),
}


def get_rule(rule_name: str) -> Optional[ValidationRule]:
    """Get a validation rule by name"""
    return VALIDATION_RULES.get(rule_name)


def list_available_rules() -> List[str]:
    """List all available validation rule names"""
    return list(VALIDATION_RULES.keys())


def validate_with_rule(rule_name: str, file_path: str, content: str, 
                      metadata: Dict[str, Any] = None) -> Optional[RuleResult]:
    """
    Apply a specific validation rule
    
    Args:
        rule_name: Name of the rule to apply
        file_path: Path to the file being validated
        content: File content
        metadata: Document metadata
        
    Returns:
        RuleResult if rule exists, None otherwise
    """
    rule = get_rule(rule_name)
    if rule:
        return rule.validate(file_path, content, metadata)
    return None