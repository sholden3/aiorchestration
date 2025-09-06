#!/usr/bin/env python3
"""
Documentation Validation System

Validates documentation health to prevent future documentation drift.
Part of Emergency Documentation Remediation implementation.

Created: 2025-01-06
Author: Emergency Response Team
Phase: Emergency Documentation Remediation
"""

import os
import re
import json
import yaml
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import subprocess


@dataclass
class ValidationResult:
    """Result of a validation check."""
    check_name: str
    passed: bool
    score: float
    issues: List[str]
    warnings: List[str]


class DocumentationValidator:
    """
    Comprehensive documentation validation system.
    
    Validates:
    - Path references are current
    - No broken internal links
    - Component documentation coverage
    - Configuration documentation completeness
    - Architecture consistency with code
    """
    
    def __init__(self, project_root: Path = None):
        """Initialize the validator."""
        self.project_root = project_root or Path.cwd()
        self.docs_dir = self.project_root / "docs"
        self.results: List[ValidationResult] = []
        
        # Patterns to check
        self.outdated_patterns = [
            r'ai-assistant',  # Old directory structure
            # Note: governance/hooks path is valid in some contexts (e.g., old references)
            # Only flag if it's a direct file reference, not in libs/governance/hooks
            r'(?<!libs/)governance/hooks/pre-commit\.py',  # Old hook location without libs prefix
        ]
        
        # Required documentation files
        self.required_docs = [
            "README.md",
            "STATUS.md",
            "TRACKER.md",
            "DECISIONS.md",
            "CLAUDE.md",
        ]
        
        # Component paths that need documentation
        self.component_paths = {
            "apps/api/mcp": "docs/architecture/mcp",
            "libs/governance": "docs/architecture/governance",
            "apps/api": "docs/architecture/backend.md",
            "apps/web": "docs/architecture/frontend.md",
        }
    
    def validate_all(self) -> Dict[str, any]:
        """Run all validation checks."""
        print("=" * 60)
        print("DOCUMENTATION VALIDATION SYSTEM")
        print("=" * 60)
        print()
        
        # Run all checks
        self.check_path_references()
        self.check_internal_links()
        self.check_component_coverage()
        self.check_configuration_docs()
        self.check_required_files()
        self.check_architecture_consistency()
        
        # Calculate overall score
        total_score = sum(r.score for r in self.results)
        max_score = len(self.results) * 100
        overall_score = (total_score / max_score * 100) if max_score > 0 else 0
        
        # Determine status
        all_passed = all(r.passed for r in self.results)
        critical_failures = [r for r in self.results if not r.passed and r.score == 0]
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_score": overall_score,
            "all_passed": all_passed,
            "critical_failures": len(critical_failures),
            "results": self.results,
            "summary": self._generate_summary()
        }
    
    def check_path_references(self) -> ValidationResult:
        """Check for outdated path references in documentation."""
        print("[CHECK] Validating path references...")
        issues = []
        warnings = []
        
        for md_file in self.docs_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in self.outdated_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append(f"Outdated reference '{pattern}' in {md_file.relative_to(self.project_root)}")
            except Exception as e:
                warnings.append(f"Could not check {md_file}: {e}")
        
        passed = len(issues) == 0
        score = 100 if passed else max(0, 100 - len(issues) * 10)
        
        result = ValidationResult(
            check_name="Path References",
            passed=passed,
            score=score,
            issues=issues,
            warnings=warnings
        )
        self.results.append(result)
        
        if passed:
            print("  [PASS] No outdated path references found")
        else:
            print(f"  [FAIL] Found {len(issues)} outdated references")
        
        return result
    
    def check_internal_links(self) -> ValidationResult:
        """Check for broken internal documentation links."""
        print("[CHECK] Validating internal links...")
        issues = []
        warnings = []
        
        # Pattern for markdown links
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        
        for md_file in self.docs_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                matches = link_pattern.findall(content)
                for link_text, link_path in matches:
                    # Skip external links
                    if link_path.startswith(('http://', 'https://', 'mailto:')):
                        continue
                    
                    # Check relative links
                    if not link_path.startswith('#'):
                        target_path = (md_file.parent / link_path).resolve()
                        if not target_path.exists():
                            issues.append(f"Broken link '{link_path}' in {md_file.relative_to(self.project_root)}")
            except Exception as e:
                warnings.append(f"Could not check links in {md_file}: {e}")
        
        passed = len(issues) == 0
        score = 100 if passed else max(0, 100 - len(issues) * 5)
        
        result = ValidationResult(
            check_name="Internal Links",
            passed=passed,
            score=score,
            issues=issues,
            warnings=warnings
        )
        self.results.append(result)
        
        if passed:
            print("  [PASS] All internal links are valid")
        else:
            print(f"  [FAIL] Found {len(issues)} broken links")
        
        return result
    
    def check_component_coverage(self) -> ValidationResult:
        """Check that all components have documentation."""
        print("[CHECK] Validating component documentation coverage...")
        issues = []
        warnings = []
        
        for component_path, doc_path in self.component_paths.items():
            component_full = self.project_root / component_path
            doc_full = self.project_root / doc_path
            
            if component_full.exists():
                if not doc_full.exists():
                    issues.append(f"Component '{component_path}' lacks documentation at '{doc_path}'")
                else:
                    # Check if documentation mentions the component
                    if doc_full.is_file():
                        with open(doc_full, 'r', encoding='utf-8') as f:
                            content = f.read()
                            component_name = Path(component_path).name
                            if component_name not in content:
                                warnings.append(f"Documentation '{doc_path}' may not cover '{component_path}'")
        
        passed = len(issues) == 0
        score = 100 if passed else max(0, 100 - len(issues) * 20)
        
        result = ValidationResult(
            check_name="Component Coverage",
            passed=passed,
            score=score,
            issues=issues,
            warnings=warnings
        )
        self.results.append(result)
        
        if passed:
            print("  [PASS] All components have documentation")
        else:
            print(f"  [FAIL] {len(issues)} components lack documentation")
        
        return result
    
    def check_configuration_docs(self) -> ValidationResult:
        """Check that all configuration files are documented."""
        print("[CHECK] Validating configuration documentation...")
        issues = []
        warnings = []
        
        # Configuration files to check
        config_files = [
            "mcp_config.yaml",
            ".mcp.json",
            "enterprise_managed_settings.json",
            ".ports.json",
        ]
        
        for config_file in config_files:
            # Find config files
            for config_path in self.project_root.rglob(config_file):
                if '.archive' in str(config_path):
                    continue
                    
                # Check if documented
                config_name = config_path.name
                documented = False
                
                for md_file in self.docs_dir.rglob("*.md"):
                    with open(md_file, 'r', encoding='utf-8') as f:
                        if config_name in f.read():
                            documented = True
                            break
                
                if not documented:
                    issues.append(f"Configuration file '{config_path.relative_to(self.project_root)}' is not documented")
        
        passed = len(issues) == 0
        score = 100 if passed else max(0, 100 - len(issues) * 15)
        
        result = ValidationResult(
            check_name="Configuration Documentation",
            passed=passed,
            score=score,
            issues=issues,
            warnings=warnings
        )
        self.results.append(result)
        
        if passed:
            print("  [PASS] All configuration files are documented")
        else:
            print(f"  [FAIL] {len(issues)} configuration files lack documentation")
        
        return result
    
    def check_required_files(self) -> ValidationResult:
        """Check that all required documentation files exist."""
        print("[CHECK] Validating required documentation files...")
        issues = []
        warnings = []
        
        for required_file in self.required_docs:
            file_path = self.project_root / required_file
            if not file_path.exists():
                issues.append(f"Required file '{required_file}' is missing")
            else:
                # Check if file has minimum content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) < 100:
                        warnings.append(f"Required file '{required_file}' seems too short ({len(content)} chars)")
        
        passed = len(issues) == 0
        score = 100 if passed else 0  # Critical check
        
        result = ValidationResult(
            check_name="Required Files",
            passed=passed,
            score=score,
            issues=issues,
            warnings=warnings
        )
        self.results.append(result)
        
        if passed:
            print("  [PASS] All required documentation files exist")
        else:
            print(f"  [FAIL] {len(issues)} required files missing")
        
        return result
    
    def check_architecture_consistency(self) -> ValidationResult:
        """Check that documented architecture matches actual code structure."""
        print("[CHECK] Validating architecture consistency...")
        issues = []
        warnings = []
        
        # Check if documented services exist
        backend_md = self.project_root / "docs/architecture/backend.md"
        if backend_md.exists():
            with open(backend_md, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for MCP components
                if "MCP Governance Server" in content:
                    if not (self.project_root / "apps/api/mcp/governance_server.py").exists():
                        issues.append("Documentation mentions MCP Governance Server but file doesn't exist")
                
                if "Hook Bridge Service" in content:
                    if not (self.project_root / "apps/api/mcp/claude_code_hook_bridge.py").exists():
                        issues.append("Documentation mentions Hook Bridge but file doesn't exist")
        
        passed = len(issues) == 0
        score = 100 if passed else max(0, 100 - len(issues) * 25)
        
        result = ValidationResult(
            check_name="Architecture Consistency",
            passed=passed,
            score=score,
            issues=issues,
            warnings=warnings
        )
        self.results.append(result)
        
        if passed:
            print("  [PASS] Documentation matches code structure")
        else:
            print(f"  [FAIL] {len(issues)} architecture inconsistencies")
        
        return result
    
    def _generate_summary(self) -> Dict[str, any]:
        """Generate a summary of validation results."""
        passed_checks = sum(1 for r in self.results if r.passed)
        total_checks = len(self.results)
        total_issues = sum(len(r.issues) for r in self.results)
        total_warnings = sum(len(r.warnings) for r in self.results)
        
        return {
            "checks_passed": f"{passed_checks}/{total_checks}",
            "total_issues": total_issues,
            "total_warnings": total_warnings,
            "critical_checks_failed": [r.check_name for r in self.results if not r.passed and r.score == 0],
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        for result in self.results:
            if not result.passed:
                if result.check_name == "Path References":
                    recommendations.append("Run path fix script to update outdated references")
                elif result.check_name == "Internal Links":
                    recommendations.append("Review and fix broken internal documentation links")
                elif result.check_name == "Component Coverage":
                    recommendations.append("Create documentation for undocumented components")
                elif result.check_name == "Configuration Documentation":
                    recommendations.append("Document all configuration files in architecture docs")
                elif result.check_name == "Required Files":
                    recommendations.append("Create missing required documentation files immediately")
                elif result.check_name == "Architecture Consistency":
                    recommendations.append("Update documentation to match actual code structure")
        
        return recommendations


def main():
    """Main entry point for documentation validation."""
    validator = DocumentationValidator()
    results = validator.validate_all()
    
    print()
    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Overall Score: {results['overall_score']:.1f}%")
    print(f"Checks Passed: {results['summary']['checks_passed']}")
    print(f"Total Issues: {results['summary']['total_issues']}")
    print(f"Total Warnings: {results['summary']['total_warnings']}")
    print()
    
    if results['all_passed']:
        print("[SUCCESS] All documentation validation checks passed!")
        return 0
    else:
        print("[FAILURE] Documentation validation failed!")
        print()
        print("Critical Issues to Fix:")
        for result in results['results']:
            if not result.passed:
                print(f"\n{result.check_name}:")
                for issue in result.issues[:5]:  # Show first 5 issues
                    print(f"  - {issue}")
                if len(result.issues) > 5:
                    print(f"  ... and {len(result.issues) - 5} more issues")
        
        print()
        print("Recommendations:")
        for rec in results['summary']['recommendations']:
            print(f"  - {rec}")
        
        return 1


if __name__ == "__main__":
    exit(main())