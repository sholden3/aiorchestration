"""
File Creation Validator

Handles validation of file creation rules.
Ensures only allowed files are being created and forbidden patterns are blocked.
"""

import fnmatch
from pathlib import Path
from typing import List
from datetime import datetime

try:
    from .base import ValidatorInterface, ValidationResult
except ImportError:
    from base import ValidatorInterface, ValidationResult


class FileCreationValidator(ValidatorInterface):
    """Validates file creation rules and patterns"""
    
    def __init__(self, repo_root: Path, config: dict, changed_files: List[str], exemption_manager=None):
        super().__init__(repo_root, config, changed_files, exemption_manager)
        self.validator_name = "File Creation Rules"
    
    def validate(self) -> ValidationResult:
        """Check that only allowed files are being created"""
        start_time = self.log_validation_start()
        result = self.create_result()
        
        file_config = self.config.get('file_creation', {})
        allowed_patterns = file_config.get('allowed_patterns', [])
        forbidden_patterns = file_config.get('forbidden_patterns', [])
        
        forbidden_files = []
        suspicious_files = []
        
        for file_path in self.changed_files:
            if self.should_skip_file(file_path):
                continue
                
            result.files_checked.append(file_path)
            filename = Path(file_path).name
            
            # Check if exempt
            if self.is_exempt(file_path, 'file_creation_rules'):
                result.add_suggestion(f"File '{file_path}' is exempt from creation rules")
                continue
            
            # Check forbidden patterns
            is_forbidden = False
            for pattern in forbidden_patterns:
                if self._matches_pattern(filename, pattern):
                    forbidden_files.append(file_path)
                    result.add_violation(
                        level="CRITICAL",
                        message=f"Forbidden file pattern: '{file_path}' matches '{pattern}'",
                        penalty=self.penalty_weights['CRITICAL'],
                        file_path=file_path
                    )
                    is_forbidden = True
                    break
            
            # Skip allowed pattern check if file is forbidden
            if is_forbidden:
                continue
            
            # Check if file matches allowed patterns
            if allowed_patterns and not any(self._matches_pattern(filename, p) for p in allowed_patterns):
                suspicious_files.append(file_path)
                result.add_violation(
                    level="HIGH",
                    message=f"Suspicious file type: '{file_path}' doesn't match allowed patterns",
                    penalty=self.penalty_weights['HIGH'],
                    file_path=file_path
                )
        
        # Additional checks
        self._check_file_sizes(result)
        self._check_binary_files(result)
        self._check_temp_files(result)
        
        # Set metadata
        result.metadata = {
            'files_checked': len(result.files_checked),
            'forbidden_files': len(forbidden_files),
            'suspicious_files': len(suspicious_files),
            'allowed_patterns': allowed_patterns,
            'forbidden_patterns': forbidden_patterns
        }
        
        if not forbidden_files and not suspicious_files:
            result.add_suggestion("All files follow creation rules")
        
        self.log_validation_end(result, start_time)
        return result
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches a pattern (supports wildcards)"""
        return fnmatch.fnmatch(filename.lower(), pattern.lower())
    
    def _check_file_sizes(self, result: ValidationResult):
        """Check for unusually large files that might be accidental"""
        max_size_mb = self.config.get('file_creation', {}).get('max_file_size_mb', 10)
        max_size_bytes = max_size_mb * 1024 * 1024
        
        for file_path in result.files_checked:
            full_path = self.repo_root / file_path
            if full_path.exists():
                try:
                    size = full_path.stat().st_size
                    if size > max_size_bytes:
                        size_mb = size / (1024 * 1024)
                        result.add_violation(
                            level="HIGH",
                            message=f"Large file: '{file_path}' ({size_mb:.1f}MB > {max_size_mb}MB)",
                            penalty=self.penalty_weights['MEDIUM'],
                            file_path=file_path
                        )
                except (OSError, IOError) as e:
                    result.add_warning(f"Could not check size of '{file_path}': {e}")
    
    def _check_binary_files(self, result: ValidationResult):
        """Check for binary files that might be accidentally committed"""
        binary_extensions = self.config.get('file_creation', {}).get('forbidden_binary_extensions', [
            '.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.db', '.sqlite',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.pdf', '.zip',
            '.rar', '.7z', '.tar', '.gz', '.tgz'
        ])
        
        for file_path in result.files_checked:
            filename = Path(file_path).name.lower()
            
            for ext in binary_extensions:
                if filename.endswith(ext.lower()):
                    # Check if this binary type is allowed
                    if not self.is_exempt(file_path, f'binary_file_{ext[1:]}'):
                        result.add_violation(
                            level="MEDIUM",
                            message=f"Binary file detected: '{file_path}' (consider using Git LFS)",
                            penalty=self.penalty_weights['LOW'],
                            file_path=file_path
                        )
                    break
    
    def _check_temp_files(self, result: ValidationResult):
        """Check for temporary files that shouldn't be committed"""
        temp_patterns = self.config.get('file_creation', {}).get('temp_file_patterns', [
            '*.tmp', '*.temp', '*.bak', '*.swp', '*.swo', '*~',
            '.DS_Store', 'Thumbs.db', '*.log'
        ])
        
        for file_path in result.files_checked:
            filename = Path(file_path).name
            
            for pattern in temp_patterns:
                if self._matches_pattern(filename, pattern):
                    result.add_violation(
                        level="HIGH",
                        message=f"Temporary file detected: '{file_path}' (should not be committed)",
                        penalty=self.penalty_weights['MEDIUM'],
                        file_path=file_path
                    )
                    break
