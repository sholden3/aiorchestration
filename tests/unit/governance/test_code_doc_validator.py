"""
Unit tests for Code Documentation Validator

@description: Tests for code documentation validation across Python, TypeScript, and JavaScript
@author: Test Suite
@version: 1.0.0
@dependencies: pytest, unittest.mock
@testing: Self-testing
@last_review: 2025-09-03
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from governance.validators.code_doc_validator import CodeDocumentationValidator, CodeValidationResult
import ast


class TestCodeDocumentationValidator:
    """Test suite for code documentation validator."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance with test config.
        
        Returns:
            Configured validator instance
        """
        with patch('governance.validators.code_doc_validator.Path.exists', return_value=False):
            return CodeDocumentationValidator()
    
    @pytest.fixture
    def well_documented_python(self):
        """Sample well-documented Python code.
        
        Returns:
            String containing properly documented Python code
        """
        return '''"""
Module for testing documentation.

@description: Test module with proper documentation
@author: Test Author
@version: 1.0.0
"""

class TestClass:
    """Test class with documentation.
    
    This class demonstrates proper documentation.
    
    Attributes:
        value: A test value
    """
    
    def __init__(self, value):
        """Initialize the test class.
        
        Args:
            value: Initial value
        """
        self.value = value
    
    def get_value(self):
        """Get the current value.
        
        Returns:
            The current value
        """
        return self.value
    
    def set_value(self, new_value):
        """Set a new value.
        
        Args:
            new_value: The new value to set
            
        Raises:
            ValueError: If new_value is None
        """
        if new_value is None:
            raise ValueError("Value cannot be None")
        self.value = new_value
'''
    
    @pytest.fixture
    def poorly_documented_python(self):
        """Sample poorly documented Python code.
        
        Returns:
            String containing poorly documented Python code
        """
        return '''
class TestClass:
    def __init__(self, value):
        self.value = value
    
    def get_value(self):
        return self.value
    
    def set_value(self, new_value):
        if new_value is None:
            raise ValueError("Value cannot be None")
        self.value = new_value
'''
    
    @pytest.fixture
    def well_documented_typescript(self):
        """Sample well-documented TypeScript code.
        
        Returns:
            String containing properly documented TypeScript code
        """
        return '''/**
 * @fileoverview Test module for documentation validation
 * @module TestModule
 * @author Test Author
 * @version 1.0.0
 */

/**
 * Test class demonstrating proper documentation.
 * 
 * @class TestClass
 * @implements {ITestInterface}
 */
export class TestClass implements ITestInterface {
    private value: string;
    
    /**
     * Initialize the test class.
     * 
     * @param {string} value - Initial value
     */
    constructor(value: string) {
        this.value = value;
    }
    
    /**
     * Get the current value.
     * 
     * @returns {string} The current value
     */
    public getValue(): string {
        return this.value;
    }
    
    /**
     * Set a new value.
     * 
     * @param {string} newValue - The new value to set
     * @throws {Error} If newValue is empty
     */
    public setValue(newValue: string): void {
        if (!newValue) {
            throw new Error("Value cannot be empty");
        }
        this.value = newValue;
    }
}
'''
    
    def test_validator_initialization(self):
        """Test validator initializes with default config."""
        with patch('governance.validators.code_doc_validator.Path.exists', return_value=False):
            validator = CodeDocumentationValidator()
            assert validator.config is not None
            assert validator.enforcement_mode in ['progressive', 'strict', 'warnings_only']
    
    def test_validate_missing_file(self, validator):
        """Test validation of non-existent file."""
        result = validator.validate_file(Path("nonexistent.py"))
        assert not result.is_valid
        assert result.score == 0.0
        assert any(v['type'] == 'file_not_found' for v in result.violations)
    
    def test_validate_well_documented_python(self, validator, well_documented_python):
        """Test validation of properly documented Python code."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value=well_documented_python):
                result = validator.validate_file(Path("test.py"))
                assert result.is_valid
                assert result.score > 0.8
                assert len(result.violations) == 0
    
    def test_validate_poorly_documented_python(self, validator, poorly_documented_python):
        """Test validation catches missing Python documentation."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value=poorly_documented_python):
                result = validator.validate_file(Path("test.py"))
                assert not result.is_valid
                assert result.score < 0.7
                assert any(v['type'] == 'missing_file_docstring' for v in result.violations)
                assert any(v['type'] == 'missing_class_docstring' for v in result.violations)
    
    def test_validate_typescript_file(self, validator, well_documented_typescript):
        """Test validation of TypeScript file."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value=well_documented_typescript):
                result = validator.validate_file(Path("test.ts"))
                assert result.is_valid
                assert result.score > 0.7
    
    def test_validate_javascript_file(self, validator):
        """Test validation of JavaScript file with relaxed requirements."""
        js_code = '''/**
 * @fileoverview Test JavaScript file
 */

function testFunction(param) {
    return param * 2;
}
'''
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value=js_code):
                result = validator.validate_file(Path("test.js"))
                # JavaScript has more lenient requirements
                assert result.score >= 0.5
    
    def test_exempted_files(self, validator):
        """Test that exempted files are skipped."""
        validator.config = {
            'validation': {
                'exemptions': {
                    'file_exemptions': ['**/tests/**', '**/*.test.*']
                }
            }
        }
        
        with patch('pathlib.Path.exists', return_value=True):
            result = validator.validate_file(Path("tests/test_file.py"))
            assert result.is_valid
            assert result.score == 1.0
            assert "exempted" in result.suggestions[0].lower()
    
    def test_method_exemptions(self, validator):
        """Test that exempted methods are not validated."""
        code = '''"""Module docstring."""

class TestClass:
    """Class docstring."""
    
    def __init__(self):
        # Constructor is exempted
        pass
    
    def public_method(self):
        # This should be flagged
        pass
'''
        validator.config['validation'] = {
            'exemptions': {
                'method_exemptions': ['__init__']
            }
        }
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value=code):
                result = validator.validate_file(Path("test.py"))
                # Should only flag public_method, not __init__
                violations = [v for v in result.violations if 'method' in v.get('type', '')]
                assert all('__init__' not in v.get('message', '') for v in violations)
    
    def test_python_method_validation(self, validator):
        """Test Python method documentation validation."""
        code = '''"""Module docstring."""

def function_with_params(param1, param2):
    """Missing Args section."""
    return param1 + param2

def function_with_return():
    """Missing Returns section."""
    return 42

def function_with_exception():
    """Missing Raises section."""
    raise ValueError("Test")
'''
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value=code):
                result = validator.validate_file(Path("test.py"))
                assert any("missing Args section" in w for w in result.warnings)
                assert any("missing Returns section" in w for w in result.warnings)
                assert any("missing Raises section" in w for w in result.warnings)
    
    def test_score_calculation(self, validator):
        """Test score calculation based on violations."""
        result = CodeValidationResult(
            file_path="test.py",
            is_valid=True,
            score=1.0
        )
        
        # Add violations with different severities
        result.violations.append({'severity': 'critical', 'type': 'test'})
        result.violations.append({'severity': 'major', 'type': 'test'})
        result.warnings.extend(['warning1', 'warning2'])
        
        score = validator._calculate_score(result)
        assert 0 <= score <= 1
        assert score < 1.0  # Should be less than perfect
    
    def test_coverage_metrics(self, validator):
        """Test documentation coverage calculation."""
        code = '''"""Module docstring."""

class DocumentedClass:
    """Class with docs."""
    
    def documented_method(self):
        """Method with docs."""
        pass
    
    def undocumented_method(self):
        pass

class UndocumentedClass:
    def method(self):
        pass
'''
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value=code):
                result = validator.validate_file(Path("test.py"))
                assert 'coverage' in result.__dict__
                assert 'classes' in result.coverage
                assert 'methods' in result.coverage
                assert result.coverage['classes'] == "1/2"  # 1 of 2 classes documented
    
    def test_generate_report(self, validator):
        """Test report generation from validation results."""
        results = [
            CodeValidationResult(
                file_path="well_documented.py",
                is_valid=True,
                score=0.95,
                coverage={'classes': '5/5', 'methods': '10/10', 'percentage': 100},
                suggestions=["Excellent code documentation!"]
            ),
            CodeValidationResult(
                file_path="poorly_documented.py",
                is_valid=False,
                score=0.4,
                violations=[
                    {'severity': 'critical', 'message': 'Missing module docstring'},
                    {'severity': 'major', 'message': 'Missing class docstring'}
                ],
                warnings=["Missing Args section", "Missing Returns section"],
                coverage={'classes': '1/3', 'methods': '2/8', 'percentage': 30}
            )
        ]
        
        report = validator.generate_report(results)
        
        assert "Code Documentation Validation Report" in report
        assert "well_documented.py" in report
        assert "poorly_documented.py" in report
        assert "✅" in report  # Valid file
        assert "❌" in report  # Invalid file
        assert "Coverage" in report
        assert "95.00%" in report  # Score for well documented
        assert "40.00%" in report  # Score for poorly documented
    
    def test_enforcement_modes(self):
        """Test different enforcement modes."""
        config = {
            'global': {
                'enabled': True,
                'enforcement_mode': 'strict'
            },
            'scoring': {
                'pass_threshold': 0.9
            }
        }
        
        with patch('builtins.open', mock_open(read_data=str(config))):
            with patch('yaml.safe_load', return_value=config):
                with patch('pathlib.Path.exists', return_value=True):
                    validator = CodeDocumentationValidator()
                    assert validator.enforcement_mode == 'strict'
    
    def test_suggestions_generation(self, validator):
        """Test that appropriate suggestions are generated."""
        result = CodeValidationResult(
            file_path="test.py",
            is_valid=False,
            score=0.6,
            violations=[
                {'type': 'missing_file_docstring'},
                {'type': 'missing_class_docstring'},
                {'type': 'missing_method_docstring'}
            ],
            coverage={'percentage': 50}
        )
        
        validator._add_suggestions(result)
        
        assert any("file-level documentation" in s for s in result.suggestions)
        assert any("public classes" in s for s in result.suggestions)
        assert any("public methods" in s for s in result.suggestions)
        assert any("80%" in s for s in result.suggestions)  # Coverage suggestion