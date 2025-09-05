#!/usr/bin/env python3
"""
Unit tests for UnifiedDocumentValidator

Tests the unified documentation validation system that uses
documentation_standards.yaml configuration.

Author: Isabella Martinez & Marcus Thompson
Created: 2025-09-03
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import yaml

from libs.governance.validators.unified_doc_validator import (
    UnifiedDocumentValidator,
    ValidationResult,
    RobustExemptionMatcher,
    SectionValidator
)


class TestRobustExemptionMatcher:
    """Test path matching and normalization"""
    
    def test_normalize_path(self):
        """Test path normalization"""
        matcher = RobustExemptionMatcher()
        
        # Windows path
        assert matcher.normalize_path("C:\\Users\\test\\file.py") == "C:/Users/test/file.py"
        
        # Unix path with leading slash
        assert matcher.normalize_path("/home/test/file.py") == "home/test/file.py"
        
        # Already normalized
        assert matcher.normalize_path("src/test/file.py") == "src/test/file.py"
    
    def test_exact_matching(self):
        """Test exact path matching"""
        matcher = RobustExemptionMatcher()
        
        # Exact match
        assert matcher.matches_pattern("node_modules", "node_modules", "exact")
        
        # Subdirectory match
        assert matcher.matches_pattern("project/node_modules", "node_modules", "exact")
        
        # No match
        assert not matcher.matches_pattern("src/modules", "node_modules", "exact")
    
    def test_glob_matching(self):
        """Test glob pattern matching"""
        matcher = RobustExemptionMatcher()
        
        # Glob patterns
        assert matcher.matches_pattern("src/__pycache__", "**/__pycache__", "glob")
        assert matcher.matches_pattern("dist/bundle.js", "**/dist", "glob")
        assert matcher.matches_pattern("test.pyc", "*.pyc", "glob")
        
        # No match
        assert not matcher.matches_pattern("src/main.py", "*.pyc", "glob")


class TestSectionValidator:
    """Test section finding and validation"""
    
    def test_find_section(self):
        """Test finding sections in markdown content"""
        validator = SectionValidator()
        
        content = """# Title
        
## Purpose
This is the purpose section with enough content to meet requirements.

## Testing  
This is testing content.

### Subsection
More content here.
"""
        
        # Find Purpose section
        result = validator.find_section(content, {
            'section': 'Purpose',
            'level': 2,
            'validation': {'min_words': 5}
        })
        
        assert result['found'] is True
        assert "purpose section" in result['content']
        assert len(result['issues']) == 0
    
    def test_section_word_count_validation(self):
        """Test word count validation"""
        validator = SectionValidator()
        
        content = """## Testing
Too short.
"""
        
        result = validator.find_section(content, {
            'section': 'Testing',
            'level': 2,
            'validation': {'min_words': 10}
        })
        
        assert result['found'] is True
        assert len(result['issues']) > 0
        assert "Too short" in result['issues'][0]


class TestUnifiedDocumentValidator:
    """Test the main unified validator"""
    
    @pytest.fixture
    def sample_config(self):
        """Provide sample configuration"""
        return {
            'document_types': {
                'README': {
                    'file_pattern': 'README.md',
                    'required_sections': [
                        {
                            'section': 'Purpose',
                            'level': 2,
                            'required': True,
                            'weight': 30,
                            'validation': {'min_words': 10}
                        },
                        {
                            'section': 'Testing',
                            'level': 2,
                            'required': True,
                            'weight': 30,
                            'validation': {'min_words': 5}
                        }
                    ]
                }
            },
            'validation_rules': {
                'scoring': {
                    'pass_threshold': 70
                }
            },
            'exemptions': {
                'directory_readme_exemptions': {
                    'full_exemptions': [
                        {
                            'path': 'node_modules',
                            'type': 'exact',
                            'reason': 'External deps'
                        }
                    ],
                    'section_exemptions': [
                        {
                            'path': 'tests',
                            'exempt_sections': ['Testing']
                        }
                    ]
                }
            }
        }
    
    def test_validate_file_with_valid_content(self, sample_config, tmp_path):
        """Test validation of valid file"""
        # Create test file
        test_file = tmp_path / "README.md"
        test_file.write_text("""# Project README

## Purpose
This is a comprehensive purpose section that explains what this project
does and why it exists. It has enough words to pass validation.

## Testing
Run tests with pytest command.
""")
        
        with patch.object(UnifiedDocumentValidator, '_load_config', return_value=sample_config):
            validator = UnifiedDocumentValidator()
            result = validator.validate_file(test_file)
        
        assert result.valid is True
        assert result.score == 100.0
        assert len(result.issues) == 0
    
    def test_validate_file_with_missing_sections(self, sample_config, tmp_path):
        """Test validation with missing sections"""
        test_file = tmp_path / "README.md"
        test_file.write_text("""# Project README

## Purpose
Short purpose.
""")
        
        with patch.object(UnifiedDocumentValidator, '_load_config', return_value=sample_config):
            validator = UnifiedDocumentValidator()
            result = validator.validate_file(test_file)
        
        assert result.valid is False
        assert "Missing required section: Testing" in result.issues
        assert result.score < 100.0
    
    def test_section_exemptions(self, sample_config, tmp_path):
        """Test that section exemptions work"""
        # Create test file in exempted directory
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        test_file = test_dir / "README.md"
        test_file.write_text("""# Tests README

## Purpose
This is the test directory with comprehensive test purpose explanation.
""")
        
        with patch.object(UnifiedDocumentValidator, '_load_config', return_value=sample_config):
            validator = UnifiedDocumentValidator()
            # Mock the relative path to return 'tests'
            with patch.object(validator, '_get_relative_path') as mock_path:
                # Return file path for file, directory path for parent
                def side_effect(p):
                    if p == test_file:
                        return "tests/README.md"
                    elif p == test_file.parent:
                        return "tests"
                    return str(p)
                mock_path.side_effect = side_effect
                
                result = validator.validate_file(test_file)
        
        assert result.valid is True
        assert "section:Testing" in result.exemptions
    
    def test_validate_path_for_exempted_directory(self, sample_config):
        """Test checking if directory needs README"""
        with patch.object(UnifiedDocumentValidator, '_load_config', return_value=sample_config):
            validator = UnifiedDocumentValidator()
            
            # Check exempted directory
            result = validator.validate_path(Path("node_modules"))
            assert result['readme_required'] is False
            assert "External deps" in result['reason']
            
            # Check non-exempted directory
            result = validator.validate_path(Path("src"))
            assert result['readme_required'] is True
    
    def test_compatibility_interface(self, sample_config):
        """Test backward compatibility with old validator interface"""
        with patch.object(UnifiedDocumentValidator, '_load_config', return_value=sample_config):
            validator = UnifiedDocumentValidator()
            
            # Check required attributes exist
            assert hasattr(validator, 'enforcement_mode')
            assert validator.enforcement_mode == 'progressive'
            
            # Check methods exist
            assert hasattr(validator, 'validate_staged_files')
            assert hasattr(validator, 'validate_file')
            assert hasattr(validator, 'validate_path')
    
    def test_score_calculation(self, sample_config, tmp_path):
        """Test that score is calculated as percentage correctly"""
        test_file = tmp_path / "README.md"
        test_file.write_text("""# README

## Purpose
This has a good purpose section with plenty of explanation about what this does.
""")
        
        with patch.object(UnifiedDocumentValidator, '_load_config', return_value=sample_config):
            validator = UnifiedDocumentValidator()
            result = validator.validate_file(test_file)
        
        # Should have partial score (Purpose found, Testing missing)
        # Purpose is 30 weight, Testing is 30 weight, so should get 30/60 = 50%
        assert result.score == 50.0  # Not 5000%!
        assert 0 <= result.score <= 100