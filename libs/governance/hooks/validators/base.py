"""
Base classes for governance validators

This module defines the abstract base class and common interfaces
for all governance validators.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime


@dataclass
class ValidationResult:
    """Result of a validation check"""
    
    validator_name: str
    success: bool
    score: float  # 0.0 to 100.0
    violations: List[Dict[str, Any]]
    warnings: List[str]
    suggestions: List[str]
    execution_time: float
    files_checked: List[str]
    metadata: Dict[str, Any]
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed"""
        return self.success
    
    @property
    def compliance_score(self) -> float:
        """Get compliance score as percentage"""
        return self.score
    
    def add_violation(self, level: str, message: str, penalty: float, file_path: str = None):
        """Add a violation to the result"""
        violation = {
            'level': level,
            'message': message,
            'penalty': penalty,
            'file_path': file_path,
            'timestamp': datetime.now().isoformat()
        }
        self.violations.append(violation)
        self.score = max(0, self.score - penalty)
        self.success = False
    
    def add_warning(self, message: str):
        """Add a warning to the result"""
        self.warnings.append(message)
    
    def add_suggestion(self, message: str):
        """Add a suggestion to the result"""
        self.suggestions.append(message)


class ValidatorInterface(ABC):
    """
    Abstract base class for all governance validators
    
    Each validator is responsible for checking a specific aspect
    of governance compliance (README files, code documentation, etc.)
    """
    
    def __init__(self, repo_root: Path, config: Dict[str, Any], 
                 changed_files: List[str], exemption_manager=None):
        """
        Initialize validator
        
        Args:
            repo_root: Path to repository root
            config: Governance configuration
            changed_files: List of changed file paths
            exemption_manager: Optional exemption manager instance
        """
        self.repo_root = Path(repo_root)
        self.config = config
        self.changed_files = changed_files
        self.exemption_manager = exemption_manager
        
        # Subclasses can override these
        self.validator_name = self.__class__.__name__
        self.penalty_weights = {
            'CRITICAL': config.get('penalties', {}).get('critical', 20),
            'HIGH': config.get('penalties', {}).get('high', 10),
            'MEDIUM': config.get('penalties', {}).get('medium', 5),
            'LOW': config.get('penalties', {}).get('low', 2)
        }
    
    @abstractmethod
    def validate(self) -> ValidationResult:
        """
        Perform validation and return results
        
        This method must be implemented by each concrete validator.
        It should check the relevant files and return a ValidationResult
        with all violations, warnings, and suggestions.
        
        Returns:
            ValidationResult: The validation result
        """
        pass
    
    def is_exempt(self, file_path: str, rule_id: str) -> bool:
        """
        Check if a file is exempt from a specific rule
        
        Args:
            file_path: Path to the file
            rule_id: ID of the rule being checked
            
        Returns:
            bool: True if exempt, False otherwise
        """
        if self.exemption_manager:
            return self.exemption_manager.is_exempt(file_path, rule_id)
        return False
    
    def get_skip_patterns(self) -> List[str]:
        """Get skip patterns from configuration"""
        return self.config.get('documentation', {}).get('skip_directories', [])
    
    def should_skip_file(self, file_path: str) -> bool:
        """
        Check if a file should be skipped based on skip patterns
        
        Args:
            file_path: Path to check
            
        Returns:
            bool: True if file should be skipped
        """
        skip_patterns = self.get_skip_patterns()
        return any(skip in file_path for skip in skip_patterns)
    
    def is_source_file(self, file_path: str) -> bool:
        """Check if file is source code"""
        extensions = ['.py', '.ts', '.js', '.tsx', '.jsx']
        return any(file_path.endswith(ext) for ext in extensions)
    
    def is_test_file(self, file_path: str) -> bool:
        """Check if file is a test file"""
        return 'test' in file_path.lower() or 'spec' in file_path.lower()
    
    def create_result(self) -> ValidationResult:
        """Create a new validation result with default values"""
        return ValidationResult(
            validator_name=self.validator_name,
            success=True,
            score=100.0,
            violations=[],
            warnings=[],
            suggestions=[],
            execution_time=0.0,
            files_checked=[],
            metadata={}
        )
    
    def log_validation_start(self) -> datetime:
        """Log the start of validation and return start time"""
        start_time = datetime.now()
        print(f"\n[CHECK] {self.validator_name}")
        print("-" * 40)
        return start_time
    
    def log_validation_end(self, result: ValidationResult, start_time: datetime):
        """Log the end of validation"""
        result.execution_time = (datetime.now() - start_time).total_seconds()
        
        if result.success:
            print(f"[PASS] {self.validator_name} - Score: {result.score:.1f}%")
        else:
            print(f"[FAIL] {self.validator_name} - Score: {result.score:.1f}% - {len(result.violations)} violation(s)")
            
        # Show top violations
        for violation in result.violations[:3]:
            print(f"  - {violation.get('message', 'Unknown violation')}")
        
        # Show warnings
        for warning in result.warnings[:2]:
            print(f"  ⚠ {warning}")
