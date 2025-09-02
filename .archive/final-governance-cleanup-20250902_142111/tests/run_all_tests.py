#!/usr/bin/env python3
"""
@fileoverview Test runner for all governance tests
@author Sam Martinez v3.2.0 - 2025-01-28
@architecture Testing - Test orchestration
@responsibility Run all governance system tests
@dependencies pytest, unittest, sys, pathlib
@integration_points All test modules in governance/tests
@testing_strategy Comprehensive test execution with reporting
@governance Test orchestration following governance requirements

Business Logic Summary:
- Discover and run all tests
- Generate coverage reports
- Provide clear pass/fail status

Architecture Integration:
- Part of CI/CD pipeline
- Validates entire governance system
- Provides test metrics
"""

import sys
import subprocess
from pathlib import Path
import json
import time
from datetime import datetime


class GovernanceTestRunner:
    """
    @class GovernanceTestRunner
    @description Orchestrates all governance system tests
    @architecture_role Test execution coordinator
    @business_logic Run tests and report results
    """
    
    def __init__(self):
        """Initialize test runner"""
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def run_all_tests(self):
        """
        Run all governance tests
        
        @method run_all_tests
        @description Execute all test suites
        @returns Overall success status
        """
        print("=" * 70)
        print("GOVERNANCE SYSTEM TEST SUITE")
        print("=" * 70)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Test Directory: {self.test_dir}")
        print()
        
        self.start_time = time.time()
        
        # Test modules to run
        test_modules = [
            'test_correlation_tracker.py',
            'test_integrated_hook.py',
            'test_smart_rules.py'
        ]
        
        overall_success = True
        
        for module in test_modules:
            module_path = self.test_dir / module
            if module_path.exists():
                success = self.run_test_module(module)
                overall_success = overall_success and success
            else:
                print(f"[WARNING] Test module not found: {module}")
        
        self.end_time = time.time()
        
        # Print summary
        self.print_summary(overall_success)
        
        return overall_success
    
    def run_test_module(self, module_name):
        """
        Run a single test module
        
        @param module_name Name of test module
        @returns Success status
        """
        print(f"\n{'=' * 50}")
        print(f"Running: {module_name}")
        print('-' * 50)
        
        try:
            # Run pytest with coverage
            result = subprocess.run(
                [
                    sys.executable, '-m', 'pytest',
                    str(self.test_dir / module_name),
                    '-v',
                    '--tb=short',
                    '--color=no'
                ],
                capture_output=True,
                text=True,
                cwd=str(self.project_root)
            )
            
            # Parse results
            success = result.returncode == 0
            
            # Store results
            self.results[module_name] = {
                'success': success,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            # Print output
            if success:
                print(f"[OK] {module_name} - All tests passed")
                # Show test counts
                for line in result.stdout.split('\n'):
                    if 'passed' in line.lower():
                        print(f"     {line.strip()}")
            else:
                print(f"[FAILED] {module_name} - Tests failed")
                # Show failures
                print("\nFailure Output:")
                print(result.stdout)
                if result.stderr:
                    print("\nError Output:")
                    print(result.stderr)
            
            return success
            
        except Exception as e:
            print(f"[ERROR] Failed to run {module_name}: {e}")
            self.results[module_name] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    def print_summary(self, overall_success):
        """
        Print test summary
        
        @param overall_success Overall test status
        """
        duration = self.end_time - self.start_time
        
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        # Module results
        print("\nModule Results:")
        for module, result in self.results.items():
            status = "[OK]" if result['success'] else "[FAILED]"
            print(f"  {status} {module}")
        
        # Statistics
        total_modules = len(self.results)
        passed_modules = sum(1 for r in self.results.values() if r['success'])
        failed_modules = total_modules - passed_modules
        
        print(f"\nStatistics:")
        print(f"  Total Modules: {total_modules}")
        print(f"  Passed: {passed_modules}")
        print(f"  Failed: {failed_modules}")
        print(f"  Duration: {duration:.2f} seconds")
        
        # Overall status
        print("\n" + "=" * 70)
        if overall_success:
            print("[OK] ALL GOVERNANCE TESTS PASSED")
        else:
            print("[FAILED] SOME GOVERNANCE TESTS FAILED")
        print("=" * 70)
    
    def run_with_coverage(self):
        """
        Run tests with coverage report
        
        @method run_with_coverage
        @description Execute tests and generate coverage
        @returns Success status
        """
        print("Running tests with coverage...")
        
        try:
            result = subprocess.run(
                [
                    sys.executable, '-m', 'pytest',
                    str(self.test_dir),
                    '--cov=governance',
                    '--cov-report=term-missing',
                    '--cov-report=html:governance/tests/coverage',
                    '-v'
                ],
                capture_output=True,
                text=True,
                cwd=str(self.project_root)
            )
            
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
            if result.returncode == 0:
                print("\n[OK] Coverage report generated in governance/tests/coverage/")
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"[ERROR] Failed to run coverage: {e}")
            return False


def main():
    """Main entry point"""
    runner = GovernanceTestRunner()
    
    # Check for coverage flag
    if '--coverage' in sys.argv:
        success = runner.run_with_coverage()
    else:
        success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()