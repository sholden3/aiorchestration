"""
@fileoverview Living document validation for governance system
@author Dr. Sarah Chen v1.0 & Lisa Anderson v1.0 - 2025-08-29
@architecture Backend - Document validation layer
@responsibility Validate living documents are current and properly formatted
@dependencies yaml, datetime, pathlib, typing
@integration_points Governance hooks, pre-commit validation
@testing_strategy Unit tests for validation logic, integration tests with hooks
@governance Ensures documentation remains living and accurate

Business Logic Summary:
- Validate document correlation IDs
- Check staleness based on update frequency
- Verify required sections exist
- Ensure auto-generated sections aren't manually edited
- Track documentation debt

Architecture Integration:
- Called by pre-commit hooks
- Validates living documents on every commit
- Updates correlation IDs automatically
- Blocks commits if documents stale
- Generates documentation debt reports

Sarah's Framework Check:
- What breaks first: YAML parsing on malformed frontmatter
- How we know: Validation exceptions in pre-commit
- Plan B: Graceful degradation with warnings
"""

import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import re
import json


class DocumentValidator:
    """
    Validates living documents according to governance requirements
    """
    
    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()
        self.living_docs_path = self.repo_root / "docs" / "living"
        
        # Document update requirements (in days)
        self.update_frequencies = {
            "CURRENT_ARCHITECTURE.md": 7,  # Weekly
            "IMPLEMENTED_FEATURES.md": 3,  # Per feature
            "UPCOMING_FEATURES.md": 14,  # Per sprint
            "ACTIVE_MOCKS.md": 7,  # Weekly
            "PHASE_PLAN.md": 3,  # Frequently during active phase
        }
        
        # Required sections per document
        self.required_sections = {
            "CURRENT_ARCHITECTURE.md": [
                "Component Status",
                "System Components", 
                "Integration Points",
                "Performance Metrics",
                "Risk Assessment"
            ],
            "IMPLEMENTED_FEATURES.md": [
                "Core Features",
                "Feature Flags",
                "Test Coverage Report",
                "Known Issues",
                "Feature Stability Matrix"
            ],
            "UPCOMING_FEATURES.md": [
                "Sprint Summary",
                "Priority 1: Critical Path Features",
                "Risk Assessment",
                "Dependencies Status"
            ],
            "ACTIVE_MOCKS.md": [
                "Active Mocks",
                "Mock Inventory",
                "Technical Debt Assessment",
                "Migration Timeline"
            ],
            "PHASE_PLAN.md": [
                "Phase Group Summary",
                "Success Metrics",
                "Risk Register"
            ]
        }
        
        self.validation_errors = []
        self.validation_warnings = []
    
    def validate_all_documents(self) -> Tuple[bool, List[str], List[str]]:
        """
        Validate all living documents
        
        @returns (is_valid, errors, warnings)
        """
        self.validation_errors = []
        self.validation_warnings = []
        
        if not self.living_docs_path.exists():
            self.validation_errors.append(
                f"Living documents directory not found: {self.living_docs_path}"
            )
            return False, self.validation_errors, self.validation_warnings
        
        # Check each required document
        for doc_name, max_age_days in self.update_frequencies.items():
            doc_path = self.living_docs_path / doc_name
            
            if not doc_path.exists():
                self.validation_errors.append(
                    f"Required document missing: {doc_name}"
                )
                continue
            
            # Validate individual document
            self._validate_document(doc_path, max_age_days)
        
        return len(self.validation_errors) == 0, self.validation_errors, self.validation_warnings
    
    def _validate_document(self, doc_path: Path, max_age_days: int):
        """
        Validate a single document
        """
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract YAML frontmatter
            frontmatter = self._extract_frontmatter(content)
            if not frontmatter:
                self.validation_errors.append(
                    f"{doc_path.name}: Missing YAML frontmatter"
                )
                return
            
            # Validate frontmatter
            self._validate_frontmatter(doc_path.name, frontmatter, max_age_days)
            
            # Validate required sections
            self._validate_sections(doc_path.name, content)
            
            # Check auto-generated sections
            self._validate_auto_sections(doc_path.name, content, frontmatter)
            
        except Exception as e:
            self.validation_errors.append(
                f"{doc_path.name}: Failed to validate - {str(e)}"
            )
    
    def _extract_frontmatter(self, content: str) -> Optional[Dict]:
        """
        Extract YAML frontmatter from document
        """
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None
        
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return None
    
    def _validate_frontmatter(self, doc_name: str, frontmatter: Dict, max_age_days: int):
        """
        Validate frontmatter contains required fields
        """
        if 'governance' not in frontmatter:
            self.validation_errors.append(
                f"{doc_name}: Missing 'governance' section in frontmatter"
            )
            return
        
        gov = frontmatter['governance']
        
        # Check required fields
        required_fields = [
            'correlation_id',
            'last_updated',
            'update_required_by',
            'validation_schema'
        ]
        
        for field in required_fields:
            if field not in gov:
                self.validation_errors.append(
                    f"{doc_name}: Missing required field '{field}' in governance"
                )
        
        # Check staleness
        if 'last_updated' in gov:
            try:
                last_updated = datetime.fromisoformat(gov['last_updated'].replace('Z', '+00:00'))
                age_days = (datetime.now(last_updated.tzinfo) - last_updated).days
                
                if age_days > max_age_days:
                    self.validation_errors.append(
                        f"{doc_name}: Document is stale (last updated {age_days} days ago, max {max_age_days})"
                    )
                elif age_days > max_age_days * 0.8:
                    self.validation_warnings.append(
                        f"{doc_name}: Document approaching staleness (last updated {age_days} days ago)"
                    )
            except (ValueError, TypeError):
                self.validation_errors.append(
                    f"{doc_name}: Invalid last_updated timestamp"
                )
        
        # Validate correlation ID format
        if 'correlation_id' in gov:
            if not re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$|^ARCH-[A-Z]+-\d{3}$', 
                          gov['correlation_id']):
                self.validation_warnings.append(
                    f"{doc_name}: Non-standard correlation ID format"
                )
    
    def _validate_sections(self, doc_name: str, content: str):
        """
        Validate required sections exist
        """
        if doc_name not in self.required_sections:
            return
        
        for section in self.required_sections[doc_name]:
            # Check for section header (## or ###)
            pattern = rf'#{2,3}\s+{re.escape(section)}'
            if not re.search(pattern, content, re.MULTILINE):
                self.validation_errors.append(
                    f"{doc_name}: Missing required section '{section}'"
                )
    
    def _validate_auto_sections(self, doc_name: str, content: str, frontmatter: Dict):
        """
        Validate auto-generated sections haven't been manually edited
        """
        gov = frontmatter.get('governance', {})
        auto_sections = gov.get('auto_sections', [])
        
        if not auto_sections:
            return
        
        # Find all auto-generated blocks
        auto_blocks = re.findall(
            r'<!-- AUTO-GENERATED - DO NOT EDIT -->.*?<!-- END AUTO-GENERATED -->',
            content,
            re.DOTALL
        )
        
        # Check if any auto blocks have been tampered with
        for block in auto_blocks:
            lines = block.split('\n')
            if len(lines) < 3:
                continue
            
            # Check for common signs of manual editing
            for line in lines[1:-1]:  # Skip markers
                if any(word in line.lower() for word in ['todo', 'fixme', 'xxx', 'hack']):
                    self.validation_warnings.append(
                        f"{doc_name}: Possible manual edit in auto-generated section"
                    )
                    break
    
    def update_correlation_id(self, doc_path: Path, correlation_id: str) -> bool:
        """
        Update the correlation ID in a document
        
        @param doc_path Path to document
        @param correlation_id New correlation ID
        @returns Success status
        """
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update correlation ID in frontmatter
            content = re.sub(
                r'(correlation_id:\s*)[^\n]+',
                f'\\1{correlation_id}',
                content
            )
            
            # Update last_updated timestamp
            now = datetime.now().isoformat() + 'Z'
            content = re.sub(
                r'(last_updated:\s*)[^\n]+',
                f'\\1{now}',
                content
            )
            
            # Update update_required_by
            update_freq = self.update_frequencies.get(doc_path.name, 7)
            next_update = (datetime.now() + timedelta(days=update_freq)).isoformat() + 'Z'
            content = re.sub(
                r'(update_required_by:\s*)[^\n]+',
                f'\\1{next_update}',
                content
            )
            
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"Failed to update correlation ID: {e}")
            return False
    
    def calculate_documentation_debt(self) -> Dict[str, Any]:
        """
        Calculate documentation debt score
        
        @returns Debt metrics
        """
        debt_score = 0
        max_score = 100
        
        # Check document existence (20 points)
        missing_docs = 0
        for doc_name in self.update_frequencies.keys():
            if not (self.living_docs_path / doc_name).exists():
                missing_docs += 1
        
        doc_existence_score = max(0, 20 - (missing_docs * 4))
        debt_score += doc_existence_score
        
        # Check staleness (30 points)
        stale_docs = sum(1 for error in self.validation_errors if 'stale' in error.lower())
        staleness_score = max(0, 30 - (stale_docs * 10))
        debt_score += staleness_score
        
        # Check completeness (30 points)
        missing_sections = sum(1 for error in self.validation_errors if 'Missing required section' in error)
        completeness_score = max(0, 30 - (missing_sections * 3))
        debt_score += completeness_score
        
        # Check quality (20 points)
        quality_issues = len(self.validation_warnings)
        quality_score = max(0, 20 - (quality_issues * 2))
        debt_score += quality_score
        
        return {
            "total_score": debt_score,
            "max_score": max_score,
            "percentage": (debt_score / max_score) * 100,
            "doc_existence": doc_existence_score,
            "staleness": staleness_score,
            "completeness": completeness_score,
            "quality": quality_score,
            "grade": self._score_to_grade(debt_score),
            "errors": len(self.validation_errors),
            "warnings": len(self.validation_warnings)
        }
    
    def _score_to_grade(self, score: int) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def generate_report(self) -> str:
        """
        Generate validation report
        
        @returns Formatted report
        """
        report = ["=" * 60]
        report.append("LIVING DOCUMENT VALIDATION REPORT")
        report.append("=" * 60)
        
        is_valid, errors, warnings = self.validate_all_documents()
        
        report.append(f"\nStatus: {'✅ VALID' if is_valid else '❌ INVALID'}")
        report.append(f"Errors: {len(errors)}")
        report.append(f"Warnings: {len(warnings)}")
        
        if errors:
            report.append("\n🔴 ERRORS (must fix):")
            for error in errors:
                report.append(f"  - {error}")
        
        if warnings:
            report.append("\n🟡 WARNINGS (should fix):")
            for warning in warnings:
                report.append(f"  - {warning}")
        
        # Calculate debt
        debt = self.calculate_documentation_debt()
        report.append(f"\n📊 DOCUMENTATION DEBT SCORE: {debt['total_score']}/{debt['max_score']} ({debt['grade']})")
        report.append(f"  - Document Existence: {debt['doc_existence']}/20")
        report.append(f"  - Freshness: {debt['staleness']}/30")
        report.append(f"  - Completeness: {debt['completeness']}/30")
        report.append(f"  - Quality: {debt['quality']}/20")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)


# Integration with governance hook
def validate_living_documents(repo_root: Path = None) -> Tuple[bool, List[str], List[str]]:
    """
    Main entry point for governance integration
    
    @returns (is_valid, errors, warnings)
    """
    validator = DocumentValidator(repo_root)
    return validator.validate_all_documents()


def update_document_correlation_ids(correlation_id: str, repo_root: Path = None) -> bool:
    """
    Update all living documents with new correlation ID
    
    @param correlation_id New correlation ID
    @returns Success status
    """
    validator = DocumentValidator(repo_root)
    success = True
    
    for doc_name in validator.update_frequencies.keys():
        doc_path = validator.living_docs_path / doc_name
        if doc_path.exists():
            if not validator.update_correlation_id(doc_path, correlation_id):
                success = False
    
    return success