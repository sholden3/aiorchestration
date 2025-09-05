#!/usr/bin/env python3
"""
@fileoverview Relaxed living document validator with advisory mode
@author Round Table Consensus v2.0 - 2025-08-29
@architecture Backend - Document validation layer (Advisory Mode)
@responsibility Provide helpful guidance for living documents without blocking
@dependencies yaml, datetime, pathlib, typing, re
@integration_points Governance hooks, pre-commit validation (non-blocking)
@testing_strategy Unit tests for suggestions, integration tests for advisory mode
@governance Implements Phase 2 progressive enforcement per round table decision

Business Logic Summary:
- Advisory validation only - no blocking
- Content accuracy over format compliance
- Progressive requirements based on project phase
- Helpful suggestions instead of strict errors
- Focus on staleness and accuracy, not structure

Architecture Integration:
- Called by pre-commit hooks in advisory mode
- Never blocks commits (except secrets)
- Provides suggestions logged separately
- Supports progressive phase enforcement
- Generates helpful improvement reports

Round Table Decision:
- Unanimous agreement to relax requirements
- Advisory mode for Phase 2
- Content validation prioritized
- Progressive enforcement strategy
"""

import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from enum import Enum
import re
import json
import os


class Severity(Enum):
    """Validation severity levels"""
    INFO = "info"
    SUGGESTION = "suggestion"
    WARNING = "warning"
    ERROR = "error"  # Only for critical issues like secrets
    BLOCKING = "blocking"  # Almost never used in Phase 2


class ValidationMessage:
    """A validation message with severity and context"""
    
    def __init__(self, severity: Severity, message: str, file: str = None, 
                 line: int = None, suggestion: str = None):
        self.severity = severity
        self.message = message
        self.file = file
        self.line = line
        self.suggestion = suggestion
    
    def __str__(self):
        prefix = {
            Severity.INFO: "ℹ️",
            Severity.SUGGESTION: "💡",
            Severity.WARNING: "⚠️",
            Severity.ERROR: "❌",
            Severity.BLOCKING: "🚫"
        }.get(self.severity, "")
        
        location = f"{self.file}:{self.line}: " if self.file and self.line else ""
        base = f"{prefix} {location}{self.message}"
        
        if self.suggestion:
            base += f"\n   Suggestion: {self.suggestion}"
        
        return base


class RelaxedDocumentValidator:
    """
    Relaxed validator for living documents - Advisory Mode
    Based on Round Table Consensus 2025-08-29
    """
    
    def __init__(self, repo_root: Path = None, phase: int = 2):
        self.repo_root = repo_root or Path.cwd()
        self.living_docs_path = self.repo_root / "docs" / "living"
        self.phase = phase  # Current project phase
        
        # Load configuration
        self.config_path = self.repo_root / "governance-config" / "living-docs.yml"
        self.config = self._load_config()
        
        # Messages collected during validation
        self.messages: List[ValidationMessage] = []
        
        # Phase-based requirements (very relaxed for Phase 2)
        self.phase_requirements = {
            2: {  # Current - Advisory only
                "required": ["title", "content"],
                "recommended": ["last_updated"],
                "optional": ["yaml_frontmatter", "specific_sections"],
                "staleness_days": 30,
                "blocking": False
            },
            3: {  # Future - Gradual increase
                "required": ["title", "content", "last_updated", "status"],
                "recommended": ["yaml_frontmatter", "key_sections"],
                "optional": ["all_sections"],
                "staleness_days": 14,
                "blocking": False  # Still advisory
            },
            5: {  # Production - Full enforcement
                "required": ["yaml_frontmatter", "all_sections", "correlation_id"],
                "recommended": [],
                "optional": [],
                "staleness_days": 7,
                "blocking": True
            }
        }
    
    def _load_config(self) -> Dict:
        """Load configuration from living-docs.yml"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                # Config issues shouldn't break validation
                self.messages.append(ValidationMessage(
                    Severity.INFO,
                    f"Could not load config: {e}",
                    suggestion="Using default advisory settings"
                ))
        
        # Default advisory config
        return {
            "validation": {
                "mode": "advisory",
                "blocking": {"enabled": False}
            },
            "enforcement_phase": 2
        }
    
    def validate_all_documents(self) -> Tuple[bool, List[str], List[str], List[str]]:
        """
        Validate all living documents in advisory mode
        
        Returns: (should_block, errors, warnings, suggestions)
        Note: should_block is almost always False in Phase 2
        """
        self.messages = []
        
        # Check if living docs directory exists
        if not self.living_docs_path.exists():
            self.messages.append(ValidationMessage(
                Severity.INFO,
                "Living docs directory not found",
                suggestion="Create docs/living/ when you have living documentation"
            ))
            return False, [], [], ["Consider creating living documentation"]
        
        # Validate each document
        doc_files = list(self.living_docs_path.glob("*.md"))
        
        if not doc_files:
            self.messages.append(ValidationMessage(
                Severity.INFO,
                "No living documents found yet",
                suggestion="Living docs will help track project evolution"
            ))
            return False, [], [], []
        
        for doc_file in doc_files:
            self._validate_document(doc_file)
        
        # Categorize messages
        errors = [str(m) for m in self.messages if m.severity == Severity.ERROR]
        warnings = [str(m) for m in self.messages if m.severity == Severity.WARNING]
        suggestions = [str(m) for m in self.messages if m.severity in [Severity.SUGGESTION, Severity.INFO]]
        
        # Check for blocking issues (very rare in Phase 2)
        should_block = any(m.severity == Severity.BLOCKING for m in self.messages)
        
        # In Phase 2, we almost never block
        if self.phase == 2 and not self._contains_secrets():
            should_block = False
        
        return should_block, errors, warnings, suggestions
    
    def _validate_document(self, doc_path: Path):
        """Validate a single document"""
        doc_name = doc_path.name
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.messages.append(ValidationMessage(
                Severity.WARNING,
                f"Could not read {doc_name}: {e}",
                doc_name
            ))
            return
        
        # Phase 2: Only check the basics
        if self.phase <= 2:
            self._check_basic_content(doc_path, content)
            self._check_staleness(doc_path, content)
            self._check_accuracy_hints(doc_path, content)
        
        # Phase 3+: Add more checks
        elif self.phase >= 3:
            self._check_basic_content(doc_path, content)
            self._check_staleness(doc_path, content)
            self._check_structure(doc_path, content)
            self._check_references(doc_path, content)
            self._check_accuracy_hints(doc_path, content)
    
    def _check_basic_content(self, doc_path: Path, content: str):
        """Check basic content requirements"""
        doc_name = doc_path.name
        
        # Must have a title
        if not content.strip():
            self.messages.append(ValidationMessage(
                Severity.WARNING,
                f"{doc_name} is empty",
                doc_name,
                suggestion="Add content to track project state"
            ))
            return
        
        lines = content.split('\n')
        
        # Check for title (any heading)
        has_title = any(line.strip().startswith('#') for line in lines[:10])
        if not has_title:
            self.messages.append(ValidationMessage(
                Severity.SUGGESTION,
                f"{doc_name} missing title",
                doc_name,
                suggestion="Add a # Title at the top"
            ))
        
        # Check for some content
        non_empty_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        if len(non_empty_lines) < 3:
            self.messages.append(ValidationMessage(
                Severity.SUGGESTION,
                f"{doc_name} has very little content",
                doc_name,
                suggestion="Add more details to make this useful"
            ))
    
    def _check_staleness(self, doc_path: Path, content: str):
        """Check if document is stale"""
        doc_name = doc_path.name
        
        # Look for last updated date (any format)
        date_patterns = [
            r'last[_\s-]?updated?:?\s*([^\n]+)',
            r'updated?:?\s*([^\n]+)',
            r'date:?\s*([^\n]+)',
            r'\*\*Date\*\*:?\s*([^\n]+)',
        ]
        
        last_updated = None
        for pattern in date_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                # Try to parse the date (be lenient)
                try:
                    # Try various formats
                    for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y', 
                               '%B %d, %Y', '%b %d, %Y', '%Y-%b-%d']:
                        try:
                            last_updated = datetime.strptime(date_str[:10], fmt)
                            break
                        except:
                            continue
                except:
                    pass
                
                if last_updated:
                    break
        
        # If we found a date, check staleness
        if last_updated:
            days_old = (datetime.now() - last_updated).days
            max_days = self.phase_requirements[self.phase].get("staleness_days", 30)
            
            if days_old > max_days:
                self.messages.append(ValidationMessage(
                    Severity.WARNING,
                    f"{doc_name} is {days_old} days old",
                    doc_name,
                    suggestion=f"Consider updating (recommended every {max_days} days)"
                ))
            elif days_old > max_days // 2:
                self.messages.append(ValidationMessage(
                    Severity.INFO,
                    f"{doc_name} last updated {days_old} days ago",
                    doc_name
                ))
        else:
            # No date found - just suggest adding one
            self.messages.append(ValidationMessage(
                Severity.SUGGESTION,
                f"{doc_name} missing last updated date",
                doc_name,
                suggestion="Add 'Last Updated: YYYY-MM-DD' for tracking"
            ))
    
    def _check_structure(self, doc_path: Path, content: str):
        """Check document structure (Phase 3+)"""
        doc_name = doc_path.name
        
        # Only suggest structure, don't require it
        if doc_name == "CURRENT_ARCHITECTURE.md":
            sections = ["Status", "Components", "Integration"]
            for section in sections:
                if section.lower() not in content.lower():
                    self.messages.append(ValidationMessage(
                        Severity.SUGGESTION,
                        f"Consider adding '{section}' section",
                        doc_name
                    ))
    
    def _check_references(self, doc_path: Path, content: str):
        """Check internal references (Phase 3+)"""
        doc_name = doc_path.name
        
        # Find markdown links
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        links = re.findall(link_pattern, content)
        
        for link_text, link_url in links:
            if link_url.startswith('#'):
                # Internal anchor - check if exists
                anchor = link_url[1:].lower().replace('-', ' ')
                if anchor not in content.lower():
                    self.messages.append(ValidationMessage(
                        Severity.INFO,
                        f"Internal link '{link_url}' might be broken",
                        doc_name,
                        suggestion="Verify anchor exists"
                    ))
    
    def _check_accuracy_hints(self, doc_path: Path, content: str):
        """Look for potential accuracy issues"""
        doc_name = doc_path.name
        
        # Check for TODO/FIXME markers
        todo_pattern = r'(TODO|FIXME|XXX|HACK)[:;\s]'
        todos = re.findall(todo_pattern, content, re.IGNORECASE)
        
        if todos:
            self.messages.append(ValidationMessage(
                Severity.INFO,
                f"{doc_name} has {len(todos)} TODO markers",
                doc_name,
                suggestion="Consider completing or removing TODOs"
            ))
        
        # Check for outdated version numbers (heuristic)
        version_pattern = r'v?(\d+)\.(\d+)\.(\d+)'
        versions = re.findall(version_pattern, content)
        
        for major, minor, patch in versions:
            if int(major) > 50:  # Probably not a real version
                self.messages.append(ValidationMessage(
                    Severity.INFO,
                    f"Unusual version number v{major}.{minor}.{patch}",
                    doc_name,
                    suggestion="Verify version number is correct"
                ))
    
    def _contains_secrets(self) -> bool:
        """Check if any document contains potential secrets"""
        # This is one of the few things that can block in Phase 2
        secret_patterns = [
            r'(api[_-]?key|apikey)\s*[:=]\s*["\'][\w\-]+["\']',
            r'(secret|password|pwd|token)\s*[:=]\s*["\'][\w\-]+["\']',
            r'-----BEGIN (RSA |EC )?PRIVATE KEY-----',
            r'[a-zA-Z0-9+/]{40,}={0,2}'  # Base64 encoded secrets
        ]
        
        for msg in self.messages:
            if any(pattern in ['secret', 'password', 'key', 'token'] 
                   for pattern in str(msg).lower()):
                return True
        
        return False
    
    def format_report(self) -> str:
        """Format validation report for console output"""
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append(f"LIVING DOCUMENTATION VALIDATION (Advisory Mode - Phase {self.phase})")
        lines.append("=" * 70)
        lines.append("")
        
        # Categorize messages
        blocking = [m for m in self.messages if m.severity == Severity.BLOCKING]
        errors = [m for m in self.messages if m.severity == Severity.ERROR]
        warnings = [m for m in self.messages if m.severity == Severity.WARNING]
        suggestions = [m for m in self.messages if m.severity == Severity.SUGGESTION]
        info = [m for m in self.messages if m.severity == Severity.INFO]
        
        # Show messages by category
        if blocking:
            lines.append("🚫 BLOCKING ISSUES (Must Fix):")
            for msg in blocking:
                lines.append(f"  {msg}")
            lines.append("")
        
        if errors:
            lines.append("❌ ERRORS (Should Fix):")
            for msg in errors:
                lines.append(f"  {msg}")
            lines.append("")
        
        if warnings:
            lines.append("⚠️  WARNINGS (Consider Fixing):")
            for msg in warnings[:5]:  # Limit to 5
                lines.append(f"  {msg}")
            if len(warnings) > 5:
                lines.append(f"  ... and {len(warnings) - 5} more warnings")
            lines.append("")
        
        if suggestions:
            lines.append("💡 SUGGESTIONS (Optional):")
            for msg in suggestions[:3]:  # Limit to 3
                lines.append(f"  {msg}")
            if len(suggestions) > 3:
                lines.append(f"  ... and {len(suggestions) - 3} more suggestions")
            lines.append("")
        
        if info:
            lines.append("ℹ️  INFO:")
            for msg in info[:2]:  # Limit to 2
                lines.append(f"  {msg}")
            if len(info) > 2:
                lines.append(f"  ... and {len(info) - 2} more info items")
            lines.append("")
        
        # Summary
        lines.append("-" * 70)
        if blocking:
            lines.append("❌ COMMIT BLOCKED - Fix blocking issues above")
        elif errors:
            lines.append("⚠️  Errors found but NOT blocking (Phase 2 advisory mode)")
        elif warnings:
            lines.append("✅ No blocking issues (warnings are advisory only)")
        else:
            lines.append("✅ Looking good! Only suggestions found")
        
        lines.append("")
        lines.append("This is ADVISORY only. Your commit will proceed.")
        lines.append("Full report: .governance/living-docs-suggestions.log")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def save_suggestions(self):
        """Save detailed suggestions to log file"""
        log_dir = self.repo_root / ".governance"
        log_dir.mkdir(exist_ok=True)
        
        suggestions_file = log_dir / "living-docs-suggestions.log"
        
        with open(suggestions_file, 'w') as f:
            f.write(f"Living Documentation Suggestions - {datetime.now()}\n")
            f.write("=" * 70 + "\n\n")
            
            for msg in self.messages:
                f.write(f"{msg}\n\n")
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("These are suggestions only. Implementation is optional.\n")


def update_document_correlation_ids(correlation_id: str):
    """
    Update correlation IDs in living documents
    (Placeholder for future implementation)
    """
    # In Phase 2, this is optional
    pass


def main():
    """Test the relaxed validator"""
    import sys
    
    validator = RelaxedDocumentValidator()
    should_block, errors, warnings, suggestions = validator.validate_all_documents()
    
    print(validator.format_report())
    validator.save_suggestions()
    
    # In Phase 2, we almost never block
    sys.exit(1 if should_block else 0)


if __name__ == "__main__":
    main()