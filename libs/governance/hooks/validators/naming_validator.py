"""
Naming Standards Validator

Handles validation of universal naming standards across the repository.
Ensures files follow consistent naming conventions.
"""

from pathlib import Path
from typing import List
from datetime import datetime

try:
    from .base import ValidatorInterface, ValidationResult
except ImportError:
    from base import ValidatorInterface, ValidationResult


class NamingValidator(ValidatorInterface):
    """Validates naming standards across the repository"""
    
    def __init__(self, repo_root: Path, config: dict, changed_files: List[str], exemption_manager=None):
        super().__init__(repo_root, config, changed_files, exemption_manager)
        self.validator_name = "Naming Standards"
    
    def validate(self) -> ValidationResult:
        """Enforce universal naming standards"""
        start_time = self.log_validation_start()
        result = self.create_result()
        
        naming_config = self.config.get('naming', {})
        standard_files = naming_config.get('standard_files', {})
        
        violations_found = False
        
        # Check for non-standard tracker files
        for file_path in self.changed_files:
            if self.should_skip_file(file_path):
                continue
                
            result.files_checked.append(file_path)
            filename = Path(file_path).name.lower()
            
            # Check if exempt
            if self.is_exempt(file_path, 'naming_standards'):
                result.add_suggestion(f"File '{file_path}' is exempt from naming standards")
                continue
            
            # Check tracker naming
            if 'tracker' in filename and filename != 'tracker.md':
                violations_found = True
                result.add_violation(
                    level="CRITICAL",
                    message=f"Non-standard tracker: '{file_path}' should be 'TRACKER.md'",
                    penalty=self.penalty_weights['HIGH'],
                    file_path=file_path
                )
            
            # Check status file naming
            if 'status' in filename and 'status.md' not in filename.lower():
                violations_found = True
                result.add_violation(
                    level="HIGH",
                    message=f"Non-standard status file: '{file_path}' should be 'STATUS.md'",
                    penalty=self.penalty_weights['HIGH'],
                    file_path=file_path
                )
            
            # Check other standard file names
            for file_type, standard_name in standard_files.items():
                if file_type in filename and filename != standard_name.lower():
                    violations_found = True
                    result.add_violation(
                        level="HIGH",
                        message=f"Non-standard {file_type} file: '{file_path}' should be '{standard_name}'",
                        penalty=self.penalty_weights['MEDIUM'],
                        file_path=file_path
                    )
            
            # Check for other naming violations
            self._check_filename_conventions(file_path, result)
        
        # Set metadata
        result.metadata = {
            'files_checked': len(result.files_checked),
            'violations_found': violations_found,
            'standard_files': standard_files
        }
        
        if not violations_found:
            result.add_suggestion("Consider adding more naming convention rules for better consistency")
        
        self.log_validation_end(result, start_time)
        return result
    
    def _check_filename_conventions(self, file_path: str, result: ValidationResult):
        """Check additional filename conventions"""
        filename = Path(file_path).name
        
        # Check for spaces in filenames (should use underscores or hyphens)
        if ' ' in filename:
            result.add_violation(
                level="MEDIUM",
                message=f"Filename contains spaces: '{file_path}' (use underscores or hyphens)",
                penalty=self.penalty_weights['LOW'],
                file_path=file_path
            )
        
        # Check for uppercase extensions
        if filename.count('.') > 0:
            extension = filename.split('.')[-1]
            if extension != extension.lower():
                result.add_violation(
                    level="LOW",
                    message=f"File extension should be lowercase: '{file_path}'",
                    penalty=self.penalty_weights['LOW'],
                    file_path=file_path
                )
        
        # Check for special characters that might cause issues
        forbidden_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in forbidden_chars:
            if char in filename:
                result.add_violation(
                    level="HIGH",
                    message=f"Filename contains forbidden character '{char}': '{file_path}'",
                    penalty=self.penalty_weights['MEDIUM'],
                    file_path=file_path
                )
        
        # Check for very long filenames (platform compatibility)
        if len(filename) > 255:
            result.add_violation(
                level="MEDIUM",
                message=f"Filename too long ({len(filename)} chars): '{file_path}' (max 255)",
                penalty=self.penalty_weights['LOW'],
                file_path=file_path
            )
