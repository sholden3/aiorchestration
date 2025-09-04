#!/usr/bin/env python3
"""
Unified Documentation Validator

Uses the documentation_standards.yaml configuration for all validation.
Replaces separate validators with a single configurable system.

Author: Isabella Martinez & Marcus Thompson
Created: 2025-09-03
Version: 1.0.0
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import sys

# Add parent directories to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "core"))

# Direct imports
try:
    from template_renderer import DocumentTemplateRenderer
    from exemption_manager import ExemptionManager
except ImportError:
    # Fallback if direct import fails
    from core.template_renderer import DocumentTemplateRenderer
    from core.exemption_manager import ExemptionManager


@dataclass
class ValidationResult:
    """Result of document validation"""
    valid: bool
    score: float
    issues: List[str]
    warnings: List[str]
    exemptions: List[str]
    metadata: Dict[str, Any]


class UnifiedDocumentValidator:
    """
    Unified validator for all documentation types.
    
    Features:
    - Configuration-driven validation
    - Exemption support
    - Template-based structure checking
    - UI-manageable rules
    - Comprehensive scoring
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the unified validator.
        
        Args:
            config_path: Path to documentation standards YAML
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "documentation_standards.yaml"
        
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize sub-components
        self.template_renderer = DocumentTemplateRenderer(config_path)
        self.exemption_manager = ExemptionManager(Path(__file__).parent.parent / "config.yaml")
        
        # Cache compiled patterns
        self._compile_patterns()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load documentation standards configuration."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for performance."""
        self.patterns = {
            'heading': re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE),
            'code_fence': re.compile(r'^```(\w*)?$', re.MULTILINE),
            'date': re.compile(r'\d{4}-\d{2}-\d{2}'),
            'timestamp': re.compile(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+UTC')
        }
    
    def validate_file(self, file_path: Path) -> ValidationResult:
        """
        Validate a documentation file.
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            ValidationResult with details
        """
        # Determine document type
        doc_type = self._determine_document_type(file_path)
        
        # Check if file is exempt
        exemptions = self._check_exemptions(file_path, doc_type)
        if exemptions and 'fully_exempt' in exemptions:
            return ValidationResult(
                valid=True,
                score=100.0,
                issues=[],
                warnings=[],
                exemptions=exemptions,
                metadata={'document_type': doc_type, 'fully_exempt': True}
            )
        
        # Read file content
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return ValidationResult(
                valid=False,
                score=0.0,
                issues=[f"Cannot read file: {e}"],
                warnings=[],
                exemptions=[],
                metadata={'error': str(e)}
            )
        
        # Perform validation
        if doc_type:
            return self._validate_structured_document(content, doc_type, exemptions)
        else:
            return self._validate_generic_document(content, file_path)
    
    def _determine_document_type(self, file_path: Path) -> Optional[str]:
        """
        Determine the type of document based on filename.
        
        Args:
            file_path: Path to file
            
        Returns:
            Document type or None
        """
        filename = file_path.name
        
        for doc_type, config in self.config.get('document_types', {}).items():
            pattern = config.get('file_pattern', '')
            if pattern and filename == pattern:
                return doc_type
        
        return None
    
    def _check_exemptions(self, file_path: Path, doc_type: str) -> List[str]:
        """
        Check for exemptions for this file.
        
        Args:
            file_path: Path to file
            doc_type: Type of document
            
        Returns:
            List of exemptions
        """
        exemptions = []
        
        # Check file-level exemptions
        if self.exemption_manager.is_exempt(str(file_path), 'documentation_validation'):
            exemptions.append('fully_exempt')
            return exemptions
        
        # Check section exemptions if it's a README
        if doc_type == 'README':
            # Use the parent directory for README exemptions
            parent_dir = file_path.parent
            
            # Check with our custom exemption system
            from pathlib import Path
            import sys
            sys.path.append(str(Path(__file__).parent.parent / "core"))
            
            try:
                from exemption_manager import DocumentationExemptionManager
                doc_exemption_mgr = DocumentationExemptionManager(self.config_path)
                
                required, reason = doc_exemption_mgr.is_readme_required(str(parent_dir))
                if not required:
                    exemptions.append('fully_exempt')
                    exemptions.append(reason)
                else:
                    # Check for section exemptions
                    exempt_sections = doc_exemption_mgr.get_exempt_sections(str(parent_dir))
                    if exempt_sections:
                        exemptions.extend([f"section:{s}" for s in exempt_sections])
            except:
                pass  # Fallback if new exemption system not available
        
        return exemptions
    
    def _validate_structured_document(self, 
                                    content: str, 
                                    doc_type: str, 
                                    exemptions: List[str]) -> ValidationResult:
        """
        Validate a structured document against its template.
        
        Args:
            content: Document content
            doc_type: Type of document
            exemptions: List of exemptions
            
        Returns:
            ValidationResult
        """
        issues = []
        warnings = []
        scores = {}
        
        # Get document structure
        structure = self.template_renderer.get_document_structure(doc_type)
        if not structure:
            return ValidationResult(
                valid=False,
                score=0.0,
                issues=[f"Unknown document type: {doc_type}"],
                warnings=[],
                exemptions=exemptions,
                metadata={'document_type': doc_type}
            )
        
        # Check required sections
        total_weight = 0
        achieved_weight = 0
        
        for section in structure['sections']:
            section_name = section['name']
            section_weight = section['weight']
            total_weight += section_weight
            
            # Check if section is exempt
            if f"section:{section_name}" in exemptions:
                achieved_weight += section_weight  # Give full credit for exempt sections
                continue
            
            # Check if section exists
            section_pattern = f"#{{1,6}}\\s+{re.escape(section_name)}"
            if re.search(section_pattern, content, re.IGNORECASE):
                # Section found
                section_score = self._validate_section_content(
                    content, 
                    section_name, 
                    section.get('validation', {})
                )
                achieved_weight += section_weight * section_score
                
                if section_score < 1.0:
                    warnings.append(f"Section '{section_name}' partially valid (score: {section_score:.2f})")
            else:
                if section['required']:
                    issues.append(f"Missing required section: {section_name}")
                else:
                    warnings.append(f"Missing optional section: {section_name}")
        
        # Calculate final score
        score = (achieved_weight / total_weight * 100) if total_weight > 0 else 0
        
        # Check against thresholds
        pass_threshold = self.config.get('validation_rules', {}).get('scoring', {}).get('pass_threshold', 70)
        warning_threshold = self.config.get('validation_rules', {}).get('scoring', {}).get('warning_threshold', 85)
        
        if score < pass_threshold:
            issues.append(f"Score {score:.1f}% is below pass threshold {pass_threshold}%")
        elif score < warning_threshold:
            warnings.append(f"Score {score:.1f}% is below warning threshold {warning_threshold}%")
        
        return ValidationResult(
            valid=score >= pass_threshold,
            score=score,
            issues=issues,
            warnings=warnings,
            exemptions=exemptions,
            metadata={
                'document_type': doc_type,
                'total_weight': total_weight,
                'achieved_weight': achieved_weight
            }
        )
    
    def _validate_section_content(self, 
                                 content: str, 
                                 section_name: str, 
                                 validation_rules: Dict) -> float:
        """
        Validate content of a specific section.
        
        Args:
            content: Full document content
            section_name: Name of section to validate
            validation_rules: Rules for this section
            
        Returns:
            Score between 0 and 1
        """
        # Extract section content (simplified)
        section_pattern = f"#{{1,6}}\\s+{re.escape(section_name)}\\s*\n(.*?)(?=^#{{1,6}}\\s|\\Z)"
        match = re.search(section_pattern, content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        
        if not match:
            return 0.0
        
        section_content = match.group(1)
        
        # Apply validation rules
        score = 1.0
        
        # Check word count
        words = len(section_content.split())
        min_words = validation_rules.get('min_words', 0)
        max_words = validation_rules.get('max_words', float('inf'))
        
        if words < min_words:
            score *= (words / min_words) if min_words > 0 else 0
        elif words > max_words:
            score *= 0.8  # Penalty for being too verbose
        
        return score
    
    def _validate_generic_document(self, content: str, file_path: Path) -> ValidationResult:
        """
        Validate a generic markdown document.
        
        Args:
            content: Document content
            file_path: Path to file
            
        Returns:
            ValidationResult
        """
        issues = []
        warnings = []
        
        # Basic markdown validation
        rules = self.config.get('validation_rules', {}).get('markdown', {})
        
        # Check heading hierarchy
        if rules.get('heading_hierarchy', True):
            hierarchy_issues = self._check_heading_hierarchy(content)
            issues.extend(hierarchy_issues)
        
        # Check line length
        max_line_length = rules.get('max_line_length', 120)
        for i, line in enumerate(content.split('\n'), 1):
            if len(line) > max_line_length:
                warnings.append(f"Line {i} exceeds {max_line_length} characters")
        
        # Check code fence language
        if rules.get('require_code_fence_language', True):
            fences = self.patterns['code_fence'].findall(content)
            for i, fence_lang in enumerate(fences):
                if not fence_lang:
                    warnings.append(f"Code fence #{i+1} missing language identifier")
        
        # Calculate score
        total_checks = 3
        passed_checks = total_checks - len(issues)
        score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        return ValidationResult(
            valid=len(issues) == 0,
            score=score,
            issues=issues,
            warnings=warnings,
            exemptions=[],
            metadata={'file': str(file_path)}
        )
    
    def _check_heading_hierarchy(self, content: str) -> List[str]:
        """
        Check if heading hierarchy is valid.
        
        Args:
            content: Document content
            
        Returns:
            List of issues
        """
        issues = []
        headings = self.patterns['heading'].findall(content)
        
        if not headings:
            return issues
        
        # Check first heading is h1
        if len(headings[0][0]) != 1:
            issues.append("Document should start with # (h1) heading")
        
        # Check hierarchy
        prev_level = 0
        for hashes, title in headings:
            level = len(hashes)
            if level > prev_level + 1 and prev_level > 0:
                issues.append(f"Heading hierarchy broken at '{title}' (h{level} after h{prev_level})")
            prev_level = level
        
        return issues
    
    def get_validation_report(self, directory: Path) -> Dict[str, Any]:
        """
        Generate validation report for a directory.
        
        Args:
            directory: Directory to validate
            
        Returns:
            Validation report
        """
        results = {}
        total_score = 0
        file_count = 0
        
        # Find all markdown files
        for md_file in directory.rglob('*.md'):
            # Skip exempted directories
            if any(part.startswith('.') for part in md_file.parts):
                continue
            
            result = self.validate_file(md_file)
            results[str(md_file)] = {
                'valid': result.valid,
                'score': result.score,
                'issues': result.issues,
                'warnings': result.warnings,
                'exemptions': result.exemptions
            }
            
            total_score += result.score
            file_count += 1
        
        average_score = (total_score / file_count) if file_count > 0 else 0
        
        return {
            'summary': {
                'files_checked': file_count,
                'average_score': average_score,
                'pass_rate': sum(1 for r in results.values() if r['valid']) / file_count if file_count > 0 else 0
            },
            'results': results
        }


def main():
    """CLI interface for the validator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Unified Documentation Validator')
    parser.add_argument('path', help='Path to file or directory to validate')
    parser.add_argument('--config', help='Path to documentation standards YAML')
    parser.add_argument('--report', action='store_true', help='Generate full report')
    
    args = parser.parse_args()
    
    # Initialize validator
    config_path = Path(args.config) if args.config else None
    validator = UnifiedDocumentValidator(config_path)
    
    path = Path(args.path)
    
    if path.is_file():
        # Validate single file
        result = validator.validate_file(path)
        
        print(f"Validation Result for {path}:")
        print(f"  Valid: {'[PASS]' if result.valid else '[FAIL]'}")
        print(f"  Score: {result.score:.1f}%")
        
        if result.issues:
            print("\nIssues:")
            for issue in result.issues:
                print(f"  [X] {issue}")
        
        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings:
                print(f"  [!] {warning}")
        
        if result.exemptions:
            print("\nExemptions:")
            for exemption in result.exemptions:
                print(f"  [i] {exemption}")
        
        sys.exit(0 if result.valid else 1)
    
    elif path.is_dir():
        # Validate directory
        if args.report:
            report = validator.get_validation_report(path)
            
            print("Documentation Validation Report")
            print("=" * 50)
            print(f"Files Checked: {report['summary']['files_checked']}")
            print(f"Average Score: {report['summary']['average_score']:.1f}%")
            print(f"Pass Rate: {report['summary']['pass_rate']*100:.1f}%")
            
            print("\nDetails:")
            for file_path, result in report['results'].items():
                status = '[PASS]' if result['valid'] else '[FAIL]'
                print(f"\n{status} {file_path} (Score: {result['score']:.1f}%)")
                
                if result['issues']:
                    for issue in result['issues']:
                        print(f"    [X] {issue}")
                
                if result['warnings']:
                    for warning in result['warnings']:
                        print(f"    [!] {warning}")
        else:
            print("Use --report flag to generate full report for directories")
    else:
        print(f"Error: {path} not found")
        sys.exit(1)


if __name__ == "__main__":
    main()