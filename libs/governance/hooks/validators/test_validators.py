"""
Test suite for the modular validator system

This file tests all validators individually and as part of the orchestrator
to ensure they work correctly and maintain backward compatibility.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Add the validators to path
current_dir = Path(__file__).parent
validators_path = current_dir / "validators"
sys.path.insert(0, str(validators_path))

from base import ValidatorInterface, ValidationResult
from readme_validator import ReadmeValidator
from code_doc_validator import CodeDocValidator
from naming_validator import NamingValidator
from file_creation_validator import FileCreationValidator
from test_coverage_validator import TestCoverageValidator
from code_quality_validator import CodeQualityValidator
from orchestrator import ValidatorOrchestrator


class TestValidationResult(unittest.TestCase):
    """Test the ValidationResult class"""
    
    def test_validation_result_creation(self):
        """Test creating a validation result"""
        result = ValidationResult(
            validator_name="TestValidator",
            success=True,
            score=100.0,
            violations=[],
            warnings=[],
            suggestions=[],
            execution_time=0.0,
            files_checked=[],
            metadata={}
        )
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.compliance_score, 100.0)
    
    def test_adding_violations(self):
        """Test adding violations to a result"""
        result = ValidationResult(
            validator_name="TestValidator",
            success=True,
            score=100.0,
            violations=[],
            warnings=[],
            suggestions=[],
            execution_time=0.0,
            files_checked=[],
            metadata={}
        )
        
        result.add_violation("HIGH", "Test violation", 10.0, "test.py")
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.compliance_score, 90.0)
        self.assertEqual(len(result.violations), 1)
        self.assertEqual(result.violations[0]['level'], "HIGH")


class TestValidatorInterface(unittest.TestCase):
    """Test the base validator interface"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config = {
            'penalties': {
                'critical': 20,
                'high': 10,
                'medium': 5,
                'low': 2
            },
            'documentation': {
                'skip_directories': ['__pycache__', '.git']
            }
        }
        self.changed_files = ['test.py', 'README.md']
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_base_validator_interface(self):
        """Test that the base validator interface works correctly"""
        # Create a concrete implementation for testing
        class TestValidator(ValidatorInterface):
            def validate(self):
                result = self.create_result()
                result.add_suggestion("Test suggestion")
                return result
        
        validator = TestValidator(
            self.temp_dir, self.config, self.changed_files
        )
        
        result = validator.validate()
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.suggestions), 1)
        self.assertEqual(result.validator_name, "TestValidator")


class TestReadmeValidator(unittest.TestCase):
    """Test the README validator"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config = {
            'penalties': {'high': 10, 'medium': 5},
            'documentation': {
                'skip_directories': ['__pycache__'],
                'directories': {
                    'readme_max_depth': 3,
                    'readme_required_parents': [],
                    'readme_min_sections': ['## Description', '## Usage']
                }
            }
        }
        self.changed_files = []
        
        # Create test directory structure
        self.test_dir = self.temp_dir / 'src'
        self.test_dir.mkdir()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_readme_validator_missing_readme(self):
        """Test validator detects missing README files"""
        all_directories = {'src'}
        
        validator = ReadmeValidator(
            self.temp_dir, self.config, self.changed_files, 
            all_directories=all_directories
        )
        
        result = validator.validate()
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any('missing README.md' in v['message'] for v in result.violations))
    
    def test_readme_validator_existing_readme(self):
        """Test validator passes with existing README"""
        all_directories = {'src'}
        
        # Create README file
        readme_path = self.test_dir / 'README.md'
        readme_path.write_text("""# Test Module
        
## Description
This is a test module.

## Usage
Use it for testing.
""")
        
        validator = ReadmeValidator(
            self.temp_dir, self.config, self.changed_files,
            all_directories=all_directories
        )
        
        result = validator.validate()
        
        self.assertTrue(result.is_valid)


class TestCodeDocValidator(unittest.TestCase):
    """Test the code documentation validator"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config = {
            'penalties': {'critical': 20, 'medium': 5},
            'documentation': {
                'skip_directories': ['__pycache__'],
                'source_code': {
                    'required_tags': ['@description:', '@author:']
                }
            }
        }
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_code_doc_validator_missing_tags(self):
        """Test validator detects missing documentation tags"""
        # Create test Python file without required tags
        test_file = self.temp_dir / 'test.py'
        test_file.write_text("""
def test_function():
    pass
""")
        
        changed_files = ['test.py']
        
        validator = CodeDocValidator(
            self.temp_dir, self.config, changed_files
        )
        
        result = validator.validate()
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any('missing documentation tags' in v['message'] for v in result.violations))
    
    def test_code_doc_validator_with_tags(self):
        """Test validator passes with required tags"""
        # Create test Python file with required tags
        test_file = self.temp_dir / 'test.py'
        test_file.write_text("""
'''
@description: Test module for testing
@author: Test Author
'''

def test_function():
    pass
""")
        
        changed_files = ['test.py']
        
        validator = CodeDocValidator(
            self.temp_dir, self.config, changed_files
        )
        
        result = validator.validate()
        
        # Should pass since all required tags are present
        self.assertTrue(result.is_valid)


class TestNamingValidator(unittest.TestCase):
    """Test the naming standards validator"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config = {
            'penalties': {'high': 10, 'medium': 5, 'low': 2},
            'naming': {
                'standard_files': {
                    'tracker': 'TRACKER.md',
                    'status': 'STATUS.md'
                }
            }
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_naming_validator_non_standard_tracker(self):
        """Test validator detects non-standard tracker files"""
        changed_files = ['project_tracker.md']
        
        validator = NamingValidator(
            self.temp_dir, self.config, changed_files
        )
        
        result = validator.validate()
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any('Non-standard tracker' in v['message'] for v in result.violations))
    
    def test_naming_validator_standard_files(self):
        """Test validator passes with standard file names"""
        changed_files = ['TRACKER.md', 'STATUS.md', 'regular_file.py']
        
        validator = NamingValidator(
            self.temp_dir, self.config, changed_files
        )
        
        result = validator.validate()
        
        # Should pass since all files follow naming standards
        self.assertTrue(result.is_valid)


class TestFileCreationValidator(unittest.TestCase):
    """Test the file creation validator"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config = {
            'penalties': {'critical': 20, 'high': 10, 'medium': 5},
            'file_creation': {
                'allowed_patterns': ['*.py', '*.md', '*.txt'],
                'forbidden_patterns': ['*.tmp', '*.log'],
                'max_file_size_mb': 1,
                'forbidden_binary_extensions': ['.exe', '.dll'],
                'temp_file_patterns': ['*.tmp', '*.bak']
            }
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_file_creation_forbidden_pattern(self):
        """Test validator detects forbidden file patterns"""
        # Create a temporary file
        temp_file = self.temp_dir / 'test.tmp'
        temp_file.write_text("temporary content")
        
        changed_files = ['test.tmp']
        
        validator = FileCreationValidator(
            self.temp_dir, self.config, changed_files
        )
        
        result = validator.validate()
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any('Forbidden file pattern' in v['message'] for v in result.violations))
    
    def test_file_creation_allowed_files(self):
        """Test validator passes with allowed file patterns"""
        changed_files = ['test.py', 'README.md', 'notes.txt']
        
        # Create the files so size check doesn't fail
        for file_name in changed_files:
            (self.temp_dir / file_name).write_text("content")
        
        validator = FileCreationValidator(
            self.temp_dir, self.config, changed_files
        )
        
        result = validator.validate()
        
        # Should pass since all files match allowed patterns
        self.assertTrue(result.is_valid)


class TestTestCoverageValidator(unittest.TestCase):
    """Test the test coverage validator"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config = {
            'penalties': {'high': 10},
            'testing': {
                'test_file_patterns': {
                    '.py': ['test_{name}.py', '{name}_test.py']
                },
                'execution_required': False
            }
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('subprocess.run')
    def test_test_coverage_missing_test(self, mock_run):
        """Test validator detects missing test files"""
        # Mock git commands
        mock_run.side_effect = [
            Mock(returncode=0, stdout=''),  # git ls-files
            Mock(returncode=0, stdout='')   # git diff --cached --name-only
        ]
        
        changed_files = ['module.py']
        
        validator = TestCoverageValidator(
            self.temp_dir, self.config, changed_files
        )
        
        result = validator.validate()
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any('No test file' in v['message'] for v in result.violations))
    
    @patch('subprocess.run')
    def test_test_coverage_with_test(self, mock_run):
        """Test validator passes when test file exists"""
        # Mock git commands to return test file
        mock_run.side_effect = [
            Mock(returncode=0, stdout='test_module.py\n'),  # git ls-files
            Mock(returncode=0, stdout='')                    # git diff --cached --name-only
        ]
        
        changed_files = ['module.py']
        
        validator = TestCoverageValidator(
            self.temp_dir, self.config, changed_files
        )
        
        result = validator.validate()
        
        # Should pass since test file exists
        self.assertTrue(result.is_valid)


class TestCodeQualityValidator(unittest.TestCase):
    """Test the code quality validator"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config = {
            'penalties': {'high': 10, 'medium': 5},
            'security': {
                'code_quality_patterns': [
                    {
                        'pattern': r'console\.log\(',
                        'message': 'Debug console.log found',
                        'severity': 'medium'
                    },
                    {
                        'pattern': r'TODO:',
                        'message': 'TODO comment found',
                        'severity': 'low'
                    }
                ]
            },
            'code_quality': {
                'max_line_length': 120
            }
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_code_quality_debug_code(self):
        """Test validator detects debug code"""
        # Create test file with debug code
        test_file = self.temp_dir / 'test.js'
        test_file.write_text("""
function test() {
    console.log("Debug message");
    return true;
}
""")
        
        changed_files = ['test.js']
        
        validator = CodeQualityValidator(
            self.temp_dir, self.config, changed_files
        )
        
        result = validator.validate()
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any('Debug console.log found' in v['message'] for v in result.violations))
    
    def test_code_quality_clean_code(self):
        """Test validator passes with clean code"""
        # Create test file without quality issues
        test_file = self.temp_dir / 'test.js'
        test_file.write_text("""
function test() {
    return true;
}
""")
        
        changed_files = ['test.js']
        
        validator = CodeQualityValidator(
            self.temp_dir, self.config, changed_files
        )
        
        result = validator.validate()
        
        # Should pass since no quality issues
        self.assertTrue(result.is_valid)


class TestValidatorOrchestrator(unittest.TestCase):
    """Test the validator orchestrator"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('subprocess.run')
    def test_orchestrator_initialization(self, mock_run):
        """Test orchestrator initializes correctly"""
        # Mock git commands
        mock_run.side_effect = [
            Mock(stdout=str(self.temp_dir)),  # git rev-parse --show-toplevel
            Mock(stdout=''),                  # git diff --cached --name-only
        ]
        
        # Create minimal config
        config_file = self.temp_dir / 'config' / 'governance' / 'rules.yaml'
        config_file.parent.mkdir(parents=True)
        config_file.write_text("""
version: 2.0
enforcement:
  compliance_minimum: 95
penalties:
  critical: 20
  high: 10
  medium: 5
  low: 2
""")
        
        with patch('builtins.open', unittest.mock.mock_open(read_data=config_file.read_text())):
            orchestrator = ValidatorOrchestrator()
        
        self.assertIsNotNone(orchestrator.config)
        self.assertEqual(len(orchestrator.validators), 6)  # 6 validators registered
    
    def test_validator_registration(self):
        """Test that all validators are properly registered"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = [
                Mock(stdout=str(self.temp_dir)),  # git rev-parse --show-toplevel
                Mock(stdout=''),                  # git diff --cached --name-only
            ]
            
            # Create minimal config
            config_file = self.temp_dir / 'config' / 'governance' / 'rules.yaml'
            config_file.parent.mkdir(parents=True)
            config_file.write_text("""
version: 2.0
enforcement:
  compliance_minimum: 95
penalties:
  critical: 20
  high: 10
  medium: 5
  low: 2
""")
            
            with patch('builtins.open', unittest.mock.mock_open(read_data=config_file.read_text())):
                orchestrator = ValidatorOrchestrator()
        
        expected_validators = [
            'readme', 'code_doc', 'naming', 'file_creation', 
            'test_coverage', 'code_quality'
        ]
        
        for validator_name in expected_validators:
            self.assertIn(validator_name, orchestrator.validators)


if __name__ == '__main__':
    unittest.main()
