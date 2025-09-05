"""
Documentation Validator Module
Created: 2025-09-03
Purpose: Validate markdown documentation against defined standards
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import fnmatch


@dataclass
class ValidationResult:
    """Result of document validation"""
    file_path: str
    is_valid: bool
    score: float
    violations: List[Dict] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class DocumentationValidator:
    """Validates markdown documentation against defined standards"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize validator with configuration"""
        self.config_path = config_path or Path(".docs-metadata/validation-rules.yaml")
        self.config = self._load_config()
        self.enforcement_mode = self.config.get('global', {}).get('enforcement_mode', 'progressive')
        
    def _load_config(self) -> Dict:
        """Load validation configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration if file not found"""
        return {
            'global': {
                'enabled': True,
                'enforcement_mode': 'warnings_only',
                'common_requirements': [
                    'must_have_title',
                    'proper_markdown_syntax'
                ]
            },
            'scoring': {
                'pass_threshold': 0.7,
                'warning_threshold': 0.85,
                'excellent_threshold': 0.95
            }
        }
    
    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single documentation file"""
        result = ValidationResult(
            file_path=str(file_path),
            is_valid=True,
            score=1.0
        )
        
        # Check if file exists
        if not file_path.exists():
            result.is_valid = False
            result.score = 0.0
            result.violations.append({
                'type': 'file_not_found',
                'severity': 'critical',
                'message': f"File not found: {file_path}"
            })
            return result
        
        # Read file content
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            result.is_valid = False
            result.score = 0.0
            result.violations.append({
                'type': 'read_error',
                'severity': 'critical',
                'message': f"Error reading file: {e}"
            })
            return result
        
        # Determine document type
        doc_type = self._determine_doc_type(file_path)
        
        # Run validations
        self._validate_common_requirements(content, result)
        self._validate_structure(content, doc_type, result)
        self._validate_content(content, doc_type, result)
        self._validate_metadata(content, doc_type, result)
        self._validate_links(content, file_path, result)
        
        # Calculate final score
        result.score = self._calculate_score(result)
        result.is_valid = result.score >= self.config.get('scoring', {}).get('pass_threshold', 0.7)
        
        # Add suggestions based on score
        self._add_suggestions(result)
        
        return result
    
    def _determine_doc_type(self, file_path: Path) -> Optional[str]:
        """Determine document type based on path patterns"""
        doc_types = self.config.get('document_types', {})
        
        for doc_type, config in doc_types.items():
            pattern = config.get('path_pattern', '')
            if pattern and fnmatch.fnmatch(str(file_path), pattern):
                return doc_type
        
        return None
    
    def _validate_common_requirements(self, content: str, result: ValidationResult):
        """Validate common requirements for all documents"""
        requirements = self.config.get('global', {}).get('common_requirements', [])
        
        if 'must_have_title' in requirements:
            if not re.match(r'^#\s+.+', content, re.MULTILINE):
                result.violations.append({
                    'type': 'missing_title',
                    'severity': 'critical',
                    'message': 'Document must have a top-level title (# Title)',
                    'line': 1
                })
        
        if 'must_have_date' in requirements:
            date_patterns = [
                r'\*\*Last Updated\*\*:\s*\w+\s+\d{1,2},?\s+\d{4}',  # **Last Updated**: Sept 3, 2025
                r'\*\*Date\*\*:\s*\d{4}-\d{2}-\d{2}',
                r'\*\*Created\*\*:\s*\d{4}-\d{2}-\d{2}',
                r'Last Updated:\s*\w+\s+\d{1,2},?\s+\d{4}',  # Without bold
                r'\d{4}-\d{2}-\d{2}',  # Any ISO date format
                r'\w+\s+\d{1,2},?\s+\d{4}'  # Month DD, YYYY format anywhere
            ]
            if not any(re.search(pattern, content, re.IGNORECASE) for pattern in date_patterns):
                result.warnings.append('Document should include a date (Last Updated, Date, or Created)')
        
        if 'proper_markdown_syntax' in requirements:
            self._validate_markdown_syntax(content, result)
    
    def _validate_markdown_syntax(self, content: str, result: ValidationResult):
        """Validate markdown syntax"""
        lines = content.split('\n')
        
        # Track if we're in a code block
        in_code_block = False
        
        # Check for common markdown issues
        for i, line in enumerate(lines, 1):
            # Toggle code block state
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            # Skip validation for lines inside code blocks
            if in_code_block:
                continue
            
            # Check for broken heading hierarchy (only outside code blocks)
            if re.match(r'^#{3,}\s', line):  # ### or more
                prev_heading = self._find_previous_heading(lines[:i-1])
                if prev_heading and prev_heading.count('#') < line.split()[0].count('#') - 1:
                    result.warnings.append(f"Line {i}: Heading hierarchy skip detected")
            
            # Check for trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                result.warnings.append(f"Line {i}: Trailing whitespace detected")
    
    def _find_previous_heading(self, lines: List[str]) -> Optional[str]:
        """Find the previous heading in the document, excluding code blocks"""
        in_code_block = False
        
        # We need to process from the beginning to track code blocks correctly
        # Build a list of valid headings
        valid_headings = []
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if not in_code_block and re.match(r'^#+\s', line):
                valid_headings.append(line)
        
        # Return the last valid heading, if any
        return valid_headings[-1] if valid_headings else None
    
    def _validate_structure(self, content: str, doc_type: Optional[str], result: ValidationResult):
        """Validate document structure based on type"""
        if not doc_type:
            return
        
        type_config = self.config.get('document_types', {}).get(doc_type, {})
        
        # Check required sections
        required_sections = type_config.get('required_sections', [])
        for section in required_sections:
            if section not in content:
                result.violations.append({
                    'type': 'missing_required_section',
                    'severity': 'critical',
                    'message': f"Missing required section: {section}",
                    'section': section
                })
        
        # Check recommended sections
        recommended_sections = type_config.get('recommended_sections', [])
        for section in recommended_sections:
            if section not in content:
                result.warnings.append(f"Missing recommended section: {section}")
    
    def _validate_content(self, content: str, doc_type: Optional[str], result: ValidationResult):
        """Validate document content requirements"""
        if not doc_type:
            return
        
        type_config = self.config.get('document_types', {}).get(doc_type, {})
        
        # Check minimum word count
        min_words = type_config.get('min_word_count', 0)
        if min_words > 0:
            word_count = len(content.split())
            if word_count < min_words:
                result.warnings.append(
                    f"Document has {word_count} words, minimum recommended is {min_words}"
                )
        
        # Check for code blocks if required
        if type_config.get('code_blocks_required', False):
            if '```' not in content:
                result.violations.append({
                    'type': 'missing_code_blocks',
                    'severity': 'major',
                    'message': 'Document requires code examples'
                })
        
        # Check for examples if required
        if type_config.get('example_required', False):
            if not re.search(r'[Ee]xample', content):
                result.warnings.append('Document should include examples')
    
    def _validate_metadata(self, content: str, doc_type: Optional[str], result: ValidationResult):
        """Validate document metadata"""
        if not doc_type:
            return
        
        type_config = self.config.get('document_types', {}).get(doc_type, {})
        metadata_required = type_config.get('metadata_required', [])
        
        for field in metadata_required:
            pattern = rf'\*\*{field.title()}\*\*:\s*.+'
            if not re.search(pattern, content, re.IGNORECASE):
                result.warnings.append(f"Missing metadata field: {field}")
    
    def _validate_links(self, content: str, file_path: Path, result: ValidationResult):
        """Validate internal and external links"""
        # Find all markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)
        
        for link_text, link_url in links:
            # Skip external links for now
            if link_url.startswith('http://') or link_url.startswith('https://'):
                continue
            
            # Check internal links
            if link_url.startswith('#'):
                # Anchor link - check if section exists
                anchor = link_url[1:].lower().replace('-', ' ')
                if not any(anchor in line.lower() for line in content.split('\n')):
                    result.warnings.append(f"Possible broken anchor link: {link_url}")
            elif not link_url.startswith('http'):
                # File link - check if file exists
                link_path = file_path.parent / link_url
                if not link_path.exists():
                    result.violations.append({
                        'type': 'broken_link',
                        'severity': 'major',
                        'message': f"Broken link to: {link_url}"
                    })
    
    def _calculate_score(self, result: ValidationResult) -> float:
        """Calculate overall documentation score"""
        if not result.violations and not result.warnings:
            return 1.0
        
        # Start with perfect score
        score = 1.0
        
        # Deduct for violations based on severity
        severity_penalties = {
            'critical': 0.35,  # Increased penalty for critical violations
            'major': 0.1,
            'minor': 0.05
        }
        
        for violation in result.violations:
            severity = violation.get('severity', 'minor')
            penalty = severity_penalties.get(severity, 0.05)
            score -= penalty
        
        # Small deduction for warnings
        score -= len(result.warnings) * 0.02
        
        # Ensure score stays between 0 and 1
        return max(0.0, min(1.0, score))
    
    def _add_suggestions(self, result: ValidationResult):
        """Add improvement suggestions based on validation results"""
        score_config = self.config.get('scoring', {})
        
        if result.score < score_config.get('warning_threshold', 0.85):
            result.suggestions.append("Consider addressing the violations and warnings to improve documentation quality")
        
        if result.score >= score_config.get('excellent_threshold', 0.95):
            result.suggestions.append("Excellent documentation! Keep up the good work!")
        
        # Specific suggestions based on violations
        violation_types = {v.get('type') for v in result.violations}
        
        if 'missing_required_section' in violation_types:
            result.suggestions.append("Add all required sections to meet documentation standards")
        
        if 'broken_link' in violation_types:
            result.suggestions.append("Fix broken links or update them to point to correct locations")
        
        if len(result.warnings) > 3:
            result.suggestions.append("Address warnings to improve documentation score")
    
    def validate_directory(self, directory: Path, pattern: str = "*.md") -> List[ValidationResult]:
        """Validate all matching files in a directory"""
        results = []
        
        for file_path in directory.glob(f"**/{pattern}"):
            # Skip exempted paths
            if self._is_exempted(file_path):
                continue
            
            result = self.validate_file(file_path)
            results.append(result)
        
        return results
    
    def _is_exempted(self, file_path: Path) -> bool:
        """Check if file is exempted from validation"""
        exempt_patterns = self.config.get('exemptions', {}).get('exempt_files', [])
        
        file_path_str = str(file_path).replace('\\', '/')  # Normalize path separators
        
        for pattern in exempt_patterns:
            # Check if the pattern matches anywhere in the path
            if '**' in pattern:
                # Handle ** patterns
                pattern_parts = pattern.replace('**/', '').replace('*', '')
                if pattern_parts in file_path_str:
                    return True
            elif fnmatch.fnmatch(file_path_str, pattern):
                return True
            # Also check if any part of the path contains the pattern
            elif '.archive' in pattern and '.archive' in file_path_str:
                return True
        
        return False
    
    def generate_report(self, results: List[ValidationResult]) -> str:
        """Generate validation report"""
        report = ["# Documentation Validation Report\n"]
        report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Files Validated**: {len(results)}\n")
        
        # Summary statistics
        valid_count = sum(1 for r in results if r.is_valid)
        avg_score = sum(r.score for r in results) / len(results) if results else 0
        
        report.append(f"**Valid Documents**: {valid_count}/{len(results)}\n")
        report.append(f"**Average Score**: {avg_score:.2%}\n")
        report.append("\n---\n")
        
        # Detailed results
        for result in results:
            status = "✅" if result.is_valid else "❌"
            report.append(f"\n## {status} {result.file_path}\n")
            report.append(f"**Score**: {result.score:.2%}\n")
            
            if result.violations:
                report.append("\n### Violations\n")
                for violation in result.violations:
                    report.append(f"- [{violation.get('severity', 'unknown').upper()}] {violation.get('message', 'Unknown violation')}\n")
            
            if result.warnings:
                report.append("\n### Warnings\n")
                for warning in result.warnings:
                    report.append(f"- {warning}\n")
            
            if result.suggestions:
                report.append("\n### Suggestions\n")
                for suggestion in result.suggestions:
                    report.append(f"- {suggestion}\n")
        
        return "".join(report)