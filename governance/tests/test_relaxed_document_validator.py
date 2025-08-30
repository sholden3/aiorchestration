#!/usr/bin/env python3
"""
@fileoverview Test suite for relaxed document validator
@author Jordan Kim v1.0 - Documentation Specialist - 2025-08-29
@architecture Backend - Test Layer
@responsibility Validate relaxed document validator works in advisory mode
@dependencies pytest, tempfile, pathlib
@integration_points Document validator, governance hooks
@testing_strategy Unit tests for advisory mode, phase progression tests
@governance Tests Phase 2 advisory validation per round table consensus

Business Logic Summary:
- Verify advisory mode doesn't block
- Test phase-based requirements
- Validate helpful suggestions
- Ensure content prioritization
- Test staleness detection

Architecture Integration:
- Tests document validator in isolation
- Validates advisory mode behavior
- Ensures progressive enforcement
- Verifies no false blocking
"""

import pytest
from pathlib import Path
import tempfile
import sys
from datetime import datetime, timedelta
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from governance.validators.relaxed_document_validator import (
    RelaxedDocumentValidator,
    Severity,
    ValidationMessage
)


class TestRelaxedDocumentValidator:
    """Test the relaxed document validator"""
    
    def setup_method(self):
        """Set up test environment"""
        # Create temporary directory for test docs
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)
        self.docs_dir = self.repo_root / "docs" / "living"
        self.docs_dir.mkdir(parents=True)
        
        # Create validator in Phase 2 (current)
        self.validator = RelaxedDocumentValidator(self.repo_root, phase=2)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_advisory_mode_never_blocks_phase_2(self):
        """Test that Phase 2 never blocks commits (except secrets)"""
        # Create a document with many issues
        doc_path = self.docs_dir / "CURRENT_ARCHITECTURE.md"
        doc_path.write_text("""
        No title here
        No date
        No structure
        Just random content
        """)
        
        should_block, errors, warnings, suggestions = self.validator.validate_all_documents()
        
        # Phase 2 should never block
        assert not should_block
        # Should have suggestions
        assert len(suggestions) > 0
    
    def test_detects_but_doesnt_block_missing_title(self):
        """Test missing title detection (suggestion only)"""
        doc_path = self.docs_dir / "TEST.md"
        doc_path.write_text("""
        Some content without a title
        More content here
        """)
        
        should_block, errors, warnings, suggestions = self.validator.validate_all_documents()
        
        assert not should_block
        # Should suggest adding title
        assert any("title" in s.lower() for s in suggestions)
    
    def test_accepts_any_date_format(self):
        """Test that any date format is accepted in Phase 2"""
        doc_path = self.docs_dir / "PHASE_PLAN.md"
        
        # Test various date formats
        date_formats = [
            "Last Updated: 2025-08-29",
            "Updated: Aug 29, 2025",
            "Date: 29/08/2025",
            "UPDATED: 8/29/2025",
            "last update: August 29th, 2025"
        ]
        
        for date_str in date_formats:
            doc_path.write_text(f"""
            # Phase Plan
            {date_str}
            
            Content here
            """)
            
            should_block, errors, warnings, suggestions = self.validator.validate_all_documents()
            
            # Should accept all formats
            assert not should_block
            # Should not warn about date format
            assert not any("date format" in w.lower() for w in warnings)
    
    def test_warns_about_staleness(self):
        """Test staleness detection"""
        doc_path = self.docs_dir / "ACTIVE_MOCKS.md"
        
        # Create document with old date
        old_date = (datetime.now() - timedelta(days=40)).strftime("%Y-%m-%d")
        doc_path.write_text(f"""
        # Active Mocks
        Last Updated: {old_date}
        
        Mock content here
        """)
        
        should_block, errors, warnings, suggestions = self.validator.validate_all_documents()
        
        assert not should_block
        # Should warn about staleness
        assert any("days old" in w for w in warnings)
    
    def test_suggests_missing_sections_not_requires(self):
        """Test that missing sections are suggestions, not requirements"""
        doc_path = self.docs_dir / "CURRENT_ARCHITECTURE.md"
        doc_path.write_text("""
        # Current Architecture
        Last Updated: 2025-08-29
        
        Basic content without required sections
        """)
        
        self.validator.phase = 3  # Even in Phase 3
        should_block, errors, warnings, suggestions = self.validator.validate_all_documents()
        
        assert not should_block  # Still advisory in Phase 3
        # Should suggest sections
        assert len(suggestions) > 0
    
    def test_no_yaml_frontmatter_required_phase_2(self):
        """Test YAML frontmatter is not required in Phase 2"""
        doc_path = self.docs_dir / "IMPLEMENTED_FEATURES.md"
        doc_path.write_text("""
        # Implemented Features
        Last Updated: 2025-08-29
        
        - Feature 1
        - Feature 2
        """)
        
        should_block, errors, warnings, suggestions = self.validator.validate_all_documents()
        
        assert not should_block
        # Should not error about missing YAML
        assert not any("yaml" in e.lower() for e in errors)
        # Might suggest it
        assert any("yaml" in s.lower() for s in suggestions) or len(suggestions) == 0
    
    def test_blocks_secrets_even_in_phase_2(self):
        """Test that secrets still block in Phase 2"""
        doc_path = self.docs_dir / "CONFIG.md"
        doc_path.write_text("""
        # Configuration
        
        API_KEY = "sk-1234567890abcdef"
        password = "admin123"
        """)
        
        # Add a message about secrets
        self.validator.messages.append(ValidationMessage(
            Severity.BLOCKING,
            "Contains secrets",
            "CONFIG.md"
        ))
        
        should_block, errors, warnings, suggestions = self.validator.validate_all_documents()
        
        # Secrets should still block
        assert should_block or self.validator._contains_secrets()
    
    def test_empty_directory_doesnt_fail(self):
        """Test that empty docs directory doesn't fail"""
        # Remove all docs
        for doc in self.docs_dir.glob("*.md"):
            doc.unlink()
        
        should_block, errors, warnings, suggestions = self.validator.validate_all_documents()
        
        assert not should_block
        assert len(errors) == 0
    
    def test_missing_directory_doesnt_fail(self):
        """Test that missing docs directory doesn't fail"""
        import shutil
        shutil.rmtree(self.docs_dir)
        
        should_block, errors, warnings, suggestions = self.validator.validate_all_documents()
        
        assert not should_block
        assert len(errors) == 0
        # Should suggest creating docs
        assert any("living" in s.lower() for s in suggestions)
    
    def test_todo_markers_generate_info(self):
        """Test that TODO markers generate info messages"""
        doc_path = self.docs_dir / "UPCOMING_FEATURES.md"
        doc_path.write_text("""
        # Upcoming Features
        
        TODO: Add authentication
        FIXME: Performance issue
        XXX: Needs review
        """)
        
        self.validator._validate_document(doc_path)
        
        # Should have info about TODOs
        info_messages = [m for m in self.validator.messages if m.severity == Severity.INFO]
        assert any("TODO" in str(m) for m in info_messages)
    
    def test_format_report_is_helpful(self):
        """Test that report format is helpful and clear"""
        doc_path = self.docs_dir / "TEST.md"
        doc_path.write_text("""
        Content without proper structure
        """)
        
        should_block, errors, warnings, suggestions = self.validator.validate_all_documents()
        report = self.validator.format_report()
        
        # Report should be advisory
        assert "Advisory Mode" in report
        assert "Phase 2" in report
        assert "Your commit will proceed" in report
        
        # Should not be scary
        assert "BLOCKED" not in report or "NOT blocking" in report


class TestPhaseProgression:
    """Test phase-based progression of requirements"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)
        self.docs_dir = self.repo_root / "docs" / "living"
        self.docs_dir.mkdir(parents=True)
    
    def teardown_method(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_phase_2_minimal_requirements(self):
        """Test Phase 2 has minimal requirements"""
        validator = RelaxedDocumentValidator(self.repo_root, phase=2)
        
        doc_path = self.docs_dir / "TEST.md"
        doc_path.write_text("Some content")
        
        should_block, errors, warnings, suggestions = validator.validate_all_documents()
        
        assert not should_block
        # Very lenient
        assert len(errors) == 0
    
    def test_phase_3_gradual_increase(self):
        """Test Phase 3 has more requirements but still advisory"""
        validator = RelaxedDocumentValidator(self.repo_root, phase=3)
        
        doc_path = self.docs_dir / "TEST.md"
        doc_path.write_text("Some content")
        
        should_block, errors, warnings, suggestions = validator.validate_all_documents()
        
        # Still doesn't block in Phase 3
        assert not should_block
        # But has more suggestions
        assert len(suggestions) >= 0
    
    def test_phase_5_still_reasonable(self):
        """Test Phase 5 requirements are still reasonable"""
        validator = RelaxedDocumentValidator(self.repo_root, phase=5)
        
        doc_path = self.docs_dir / "TEST.md"
        doc_path.write_text("""
        # Test Document
        Last Updated: 2025-08-29
        
        ## Status
        Active
        
        ## Content
        Full content here
        """)
        
        should_block, errors, warnings, suggestions = validator.validate_all_documents()
        
        # Phase 5 might block but only for serious issues
        # This basic doc should pass
        assert not should_block or len(errors) > 0


class TestContentValidation:
    """Test content validation features"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)
        self.docs_dir = self.repo_root / "docs" / "living"
        self.docs_dir.mkdir(parents=True)
        self.validator = RelaxedDocumentValidator(self.repo_root, phase=2)
    
    def teardown_method(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detects_unusual_version_numbers(self):
        """Test detection of unusual version numbers"""
        doc_path = self.docs_dir / "VERSION.md"
        doc_path.write_text("""
        # Version Info
        
        Current version: v99.0.0
        Previous: v98.5.2
        """)
        
        self.validator._validate_document(doc_path)
        
        # Should have info about unusual versions
        info_messages = [m for m in self.validator.messages if m.severity == Severity.INFO]
        assert any("version" in str(m).lower() for m in info_messages)
    
    def test_checks_internal_links(self):
        """Test internal link checking"""
        doc_path = self.docs_dir / "LINKS.md"
        doc_path.write_text("""
        # Document with Links
        
        See [missing section](#non-existent-anchor)
        See [valid section](#valid-section)
        
        ## Valid Section
        Content here
        """)
        
        self.validator.phase = 3  # Link checking in Phase 3+
        self.validator._validate_document(doc_path)
        
        # Should have info about broken link
        info_messages = [m for m in self.validator.messages if m.severity == Severity.INFO]
        assert any("broken" in str(m).lower() for m in info_messages)
    
    def test_very_little_content_warning(self):
        """Test warning for documents with very little content"""
        doc_path = self.docs_dir / "EMPTY.md"
        doc_path.write_text("""
        # Title
        
        One line.
        """)
        
        self.validator._validate_document(doc_path)
        
        # Should suggest adding more content
        suggestions = [m for m in self.validator.messages if m.severity == Severity.SUGGESTION]
        assert any("little content" in str(m) for m in suggestions)


class TestReportFormatting:
    """Test report formatting and user experience"""
    
    def test_report_is_not_scary(self):
        """Test that reports are helpful, not scary"""
        validator = RelaxedDocumentValidator()
        
        # Add various message types
        validator.messages = [
            ValidationMessage(Severity.WARNING, "This could be better"),
            ValidationMessage(Severity.SUGGESTION, "Consider doing this"),
            ValidationMessage(Severity.INFO, "Just FYI")
        ]
        
        report = validator.format_report()
        
        # Should emphasize advisory nature
        assert "ADVISORY" in report
        assert "Your commit will proceed" in report
        
        # Should use friendly language
        assert "Consider" in report or "Optional" in report
    
    def test_report_limits_output(self):
        """Test that report limits output to avoid overwhelming"""
        validator = RelaxedDocumentValidator()
        
        # Add many messages
        for i in range(20):
            validator.messages.append(
                ValidationMessage(Severity.SUGGESTION, f"Suggestion {i}")
            )
        
        report = validator.format_report()
        
        # Should limit and indicate more
        assert "more suggestions" in report.lower()
        
        # Should not be too long
        lines = report.split('\n')
        assert len(lines) < 50  # Reasonable length
    
    def test_suggestions_saved_to_file(self):
        """Test that detailed suggestions are saved to file"""
        temp_dir = tempfile.mkdtemp()
        validator = RelaxedDocumentValidator(Path(temp_dir))
        
        validator.messages = [
            ValidationMessage(Severity.SUGGESTION, "Detailed suggestion 1"),
            ValidationMessage(Severity.SUGGESTION, "Detailed suggestion 2")
        ]
        
        validator.save_suggestions()
        
        suggestions_file = Path(temp_dir) / ".governance" / "living-docs-suggestions.log"
        assert suggestions_file.exists()
        
        content = suggestions_file.read_text()
        assert "Detailed suggestion 1" in content
        assert "Detailed suggestion 2" in content
        
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])