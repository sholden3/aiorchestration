"""
Unit tests for Documentation Validator
Created: 2025-09-03
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from governance.validators.doc_validator import DocumentationValidator, ValidationResult


class TestDocumentationValidator:
    """Test suite for documentation validator"""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance with test config"""
        with patch('governance.validators.doc_validator.Path.exists', return_value=False):
            return DocumentationValidator()
    
    @pytest.fixture
    def sample_doc(self):
        """Sample valid documentation content"""
        return """# Test Document

**Last Updated**: 2025-09-03  
**Status**: Active  

## Overview

This is a test document with proper structure.

## Components

- Component A
- Component B

## Data Flow

Data flows from A to B.
"""
    
    @pytest.fixture
    def invalid_doc(self):
        """Sample invalid documentation content"""
        return """This document has no title or structure.
Just some random text without proper markdown.
"""
    
    def test_validator_initialization(self):
        """Test validator initializes with default config"""
        with patch('governance.validators.doc_validator.Path.exists', return_value=False):
            validator = DocumentationValidator()
            assert validator.config is not None
            assert validator.enforcement_mode == 'warnings_only'
    
    def test_validate_missing_file(self, validator):
        """Test validation of non-existent file"""
        result = validator.validate_file(Path("nonexistent.md"))
        assert not result.is_valid
        assert result.score == 0.0
        assert any(v['type'] == 'file_not_found' for v in result.violations)
    
    def test_validate_valid_document(self, validator, sample_doc):
        """Test validation of properly formatted document"""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value=sample_doc):
                result = validator.validate_file(Path("test.md"))
                assert result.is_valid
                assert result.score > 0.7
                assert len(result.violations) == 0
    
    def test_validate_invalid_document(self, validator, invalid_doc):
        """Test validation catches missing title"""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value=invalid_doc):
                result = validator.validate_file(Path("test.md"))
                assert not result.is_valid
                assert any(v['type'] == 'missing_title' for v in result.violations)
    
    def test_validate_missing_sections(self, validator):
        """Test detection of missing required sections"""
        doc = """# Architecture Document
        
Some content but missing required sections.
"""
        # Mock the config to require specific sections
        validator.config = {
            'global': {'common_requirements': ['must_have_title']},
            'document_types': {
                'architecture': {
                    'path_pattern': 'docs/architecture/*.md',
                    'required_sections': ['## Overview', '## Components']
                }
            },
            'scoring': {'pass_threshold': 0.7}
        }
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value=doc):
                with patch.object(validator, '_determine_doc_type', return_value='architecture'):
                    result = validator.validate_file(Path("docs/architecture/test.md"))
                    assert not result.is_valid
                    assert any(v['type'] == 'missing_required_section' for v in result.violations)
    
    def test_validate_broken_links(self, validator):
        """Test detection of broken internal links"""
        doc = """# Document with Links
        
See [broken link](./nonexistent.md) for details.
"""
        with patch('pathlib.Path.exists', side_effect=[True, False]):  # File exists, link doesn't
            with patch('pathlib.Path.read_text', return_value=doc):
                result = validator.validate_file(Path("test.md"))
                assert any(v['type'] == 'broken_link' for v in result.violations)
    
    def test_score_calculation(self, validator):
        """Test score calculation based on violations"""
        result = ValidationResult(
            file_path="test.md",
            is_valid=True,
            score=1.0
        )
        
        # Add violations with different severities
        result.violations.append({'severity': 'critical', 'type': 'test'})
        result.violations.append({'severity': 'major', 'type': 'test'})
        result.warnings.append('Warning 1')
        
        score = validator._calculate_score(result)
        assert 0 <= score <= 1
        assert score < 1.0  # Should be less than perfect due to violations
    
    def test_enforcement_modes(self):
        """Test different enforcement modes"""
        config = {
            'global': {
                'enabled': True,
                'enforcement_mode': 'strict'
            },
            'scoring': {'pass_threshold': 0.9}
        }
        
        with patch('builtins.open', mock_open(read_data=str(config))):
            with patch('yaml.safe_load', return_value=config):
                with patch('pathlib.Path.exists', return_value=True):
                    validator = DocumentationValidator()
                    assert validator.enforcement_mode == 'strict'
    
    def test_validate_directory(self, validator):
        """Test validation of multiple files in directory"""
        # Set up exemption config
        validator.config = {
            'exemptions': {
                'exempt_files': ['*.archive/*', 'temp/*', 'node_modules/*']
            },
            'scoring': {'pass_threshold': 0.7}
        }
        
        mock_files = [
            Path("docs/test1.md"),
            Path("docs/test2.md"),
            Path("docs/.archive/old.md")  # Should be exempted
        ]
        
        with patch.object(Path, 'glob', return_value=mock_files):
            with patch.object(validator, 'validate_file') as mock_validate:
                mock_validate.return_value = ValidationResult(
                    file_path="test.md",
                    is_valid=True,
                    score=0.8
                )
                
                results = validator.validate_directory(Path("docs"))
                
                # Should only validate non-exempted files
                assert len(results) == 2
                assert mock_validate.call_count == 2
    
    def test_generate_report(self, validator):
        """Test report generation from validation results"""
        results = [
            ValidationResult(
                file_path="doc1.md",
                is_valid=True,
                score=0.95,
                suggestions=["Excellent documentation!"]
            ),
            ValidationResult(
                file_path="doc2.md",
                is_valid=False,
                score=0.6,
                violations=[{'severity': 'critical', 'message': 'Missing title'}],
                warnings=["Missing date"]
            )
        ]
        
        report = validator.generate_report(results)
        
        assert "Documentation Validation Report" in report
        assert "doc1.md" in report
        assert "doc2.md" in report
        assert "✅" in report  # Valid doc
        assert "❌" in report  # Invalid doc
        assert "Missing title" in report
    
    def test_markdown_syntax_validation(self, validator):
        """Test markdown syntax validation"""
        doc = """# Title

### Skipped Heading Level

Content with trailing space 
"""
        result = ValidationResult(
            file_path="test.md",
            is_valid=True,
            score=1.0
        )
        
        validator._validate_markdown_syntax(doc, result)
        
        assert any("Heading hierarchy skip" in w for w in result.warnings)
        assert any("Trailing whitespace" in w for w in result.warnings)
    
    def test_document_type_detection(self, validator):
        """Test correct document type detection"""
        validator.config = {
            'document_types': {
                'architecture': {'path_pattern': 'docs/architecture/*.md'},
                'api': {'path_pattern': 'docs/api/*.md'},
                'readme': {'path_pattern': '**/README.md'}
            }
        }
        
        assert validator._determine_doc_type(Path('docs/architecture/system.md')) == 'architecture'
        assert validator._determine_doc_type(Path('docs/api/endpoints.md')) == 'api'
        assert validator._determine_doc_type(Path('project/README.md')) == 'readme'
        assert validator._determine_doc_type(Path('random/file.md')) is None
    
    def test_exemption_checking(self, validator):
        """Test file exemption logic"""
        validator.config = {
            'exemptions': {
                'exempt_files': [
                    '*.archive/*',
                    'temp/*',
                    'node_modules/*'
                ]
            }
        }
        
        assert validator._is_exempted(Path('.archive/old.md'))
        assert validator._is_exempted(Path('temp/working.md'))
        assert validator._is_exempted(Path('node_modules/package/README.md'))
        assert not validator._is_exempted(Path('docs/valid.md'))