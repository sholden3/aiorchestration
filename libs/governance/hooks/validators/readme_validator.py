"""
README Validator

Handles validation of README.md files across the repository.
Ensures every directory has proper README documentation.
"""

import sys
from pathlib import Path
from typing import Set, List
from datetime import datetime

try:
    from .base import ValidatorInterface, ValidationResult
except ImportError:
    from base import ValidatorInterface, ValidationResult


class ReadmeValidator(ValidatorInterface):
    """Validates README.md files across the repository"""
    
    def __init__(self, repo_root: Path, config: dict, changed_files: List[str], 
                 exemption_manager=None, all_directories: Set[str] = None):
        super().__init__(repo_root, config, changed_files, exemption_manager)
        self.validator_name = "README Files"
        self.all_directories = all_directories or self._get_all_directories()
        
        # Try to import unified validator
        self.unified_validator = None
        try:
            from libs.governance.validators.unified_doc_validator import UnifiedDocumentValidator
            self.unified_validator = UnifiedDocumentValidator()
        except ImportError:
            pass
    
    def _get_all_directories(self) -> Set[str]:
        """Get all directories in the project"""
        import os
        
        dirs = set()
        skip_paths = self.get_skip_patterns()
        
        for root, directories, _ in os.walk(self.repo_root):
            # Skip if current path contains any skip pattern
            if any(skip in root for skip in skip_paths):
                continue
                
            for d in directories:
                if d not in skip_paths:
                    rel_path = Path(root) / d
                    rel_str = str(rel_path.relative_to(self.repo_root))
                    # Double check the relative path doesn't contain skip patterns
                    if not any(skip in rel_str for skip in skip_paths):
                        dirs.add(rel_str)
        return dirs
    
    def validate(self) -> ValidationResult:
        """Validate README files using unified validator with exemption support"""
        start_time = self.log_validation_start()
        result = self.create_result()
        
        if self.unified_validator:
            return self._validate_with_unified_validator(result, start_time)
        else:
            return self._validate_basic(result, start_time)
    
    def _validate_with_unified_validator(self, result: ValidationResult, start_time: datetime) -> ValidationResult:
        """Use unified validator with exemptions"""
        try:
            dirs_without_readme = []
            readme_issues = []
            
            for dir_path in self.all_directories:
                readme_path = self.repo_root / dir_path / "README.md"
                result.files_checked.append(str(readme_path))
                
                # Check if README is required (using exemption system)
                if readme_path.exists():
                    validation_result = self.unified_validator.validate_file(readme_path)
                    if not validation_result.valid and 'fully_exempt' not in validation_result.exemptions:
                        for issue in validation_result.issues:
                            if 'Missing required section' in issue:
                                readme_issues.append((dir_path, issue))
                                result.add_violation(
                                    level="HIGH",
                                    message=f"README in '{dir_path}': {issue}",
                                    penalty=self.penalty_weights['MEDIUM'],
                                    file_path=str(readme_path)
                                )
                else:
                    # Check if directory needs README
                    validation_result = self.unified_validator.validate_path(self.repo_root / dir_path)
                    if validation_result.get('readme_required', True):
                        dirs_without_readme.append(dir_path)
                        result.add_violation(
                            level="CRITICAL",
                            message=f"Directory '{dir_path}' missing README.md",
                            penalty=self.penalty_weights['HIGH'],
                            file_path=str(readme_path)
                        )
            
            # Set metadata
            result.metadata = {
                'directories_checked': len(self.all_directories),
                'directories_without_readme': len(dirs_without_readme),
                'readme_issues': len(readme_issues),
                'validator_type': 'unified'
            }
            
        except Exception as e:
            result.add_warning(f"Unified validator error, falling back: {e}")
            return self._validate_basic(result, start_time)
        
        self.log_validation_end(result, start_time)
        return result
    
    def _validate_basic(self, result: ValidationResult, start_time: datetime) -> ValidationResult:
        """Fallback to original logic if unified validator not available"""
        doc_config = self.config.get('documentation', {}).get('directories', {})
        max_depth = doc_config.get('readme_max_depth', 999)
        required_parents = doc_config.get('readme_required_parents', [])
        required_sections = doc_config.get('readme_min_sections', [])
        
        dirs_without_readme = []
        
        for dir_path in self.all_directories:
            depth = len(Path(dir_path).parts)
            
            # Skip deep directories unless explicitly required
            if depth > max_depth and dir_path not in required_parents:
                continue
            
            should_check = False
            if depth <= max_depth:
                should_check = True
            else:
                for parent in required_parents:
                    if dir_path.startswith(parent + '/') or dir_path == parent:
                        should_check = True
                        break
            
            if should_check:
                readme_path = self.repo_root / dir_path / "README.md"
                result.files_checked.append(str(readme_path))
                
                if not readme_path.exists():
                    # Check if exempt
                    if not self.is_exempt(str(readme_path), 'readme_required'):
                        dirs_without_readme.append(dir_path)
                        result.add_violation(
                            level="CRITICAL",
                            message=f"Directory '{dir_path}' missing README.md",
                            penalty=self.penalty_weights['HIGH'],
                            file_path=str(readme_path)
                        )
                else:
                    # Check README content
                    try:
                        content = readme_path.read_text(encoding='utf-8', errors='ignore')
                    except:
                        content = readme_path.read_text(errors='ignore')
                    
                    missing = [s for s in required_sections if s not in content]
                    if missing and not self.is_exempt(str(readme_path), 'readme_sections'):
                        result.add_violation(
                            level="HIGH",
                            message=f"README in '{dir_path}' missing sections: {', '.join(missing)}",
                            penalty=self.penalty_weights['MEDIUM'],
                            file_path=str(readme_path)
                        )
        
        # Set metadata
        result.metadata = {
            'directories_checked': len(self.all_directories),
            'directories_without_readme': len(dirs_without_readme),
            'max_depth_checked': max_depth,
            'validator_type': 'basic'
        }
        
        if not result.violations:
            result.add_suggestion("Consider adding more detailed README sections for better documentation")
        
        self.log_validation_end(result, start_time)
        return result
