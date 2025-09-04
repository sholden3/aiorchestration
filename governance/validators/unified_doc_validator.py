#!/usr/bin/env python3
"""
Unified Documentation Validator - Fixed Version

Uses the documentation_standards.yaml configuration for all validation.
Properly handles exemptions and scoring.

Author: Isabella Martinez & Marcus Thompson
Created: 2025-09-03
Version: 2.0.0 (Fixed)
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass
from functools import lru_cache
import fnmatch
import sys


@dataclass
class ValidationResult:
    """Result of document validation"""
    valid: bool
    score: float
    issues: List[str]
    warnings: List[str]
    exemptions: List[str]
    metadata: Dict[str, Any]
    
    # Compatibility properties for old validators
    @property
    def is_valid(self):
        return self.valid
    
    @property
    def violations(self):
        return [{'message': issue} for issue in self.issues]
    
    @property
    def suggestions(self):
        return []


class RobustExemptionMatcher:
    """Handles all exemption pattern matching logic"""
    
    def normalize_path(self, path: str) -> str:
        """Normalize path for consistent matching"""
        # Convert to forward slashes
        normalized = str(path).replace('\\', '/')
        # Remove leading slash if present
        if normalized.startswith('/'):
            normalized = normalized[1:]
        return normalized
    
    def matches_pattern(self, path: str, pattern: str, pattern_type: str = 'exact') -> bool:
        """Check if path matches exemption pattern"""
        norm_path = self.normalize_path(path)
        norm_pattern = self.normalize_path(pattern)
        
        if pattern_type == 'exact':
            # Exact match or ends with pattern
            return norm_path == norm_pattern or norm_path.endswith('/' + norm_pattern)
            
        elif pattern_type == 'glob':
            # Use glob pattern matching
            return fnmatch.fnmatch(norm_path, norm_pattern) or \
                   fnmatch.fnmatch(norm_path, f"**/{norm_pattern}") or \
                   fnmatch.fnmatch(norm_path, f"{norm_pattern}/**")
                   
        elif pattern_type == 'regex':
            # Regex pattern matching
            import re
            try:
                return bool(re.match(norm_pattern, norm_path))
            except:
                return False
                
        return False


class SectionValidator:
    """Validates individual document sections"""
    
    def find_section(self, content: str, section_config: Dict) -> Dict:
        """Find and validate a section in content"""
        section_name = section_config.get('section', '')
        level = section_config.get('level', 2)
        
        # Build regex for finding section
        heading_marker = '#' * level
        pattern = rf"^{re.escape(heading_marker)}\s+{re.escape(section_name)}\s*$"
        
        result = {
            'found': False,
            'issues': [],
            'content': ''
        }
        
        # Search for section
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if re.match(pattern, line, re.IGNORECASE):
                result['found'] = True
                
                # Extract section content
                section_content = []
                for j in range(i + 1, len(lines)):
                    # Stop at next heading of same or higher level
                    if lines[j].startswith('#' * (level - 1)) and lines[j].strip():
                        break
                    section_content.append(lines[j])
                
                result['content'] = '\n'.join(section_content).strip()
                
                # Validate content against requirements
                validation = section_config.get('validation', {})
                if validation:
                    word_count = len(result['content'].split())
                    min_words = validation.get('min_words', 0)
                    max_words = validation.get('max_words', float('inf'))
                    
                    if word_count < min_words:
                        result['issues'].append(f"Too short: {word_count} words (minimum: {min_words})")
                    elif word_count > max_words:
                        result['issues'].append(f"Too long: {word_count} words (maximum: {max_words})")
                
                break
        
        return result


class UnifiedDocumentValidator:
    """Fixed version with proper validation and exemption logic"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the unified validator"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "documentation_standards.yaml"
        
        self.config_path = config_path
        self.config = self._load_config()
        self.exemption_matcher = RobustExemptionMatcher()
        self.section_validator = SectionValidator()
        
        # Compatibility attributes
        self.enforcement_mode = 'progressive'
        
        # Sync exemptions from old config
        self._sync_exemptions()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load documentation standards configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def _sync_exemptions(self):
        """Synchronize exemptions from old config"""
        try:
            old_config_path = Path(__file__).parent.parent.parent / "governance" / "config.yaml"
            if old_config_path.exists():
                with open(old_config_path, 'r', encoding='utf-8') as f:
                    old_config = yaml.safe_load(f)
                
                skip_dirs = old_config.get('documentation', {}).get('skip_directories', [])
                
                # Add to our exemptions if not present
                if 'exemptions' in self.config:
                    current_exemptions = self.config['exemptions']['directory_readme_exemptions']['full_exemptions']
                    current_paths = {ex['path'] for ex in current_exemptions}
                    
                    for skip_dir in skip_dirs:
                        if skip_dir not in current_paths:
                            current_exemptions.append({
                                'path': skip_dir,
                                'type': 'glob' if '**' in skip_dir else 'exact',
                                'reason': 'Migrated from skip_directories',
                                'permanent': True
                            })
        except Exception as e:
            # Don't fail if sync doesn't work
            pass
    
    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a documentation file"""
        # Initialize result
        issues = []
        warnings = []
        exemptions = []
        score = 100.0
        
        # Get relative path for exemption checking
        rel_path = self._get_relative_path(file_path)
        # For directory-based exemptions (like README section exemptions), use parent directory
        dir_rel_path = self._get_relative_path(file_path.parent)
        
        # Check if file is completely exempt
        if self._is_file_exempt(rel_path):
            exemptions.append('fully_exempt')
            return ValidationResult(
                valid=True,
                score=100.0,
                issues=[],
                warnings=[],
                exemptions=exemptions,
                metadata={'exempted': True, 'reason': 'File exempted from validation'}
            )
        
        # Determine document type
        doc_type = self._determine_document_type(file_path)
        if not doc_type:
            # Unknown type, pass by default
            return ValidationResult(
                valid=True,
                score=100.0,
                issues=[],
                warnings=['Unknown document type - validation skipped'],
                exemptions=[],
                metadata={'document_type': 'unknown'}
            )
        
        # Read content
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return ValidationResult(
                valid=False,
                score=0.0,
                issues=[f"Could not read file: {e}"],
                warnings=[],
                exemptions=[],
                metadata={'error': str(e)}
            )
        
        # Get document configuration
        doc_config = self.config.get('document_types', {}).get(doc_type, {})
        required_sections = doc_config.get('required_sections', [])
        
        # Validate sections
        total_weight = 0
        earned_weight = 0
        
        for section_config in required_sections:
            section_name = section_config.get('section', '')
            section_weight = section_config.get('weight', 10)
            is_required = section_config.get('required', True)
            
            if is_required:
                total_weight += section_weight
            
            # Check if section is exempt (use directory path for section exemptions)
            if self._is_section_exempt(dir_rel_path, section_name):
                exemptions.append(f"section:{section_name}")
                if is_required:
                    earned_weight += section_weight  # Full credit for exempt sections
                continue
            
            # Validate section
            section_result = self.section_validator.find_section(content, section_config)
            
            if section_result['found']:
                if not section_result['issues']:
                    # Section is valid
                    if is_required:
                        earned_weight += section_weight
                else:
                    # Section has issues - partial credit
                    if is_required:
                        earned_weight += section_weight * 0.5
                    for issue in section_result['issues']:
                        warnings.append(f"{section_name}: {issue}")
            else:
                # Section missing
                if is_required:
                    issues.append(f"Missing required section: {section_name}")
                else:
                    warnings.append(f"Missing optional section: {section_name}")
        
        # Calculate score correctly (as percentage, not percentage * 100)
        if total_weight > 0:
            score = (earned_weight / total_weight) * 100
        else:
            score = 100.0
        
        # Determine validity based on threshold
        pass_threshold = self.config.get('validation_rules', {}).get('scoring', {}).get('pass_threshold', 70)
        valid = score >= pass_threshold and len(issues) == 0
        
        return ValidationResult(
            valid=valid,
            score=score,
            issues=issues,
            warnings=warnings,
            exemptions=exemptions,
            metadata={
                'document_type': doc_type,
                'total_weight': total_weight,
                'earned_weight': earned_weight
            }
        )
    
    def validate_path(self, path: Path) -> Dict[str, Any]:
        """Check if a directory needs a README"""
        rel_path = self._get_relative_path(path)
        
        # Check full exemptions
        exemptions_config = self.config.get('exemptions', {}).get('directory_readme_exemptions', {})
        for exemption in exemptions_config.get('full_exemptions', []):
            pattern = exemption.get('pattern', exemption.get('path', ''))
            pattern_type = exemption.get('type', 'exact')
            
            if self.exemption_matcher.matches_pattern(rel_path, pattern, pattern_type):
                return {
                    'readme_required': False,
                    'reason': exemption.get('reason', 'Exempted'),
                    'exemption_type': pattern_type,
                    'path': str(path)
                }
        
        # Not exempt, README required
        return {
            'readme_required': True,
            'reason': 'No exemption found',
            'path': str(path)
        }
    
    def _is_file_exempt(self, rel_path: str) -> bool:
        """Check if file is completely exempt from validation"""
        file_exemptions = self.config.get('exemptions', {}).get('file_exemptions', [])
        
        for exemption in file_exemptions:
            pattern = exemption.get('pattern', exemption.get('path', ''))
            pattern_type = exemption.get('type', 'exact')
            
            if self.exemption_matcher.matches_pattern(rel_path, pattern, pattern_type):
                return True
        
        return False
    
    def _is_section_exempt(self, rel_path: str, section_name: str) -> bool:
        """Check if a specific section is exempt for a path"""
        exemptions_config = self.config.get('exemptions', {}).get('directory_readme_exemptions', {})
        section_exemptions = exemptions_config.get('section_exemptions', [])
        
        for exemption in section_exemptions:
            # Check if path matches
            pattern = exemption.get('path', '')
            if self.exemption_matcher.matches_pattern(rel_path, pattern, 'exact'):
                # Check if section is in exempt list
                exempt_sections = exemption.get('exempt_sections', [])
                for exempt in exempt_sections:
                    if exempt.lower() in section_name.lower():
                        return True
        
        return False
    
    def _get_relative_path(self, path: Path) -> str:
        """Get normalized relative path"""
        try:
            # Try to get relative to repo root
            repo_root = Path.cwd()
            if path.is_absolute():
                try:
                    rel_path = path.relative_to(repo_root)
                except ValueError:
                    # Path is not relative to repo root
                    rel_path = path
            else:
                rel_path = path
            
            return self.exemption_matcher.normalize_path(str(rel_path))
        except Exception:
            return self.exemption_matcher.normalize_path(str(path))
    
    def _determine_document_type(self, file_path: Path) -> Optional[str]:
        """Determine document type from file name/path"""
        file_name = file_path.name
        
        # Check each document type's pattern
        for doc_type, config in self.config.get('document_types', {}).items():
            pattern = config.get('file_pattern', '')
            if pattern and pattern.lower() == file_name.lower():
                return doc_type
        
        return None
    
    # Compatibility methods for old interface
    def validate_staged_files(self):
        """Compatibility method for old validator interface"""
        import subprocess
        from types import SimpleNamespace
        
        # Get staged files
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True, text=True
        )
        staged_files = [f for f in result.stdout.strip().split('\n') if f.endswith('.md')]
        
        summary = SimpleNamespace(
            total_files=len(staged_files),
            valid_files=0,
            invalid_files=0,
            critical_violations=0,
            high_violations=0,
            medium_violations=0,
            low_violations=0,
            total_violations=0,
            results=[]
        )
        
        for file_path in staged_files:
            path = Path(file_path)
            if path.exists():
                result = self.validate_file(path)
                
                file_result = SimpleNamespace(
                    file_path=str(path),
                    is_valid=result.valid,
                    score=result.score / 100,  # Convert to 0-1 range for compatibility
                    violations=result.violations,
                    warnings=result.warnings,
                    suggestions=[],
                    severity='critical' if not result.valid else 'low',
                    message=result.issues[0] if result.issues else '',
                    penalty=10.0 if not result.valid else 0.0
                )
                
                summary.results.append(file_result)
                
                if result.valid:
                    summary.valid_files += 1
                else:
                    summary.invalid_files += 1
                    summary.total_violations += len(result.issues)
                    
                    # Count by severity
                    for issue in result.issues:
                        if 'Missing required section' in issue:
                            summary.critical_violations += 1
                        else:
                            summary.medium_violations += 1
        
        return summary


def main():
    """CLI interface for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Unified Documentation Validator')
    parser.add_argument('path', help='Path to file or directory to validate')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    
    args = parser.parse_args()
    
    validator = UnifiedDocumentValidator()
    path = Path(args.path)
    
    if path.is_file():
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
    
    elif path.is_dir():
        check_result = validator.validate_path(path)
        print(f"Directory: {path}")
        print(f"  README Required: {'Yes' if check_result['readme_required'] else 'No'}")
        print(f"  Reason: {check_result['reason']}")
    
    else:
        print(f"Error: {path} not found")
        sys.exit(1)


if __name__ == "__main__":
    main()