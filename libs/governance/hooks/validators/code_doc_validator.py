"""
Code Documentation Validator

Handles validation of source code documentation standards.
Ensures every source file has complete documentation with required tags.
"""

from pathlib import Path
from typing import List
from datetime import datetime

try:
    from .base import ValidatorInterface, ValidationResult
except ImportError:
    from base import ValidatorInterface, ValidationResult


class CodeDocValidator(ValidatorInterface):
    """Validates source code documentation standards"""
    
    def __init__(self, repo_root: Path, config: dict, changed_files: List[str], exemption_manager=None):
        super().__init__(repo_root, config, changed_files, exemption_manager)
        self.validator_name = "Source Code Documentation"
        
        # Try to import advanced validators
        self.advanced_validator = None
        try:
            from libs.governance.validators.unified_doc_validator import UnifiedDocumentValidator
            self.advanced_validator = UnifiedDocumentValidator()
        except ImportError:
            try:
                from libs.governance.validators.code_doc_validator import CodeDocumentationValidator
                self.advanced_validator = CodeDocumentationValidator()
            except ImportError:
                pass
    
    def validate(self) -> ValidationResult:
        """Validate source code documentation"""
        start_time = self.log_validation_start()
        result = self.create_result()
        
        # Get staged code files
        code_files = [
            f for f in self.changed_files 
            if self.is_source_file(f)
            and not self.is_test_file(f)
            and not any(pattern in f for pattern in ['migrations', 'vendor', 'node_modules'])
            and not self.should_skip_file(f)
        ]
        
        if not code_files:
            result.add_suggestion("No code files to validate")
            self.log_validation_end(result, start_time)
            return result
        
        if self.advanced_validator:
            return self._validate_with_advanced_validator(result, code_files, start_time)
        else:
            return self._validate_basic(result, code_files, start_time)
    
    def _validate_with_advanced_validator(self, result: ValidationResult, 
                                        code_files: List[str], start_time: datetime) -> ValidationResult:
        """Use advanced code documentation validator"""
        try:
            total_score = 0
            failed_files = []
            
            enforcement_mode = getattr(self.advanced_validator, 'enforcement_mode', 'strict')
            result.metadata['enforcement_mode'] = enforcement_mode
            
            for file_path in code_files:
                full_path = self.repo_root / file_path
                if not full_path.exists():
                    continue
                
                result.files_checked.append(file_path)
                
                # Validate the file
                validation_result = self.advanced_validator.validate_file(full_path)
                file_score = getattr(validation_result, 'score', 0)
                total_score += file_score
                
                # Check if valid
                is_valid = getattr(validation_result, 'is_valid', file_score >= 0.8)
                
                if not is_valid:
                    failed_files.append(file_path)
                    
                    # Add violations from the validator
                    violations = getattr(validation_result, 'violations', [])
                    for violation in violations[:3]:  # Limit to top 3 violations
                        message = violation.get('message', 'Code documentation issue')
                        severity = violation.get('severity', 'medium').upper()
                        penalty = self.penalty_weights.get(severity, self.penalty_weights['MEDIUM'])
                        
                        result.add_violation(
                            level=severity,
                            message=f"{file_path}: {message}",
                            penalty=penalty,
                            file_path=file_path
                        )
            
            # Calculate average score
            avg_score = total_score / len(code_files) if code_files else 1.0
            result.metadata['average_score'] = avg_score
            result.metadata['failed_files'] = len(failed_files)
            
            # Apply enforcement based on mode
            if failed_files and enforcement_mode != 'warnings_only':
                if not result.violations:  # If no specific violations were added
                    result.add_violation(
                        level="HIGH",
                        message=f"Code documentation below standards in {len(failed_files)} file(s)",
                        penalty=self.penalty_weights['HIGH']
                    )
            
        except Exception as e:
            result.add_warning(f"Advanced validator error, falling back: {e}")
            return self._validate_basic(result, code_files, start_time)
        
        self.log_validation_end(result, start_time)
        return result
    
    def _validate_basic(self, result: ValidationResult, code_files: List[str], start_time: datetime) -> ValidationResult:
        """Basic validation using required tags"""
        source_config = self.config.get('documentation', {}).get('source_code', {})
        required_tags = source_config.get('required_tags', [
            '@description:', '@author:', '@version:', '@dependencies:', 
            '@exports:', '@testing:', '@last_review:'
        ])
        
        poorly_documented = []
        
        for file_path in code_files:
            full_path = self.repo_root / file_path
            if not full_path.exists():
                continue
                
            result.files_checked.append(file_path)
            
            # Skip if exempt
            if self.is_exempt(file_path, 'source_documentation'):
                result.add_suggestion(f"File '{file_path}' is exempt from documentation requirements")
                continue
            
            try:
                content = full_path.read_text(errors='ignore')
            except Exception as e:
                result.add_warning(f"Could not read file '{file_path}': {e}")
                continue
            
            missing_tags = []
            for tag in required_tags:
                if tag not in content:
                    missing_tags.append(tag)
            
            if missing_tags:
                poorly_documented.append(file_path)
                penalty = self.penalty_weights['MEDIUM'] * len(missing_tags)
                
                result.add_violation(
                    level="CRITICAL",
                    message=f"File '{file_path}' missing documentation tags: {', '.join(missing_tags)}",
                    penalty=penalty,
                    file_path=file_path
                )
        
        # Set metadata
        result.metadata = {
            'files_checked': len(code_files),
            'poorly_documented': len(poorly_documented),
            'required_tags': required_tags,
            'validator_type': 'basic'
        }
        
        if not poorly_documented:
            result.add_suggestion("Consider using advanced documentation validators for better quality checks")
        
        self.log_validation_end(result, start_time)
        return result
