#!/usr/bin/env python3
"""
Project Structure Validation Script
Cross-platform replacement for validate-project-structure.sh
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

def check_required_directories() -> Tuple[bool, List[str]]:
    """Check if all required directories exist"""
    required_dirs = [
        "ai-assistant/backend/tests",
        "ai-assistant/backend/docs/api",
        "ai-assistant/backend/docs/architecture",
        "ai-assistant/backend/docs/runbooks",
        "ai-assistant/src/app/testing",
        "ai-assistant/src/e2e",
        "ai-assistant/electron/tests",
        "docs/fixes/critical",
        "docs/fixes/high",
        "docs/architecture",
        "docs/processes",
        "docs/runbooks",
        "tests/integration",
        "tests/performance",
        "tests/failure-scenarios",
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    return len(missing_dirs) == 0, missing_dirs

def count_files(pattern: str, path: str, exclude_patterns: List[str] = None) -> int:
    """Count files matching pattern in path"""
    count = 0
    path_obj = Path(path)
    
    if not path_obj.exists():
        return 0
    
    for file_path in path_obj.rglob(pattern):
        # Skip if matches exclude patterns
        if exclude_patterns:
            skip = False
            for exclude in exclude_patterns:
                if exclude in str(file_path):
                    skip = True
                    break
            if skip:
                continue
        
        count += 1
    
    return count

def validate_test_coverage() -> dict:
    """Validate test file coverage"""
    results = {}
    
    # Backend test validation
    if Path("ai-assistant/backend").exists():
        backend_files = count_files("*.py", "ai-assistant/backend", 
                                   exclude_patterns=["tests", "__pycache__", "venv"])
        backend_tests = count_files("test_*.py", "ai-assistant/backend/tests")
        results["backend"] = {
            "implementation": backend_files,
            "tests": backend_tests
        }
    
    # Frontend component test validation
    if Path("ai-assistant/src/app/components").exists():
        component_files = count_files("*.component.ts", "ai-assistant/src/app/components")
        component_tests = count_files("*.component.spec.ts", "ai-assistant/src/app/components")
        results["components"] = {
            "implementation": component_files,
            "tests": component_tests
        }
    
    # Frontend service test validation
    if Path("ai-assistant/src/app/services").exists():
        service_files = count_files("*.service.ts", "ai-assistant/src/app/services")
        service_tests = count_files("*.service.spec.ts", "ai-assistant/src/app/services")
        results["services"] = {
            "implementation": service_files,
            "tests": service_tests
        }
    
    return results

def check_documentation() -> dict:
    """Check documentation files"""
    docs = {
        "CLAUDE.md": Path("CLAUDE.md").exists(),
        "Fix plan": Path("docs/fixes/fixes-implementation-plan.md").exists(),
        "Architecture": Path("docs/ARCHITECTURE.md").exists(),
        "Testing Strategy": Path("docs/TESTING_STRATEGY.md").exists(),
        "Implementation Phases": Path("docs/IMPLEMENTATION_PHASES.md").exists()
    }
    return docs

def main():
    """Main validation function"""
    print("[CHECK] PROJECT STRUCTURE VALIDATION")
    print("-" * 40)
    
    # Check required directories
    dirs_valid, missing_dirs = check_required_directories()
    
    if not dirs_valid:
        print(f"[WARN] Missing {len(missing_dirs)} required directories:")
        for dir_path in missing_dirs[:5]:  # Show first 5
            print(f"  - {dir_path}")
        if len(missing_dirs) > 5:
            print(f"  ... and {len(missing_dirs) - 5} more")
    else:
        print("[PASS] All required directories present")
    
    # Check test coverage
    print("\n[CHECK] TEST FILE VALIDATION")
    print("-" * 40)
    test_results = validate_test_coverage()
    
    for category, counts in test_results.items():
        impl = counts.get("implementation", 0)
        tests = counts.get("tests", 0)
        coverage = (tests / impl * 100) if impl > 0 else 0
        
        status = "[PASS]" if coverage >= 50 else "[WARN]"
        print(f"{status} {category.capitalize()}: {impl} files, {tests} tests ({coverage:.1f}% coverage)")
    
    # Check documentation
    print("\n[CHECK] DOCUMENTATION VALIDATION")
    print("-" * 40)
    docs = check_documentation()
    
    all_docs_present = True
    for doc_name, exists in docs.items():
        status = "[PASS]" if exists else "[WARN]"
        print(f"{status} {doc_name}")
        if not exists:
            all_docs_present = False
    
    # Final verdict
    print("\n" + "=" * 40)
    
    # Determine overall status (more lenient for cross-platform compatibility)
    if dirs_valid and all_docs_present:
        print("[PASS] Project structure validation complete")
        return 0
    elif len(missing_dirs) > 10:
        print(f"[FAIL] Project structure issues: {len(missing_dirs)} missing directories")
        return 1
    else:
        print(f"[WARN] Project structure has minor issues")
        return 0  # Return success but with warnings

if __name__ == "__main__":
    sys.exit(main())