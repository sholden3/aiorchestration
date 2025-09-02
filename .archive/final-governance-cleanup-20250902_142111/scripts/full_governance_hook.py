#!/usr/bin/env python3
"""
FULL GOVERNANCE PRE-COMMIT HOOK v3.0
=====================================
@fileoverview Complete governance integration with all validators and detectors
@author Alex Novak v3.0 & Dr. Sarah Chen v3.0 - 2025-08-29
@architecture Full governance integration layer
@business_logic Orchestrates all governance validation for comprehensive compliance
@responsibility Orchestrate all governance components for comprehensive validation
@dependencies All governance modules, validators, detectors, trackers
@integration_points Git hooks, CI/CD, IDE plugins, monitoring dashboard
@testing_strategy End-to-end governance validation tests
@governance This is the master governance orchestrator

Business Logic Summary:
- Integrate all governance components
- Run domain-specific validators
- Check magic variables and boilerplate
- Track test execution staleness
- Validate documentation (advisory mode)
- Calculate comprehensive risk scores
- Generate detailed reports

Architecture Integration:
- Central governance orchestrator
- Uses all validators and detectors
- Integrates with correlation tracking
- Provides comprehensive audit trail
- Supports progressive enforcement
"""

import sys
import os
import subprocess
import json
import yaml
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import traceback

# Add governance module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import all governance components
from governance.core.correlation_tracker import get_correlation_tracker, OperationStatus
from governance.core.engine import GovernanceEngine
from governance.core.context import GovernanceContext
from governance.core.enhanced_governance_engine import (
    EnhancedGovernanceEngine,
    MagicVariableDetector,
    TestExecutionTracker,
    BoilerplateDetector
)
from governance.rules.smart_rules import SmartRules, RuleEnhancer
from governance.validators.domain_validators import DomainValidatorOrchestrator
from governance.validators.relaxed_document_validator import RelaxedDocumentValidator

# Try to import optional components
try:
    from governance.rules.test_exemptions import TestExemptionRules, SmartExemptionEngine
    HAS_EXEMPTIONS = True
except ImportError:
    HAS_EXEMPTIONS = False


class GovernanceLevel(Enum):
    """Governance enforcement levels"""
    MINIMAL = "minimal"      # Basic checks only
    ADVISORY = "advisory"    # Warnings but don't block
    MODERATE = "moderate"    # Block on critical issues
    STRICT = "strict"        # Full enforcement
    

class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"              # Safe to proceed
    MEDIUM = "medium"        # Review recommended
    HIGH = "high"            # Approval required
    CRITICAL = "critical"    # Block commit


class FullGovernanceOrchestrator:
    """
    Master orchestrator for all governance components
    Coordinates validation, tracking, and reporting
    """
    
    def __init__(self, repo_root: Path = None, phase: int = 2):
        """Initialize all governance components"""
        self.repo_root = repo_root or Path.cwd()
        self.phase = phase  # Project phase for progressive enforcement
        self.correlation_tracker = get_correlation_tracker()
        self.correlation = None
        
        # Load configuration
        self.config_path = self.repo_root / "governance-config"
        self.config = self._load_configurations()
        
        # Determine governance level based on phase
        self.governance_level = self._determine_governance_level()
        
        # Initialize all components
        self._initialize_components()
        
        # Track validation results
        self.results = {
            "passed": True,
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "metrics": {},
            "risk_score": 0.0,
            "risk_level": RiskLevel.LOW
        }
    
    def _load_configurations(self) -> Dict:
        """Load all governance configurations"""
        config = {
            "exemptions": {},
            "rules": {},
            "living_docs": {},
            "hallucination": {}
        }
        
        # Load exemptions
        exemptions_file = self.config_path / "exemptions.yml"
        if exemptions_file.exists():
            with open(exemptions_file, 'r') as f:
                config["exemptions"] = yaml.safe_load(f)
        
        # Load governance rules
        rules_file = self.config_path / "governance-rules.yml"
        if rules_file.exists():
            with open(rules_file, 'r') as f:
                config["rules"] = yaml.safe_load(f)
        
        # Load living docs config
        living_docs_file = self.config_path / "living-docs.yml"
        if living_docs_file.exists():
            with open(living_docs_file, 'r') as f:
                config["living_docs"] = yaml.safe_load(f)
        
        # Load hallucination patterns
        hallucination_file = self.config_path / "hallucination-patterns.yml"
        if hallucination_file.exists():
            with open(hallucination_file, 'r') as f:
                config["hallucination"] = yaml.safe_load(f)
        
        return config
    
    def _determine_governance_level(self) -> GovernanceLevel:
        """Determine governance level based on phase and environment"""
        # Check for environment overrides
        if os.environ.get("GOVERNANCE_BYPASS") == "true":
            return GovernanceLevel.MINIMAL
        
        if os.environ.get("GOVERNANCE_STRICT") == "true":
            return GovernanceLevel.STRICT
        
        # Phase-based governance
        if self.phase <= 2:
            return GovernanceLevel.ADVISORY
        elif self.phase == 3:
            return GovernanceLevel.MODERATE
        else:
            return GovernanceLevel.STRICT
    
    def _initialize_components(self):
        """Initialize all governance components"""
        # Core components
        self.governance_engine = GovernanceEngine()
        self.enhanced_engine = EnhancedGovernanceEngine(base_path=self.repo_root)
        self.smart_rules = SmartRules()
        self.rule_enhancer = RuleEnhancer()
        
        # Validators
        self.domain_validator = DomainValidatorOrchestrator()
        self.doc_validator = RelaxedDocumentValidator(self.repo_root, self.phase)
        
        # Detectors
        self.magic_detector = MagicVariableDetector()
        self.boilerplate_detector = BoilerplateDetector()
        self.test_tracker = TestExecutionTracker(
            str(self.repo_root / ".governance" / "test-execution.db")
        )
        
        # Optional components
        if HAS_EXEMPTIONS:
            self.exemption_engine = SmartExemptionEngine()
        else:
            self.exemption_engine = None
    
    def get_git_info(self) -> Dict[str, Any]:
        """Get information about the git commit"""
        info = {}
        
        # Get user
        result = subprocess.run(
            ['git', 'config', 'user.name'],
            capture_output=True, text=True
        )
        info['user'] = result.stdout.strip() if result.returncode == 0 else 'unknown'
        
        # Get branch
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True, text=True
        )
        info['branch'] = result.stdout.strip() if result.returncode == 0 else 'unknown'
        
        # Get changed files
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True, text=True
        )
        info['files'] = result.stdout.strip().split('\n') if result.stdout else []
        
        # Get commit message (if available)
        commit_msg_file = self.repo_root / ".git" / "COMMIT_EDITMSG"
        if commit_msg_file.exists():
            with open(commit_msg_file, 'r') as f:
                info['message'] = f.read().strip()
        else:
            info['message'] = ""
        
        return info
    
    def validate_files(self, files: List[str]) -> Dict[str, Any]:
        """Run all validators on changed files"""
        validation_results = {
            "domain_validation": {},
            "magic_variables": [],
            "boilerplate": [],
            "documentation": {},
            "test_staleness": [],
            "hallucination": []
        }
        
        for file_path in files:
            if not file_path or not Path(file_path).exists():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                self.results["warnings"].append(f"Could not read {file_path}: {e}")
                continue
            
            # Skip binary files
            if '\0' in content:
                continue
            
            # Domain-specific validation
            domain_results = self.domain_validator.validate(content, file_path)
            if domain_results:
                validation_results["domain_validation"][file_path] = domain_results
            
            # Magic variable detection
            magic_vars = self.magic_detector.detect(content, file_path)
            if magic_vars:
                validation_results["magic_variables"].extend(magic_vars)
            
            # Boilerplate detection
            boilerplate = self.boilerplate_detector.detect_boilerplate(content, file_path)
            if boilerplate:
                validation_results["boilerplate"].extend(boilerplate)
            
            # Track this file for boilerplate comparison
            self.boilerplate_detector.add_pattern(content, file_path)
        
        # Document validation (advisory mode)
        doc_passed, doc_errors, doc_warnings, doc_suggestions = self.doc_validator.validate_all_documents()
        validation_results["documentation"] = {
            "passed": doc_passed,
            "errors": doc_errors,
            "warnings": doc_warnings,
            "suggestions": doc_suggestions
        }
        
        # Test staleness check
        stale_tests = self.test_tracker.get_stale_tests(max_age_days=7)
        validation_results["test_staleness"] = stale_tests
        
        return validation_results
    
    def calculate_risk_score(self, validation_results: Dict) -> Tuple[float, RiskLevel]:
        """Calculate overall risk score and level"""
        score = 0.0
        
        # Domain validation risks
        for file_path, domain_results in validation_results.get("domain_validation", {}).items():
            for domain, result in domain_results.items():
                if not result.passed:
                    score += result.risk_score
        
        # Magic variables (medium risk)
        magic_count = len(validation_results.get("magic_variables", []))
        score += magic_count * 0.5
        
        # Boilerplate (low risk)
        boilerplate_count = len(validation_results.get("boilerplate", []))
        score += boilerplate_count * 0.3
        
        # Documentation issues (low risk in advisory mode)
        doc_errors = len(validation_results["documentation"].get("errors", []))
        score += doc_errors * 0.2
        
        # Stale tests (medium risk)
        stale_count = len(validation_results.get("test_staleness", []))
        score += stale_count * 1.0
        
        # Determine risk level
        if score >= 10:
            level = RiskLevel.CRITICAL
        elif score >= 7:
            level = RiskLevel.HIGH
        elif score >= 4:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        
        return min(score, 10.0), level
    
    def format_report(self, git_info: Dict, validation_results: Dict) -> str:
        """Format comprehensive governance report"""
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("FULL GOVERNANCE VALIDATION REPORT")
        lines.append(f"Phase: {self.phase} | Level: {self.governance_level.value.upper()}")
        lines.append("=" * 70)
        lines.append("")
        
        # Git info
        lines.append(f"User: {git_info['user']}")
        lines.append(f"Branch: {git_info['branch']}")
        lines.append(f"Files: {len(git_info['files'])}")
        if self.correlation:
            lines.append(f"Correlation ID: {self.correlation.correlation_id}")
        lines.append("")
        
        # Risk assessment
        lines.append("RISK ASSESSMENT")
        lines.append("-" * 40)
        lines.append(f"Risk Score: {self.results['risk_score']:.1f}/10.0")
        lines.append(f"Risk Level: {self.results['risk_level'].value.upper()}")
        lines.append("")
        
        # Domain validation
        if validation_results["domain_validation"]:
            lines.append("DOMAIN-SPECIFIC VALIDATION")
            lines.append("-" * 40)
            
            for file_path, domain_results in validation_results["domain_validation"].items():
                lines.append(f"\n{file_path}:")
                for domain, result in domain_results.items():
                    status = "✅" if result.passed else "❌"
                    lines.append(f"  {status} {domain.upper()} (risk: {result.risk_score:.1f})")
                    
                    if result.errors:
                        for error in result.errors[:2]:
                            lines.append(f"    ERROR: {error}")
                    
                    if result.warnings:
                        for warning in result.warnings[:2]:
                            lines.append(f"    WARN: {warning}")
            lines.append("")
        
        # Magic variables
        if validation_results["magic_variables"]:
            lines.append("MAGIC VARIABLES DETECTED")
            lines.append("-" * 40)
            for issue in validation_results["magic_variables"][:5]:
                lines.append(f"  {issue['file']}: {issue['value']}")
                if issue.get("suggestion"):
                    lines.append(f"    → {issue['suggestion']}")
            if len(validation_results["magic_variables"]) > 5:
                lines.append(f"  ... and {len(validation_results['magic_variables']) - 5} more")
            lines.append("")
        
        # Boilerplate
        if validation_results["boilerplate"]:
            lines.append("BOILERPLATE CODE DETECTED")
            lines.append("-" * 40)
            for pattern in validation_results["boilerplate"][:3]:
                lines.append(f"  {pattern['file']} similar to {pattern['similar_to']}")
                lines.append(f"    Similarity: {pattern['similarity']:.0%}")
            lines.append("")
        
        # Documentation
        doc = validation_results["documentation"]
        if doc["errors"] or doc["warnings"]:
            lines.append("DOCUMENTATION VALIDATION (Advisory)")
            lines.append("-" * 40)
            
            if doc["errors"]:
                for error in doc["errors"][:2]:
                    lines.append(f"  ERROR: {error}")
            
            if doc["warnings"]:
                for warning in doc["warnings"][:2]:
                    lines.append(f"  WARN: {warning}")
            
            if doc["suggestions"]:
                lines.append(f"  {len(doc['suggestions'])} suggestions available")
            lines.append("")
        
        # Test staleness
        if validation_results["test_staleness"]:
            lines.append("STALE TESTS DETECTED")
            lines.append("-" * 40)
            for test in validation_results["test_staleness"][:3]:
                lines.append(f"  {test['test_file']}: {test['days_old']} days old")
            lines.append("")
        
        # Decision
        lines.append("=" * 70)
        lines.append("DECISION")
        lines.append("-" * 40)
        
        if self.governance_level == GovernanceLevel.MINIMAL:
            lines.append("✅ MINIMAL CHECKS PASSED - Proceeding")
        elif self.governance_level == GovernanceLevel.ADVISORY:
            lines.append("✅ ADVISORY MODE - Proceeding with recommendations")
            if self.results['risk_level'] in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                lines.append("⚠️  HIGH RISK DETECTED - Review recommended")
        elif self.governance_level == GovernanceLevel.MODERATE:
            if self.results['risk_level'] == RiskLevel.CRITICAL:
                lines.append("❌ CRITICAL RISK - Commit blocked")
            elif self.results['risk_level'] == RiskLevel.HIGH:
                lines.append("⚠️  HIGH RISK - Approval required")
            else:
                lines.append("✅ MODERATE CHECKS PASSED - Proceeding")
        else:  # STRICT
            if self.results['risk_level'] in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                lines.append("❌ GOVERNANCE FAILED - Commit blocked")
            elif self.results['risk_level'] == RiskLevel.MEDIUM:
                lines.append("⚠️  REVIEW REQUIRED - Get approval")
            else:
                lines.append("✅ STRICT CHECKS PASSED - Proceeding")
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def save_report(self, report: str):
        """Save detailed report to file"""
        report_dir = self.repo_root / ".governance" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"governance_report_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Also save as latest
        latest_file = report_dir / "latest_report.txt"
        with open(latest_file, 'w') as f:
            f.write(report)
    
    def run_validation(self) -> int:
        """Main validation entry point"""
        try:
            # Get git information
            git_info = self.get_git_info()
            
            # Create correlation for tracking
            self.correlation = self.correlation_tracker.create_correlation(
                operation_type="git.pre_commit",
                operation_name="full_governance_validation",
                user=git_info['user'],
                metadata=git_info
            )
            
            # Run all validators
            print("\n🔍 Running full governance validation...")
            validation_results = self.validate_files(git_info['files'])
            
            # Calculate risk
            risk_score, risk_level = self.calculate_risk_score(validation_results)
            self.results['risk_score'] = risk_score
            self.results['risk_level'] = risk_level
            
            # Generate report
            report = self.format_report(git_info, validation_results)
            print(report)
            
            # Save report
            self.save_report(report)
            
            # Update correlation with results
            self.correlation_tracker.update_correlation(
                self.correlation.correlation_id,
                metadata={
                    "risk_score": risk_score,
                    "risk_level": risk_level.value,
                    "governance_level": self.governance_level.value,
                    "validation_results": validation_results
                }
            )
            
            # Determine exit code based on governance level and risk
            if self.governance_level == GovernanceLevel.MINIMAL:
                exit_code = 0
            elif self.governance_level == GovernanceLevel.ADVISORY:
                exit_code = 0  # Advisory never blocks
            elif self.governance_level == GovernanceLevel.MODERATE:
                exit_code = 1 if risk_level == RiskLevel.CRITICAL else 0
            else:  # STRICT
                exit_code = 1 if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] else 0
            
            # Complete correlation
            status = OperationStatus.COMPLETED if exit_code == 0 else OperationStatus.FAILED
            self.correlation_tracker.complete_correlation(
                self.correlation.correlation_id,
                status=status
            )
            
            return exit_code
            
        except Exception as e:
            print(f"\n❌ Governance validation error: {e}")
            print(traceback.format_exc())
            
            if self.correlation:
                self.correlation_tracker.complete_correlation(
                    self.correlation.correlation_id,
                    status=OperationStatus.FAILED,
                    error=str(e)
                )
            
            # In case of error, be lenient
            return 0 if self.governance_level in [GovernanceLevel.MINIMAL, GovernanceLevel.ADVISORY] else 1


def main():
    """Main entry point for pre-commit hook"""
    # Check for bypass
    if os.environ.get("GOVERNANCE_EMERGENCY_BYPASS") == "true":
        print("⚠️  EMERGENCY BYPASS ACTIVE - Skipping governance")
        return 0
    
    # Run full governance
    orchestrator = FullGovernanceOrchestrator()
    return orchestrator.run_validation()


if __name__ == "__main__":
    sys.exit(main())