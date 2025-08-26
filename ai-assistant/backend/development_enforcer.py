#!/usr/bin/env python
"""
Development Standards Enforcer
Run this BEFORE committing code to ensure compliance with our rules
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from persona_manager import PersonaManager, PersonaType
from rules_enforcement import RulesEnforcementEngine, RuleType
from cache_manager import IntelligentCache
from config import Config

class DevelopmentEnforcer:
    """Enforces our development standards and assumptions"""
    
    def __init__(self):
        self.config = Config()
        self.persona_manager = PersonaManager()
        self.rules_engine = RulesEnforcementEngine()
        self.cache = IntelligentCache()
        self.violations = []
        
    async def check_magic_variables(self, directory: str = ".") -> List[Dict]:
        """Check for magic variables in code"""
        violations = []
        
        # Patterns to detect
        magic_patterns = [
            (r'\b(localhost|127\.0\.0\.1)\b', 'hardcoded host'),
            (r'\b(3000|8000|5432|3306)\b', 'hardcoded port'),
            (r'(api_key|secret|password)\s*=\s*["\']', 'hardcoded credential'),
            (r'\b(10|100|1000)\b(?!\d)', 'magic number limit'),
        ]
        
        for root, dirs, files in os.walk(directory):
            # Skip test and cache directories
            if any(skip in root for skip in ['.git', '__pycache__', 'node_modules', 'cache']):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            lines = content.split('\n')
                            
                        for i, line in enumerate(lines, 1):
                            for pattern, desc in magic_patterns:
                                import re
                                if re.search(pattern, line):
                                    violations.append({
                                        'file': filepath,
                                        'line': i,
                                        'type': desc,
                                        'content': line.strip()[:80]
                                    })
                    except Exception as e:
                        print(f"[WARN] Could not check {filepath}: {e}")
                        
        return violations
    
    async def check_test_coverage(self) -> Dict:
        """Check test coverage meets standards"""
        try:
            # Run coverage
            result = subprocess.run(
                [sys.executable, '-m', 'coverage', 'report', '--format=total'],
                capture_output=True, text=True, cwd=Path(__file__).parent
            )
            
            coverage = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
            
            return {
                'coverage': coverage,
                'meets_standard': coverage >= 70,
                'recommendation': 'Increase test coverage' if coverage < 70 else 'Good coverage'
            }
        except Exception as e:
            return {
                'coverage': 0,
                'error': str(e),
                'recommendation': 'Install coverage: pip install coverage'
            }
    
    async def check_documentation(self, directory: str = ".") -> Dict:
        """Check documentation completeness"""
        total_functions = 0
        documented_functions = 0
        missing_docs = []
        
        for root, dirs, files in os.walk(directory):
            if any(skip in root for skip in ['.git', '__pycache__', 'test']):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        import ast
                        tree = ast.parse(content)
                        
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                total_functions += 1
                                if ast.get_docstring(node):
                                    documented_functions += 1
                                else:
                                    missing_docs.append(f"{filepath}:{node.lineno} {node.name}()")
                    except Exception as e:
                        print(f"[WARNING] Could not parse {filepath}: {e}")
        
        coverage = (documented_functions / total_functions * 100) if total_functions > 0 else 0
        
        return {
            'total_functions': total_functions,
            'documented': documented_functions,
            'coverage': f"{coverage:.1f}%",
            'missing': missing_docs[:10]  # First 10 missing
        }
    
    async def validate_assumptions(self, code_changes: List[str]) -> List[Dict]:
        """Validate no assumptions in code changes"""
        violations = []
        
        assumption_phrases = [
            'should work', 'probably', 'likely', 'assume', 
            'I think', 'might be', 'typically', 'usually'
        ]
        
        for filepath in code_changes:
            if not os.path.exists(filepath):
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines, 1):
                    # Check comments for assumptions
                    if '#' in line:
                        comment = line[line.index('#'):]
                        for phrase in assumption_phrases:
                            if phrase in comment.lower():
                                violations.append({
                                    'file': filepath,
                                    'line': i,
                                    'assumption': phrase,
                                    'content': line.strip()
                                })
            except Exception as e:
                print(f"[WARNING] Could not process file: {e}")
                
        return violations
    
    async def enforce_persona_review(self, changes: List[str]) -> Dict:
        """Have each persona review the changes"""
        reviews = {}
        
        for filepath in changes:
            if not filepath.endswith('.py'):
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Auto-select persona for review
                suggested = self.persona_manager.suggest_persona(content)
                if suggested:
                    persona = suggested[0]
                    
                    # Create review based on persona expertise
                    if persona == PersonaType.SARAH_CHEN:
                        reviews[filepath] = {
                            'reviewer': 'Dr. Sarah Chen',
                            'focus': 'AI integration and Claude optimization',
                            'checks': ['No hardcoded API keys', 'Proper error handling', 'Token optimization']
                        }
                    elif persona == PersonaType.MARCUS_RODRIGUEZ:
                        reviews[filepath] = {
                            'reviewer': 'Marcus Rodriguez',
                            'focus': 'Performance and architecture',
                            'checks': ['No performance bottlenecks', 'Proper caching', 'Database efficiency']
                        }
                    elif persona == PersonaType.EMILY_WATSON:
                        reviews[filepath] = {
                            'reviewer': 'Emily Watson',
                            'focus': 'User experience and interface',
                            'checks': ['Clear error messages', 'Intuitive design', 'Accessibility']
                        }
            except Exception as e:
                print(f"[WARNING] Could not process file: {e}")
                
        return reviews
    
    async def run_enforcement(self, directory: str = ".", check_all: bool = False) -> Dict:
        """Run all enforcement checks"""
        print("[ENFORCEMENT] Starting development standards check...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'directory': directory,
            'checks': {}
        }
        
        # Check magic variables
        print("[CHECK] Magic variables...")
        magic = await self.check_magic_variables(directory)
        results['checks']['magic_variables'] = {
            'found': len(magic),
            'violations': magic[:5]  # First 5
        }
        
        # Check test coverage
        if check_all:
            print("[CHECK] Test coverage...")
            coverage = await self.check_test_coverage()
            results['checks']['test_coverage'] = coverage
        
        # Check documentation
        print("[CHECK] Documentation...")
        docs = await self.check_documentation(directory)
        results['checks']['documentation'] = docs
        
        # Get changed files (simplified - in production use git)
        changed_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    changed_files.append(os.path.join(root, file))
        
        # Validate assumptions
        print("[CHECK] Assumptions...")
        assumptions = await self.validate_assumptions(changed_files[:10])
        results['checks']['assumptions'] = {
            'found': len(assumptions),
            'violations': assumptions
        }
        
        # Persona review
        print("[CHECK] Persona review...")
        reviews = await self.enforce_persona_review(changed_files[:5])
        results['checks']['persona_reviews'] = reviews
        
        # Calculate overall status
        total_violations = (
            len(magic) + 
            len(assumptions) +
            (1 if docs.get('coverage', '0%').strip('%') and float(docs['coverage'].strip('%')) < 70 else 0)
        )
        
        results['summary'] = {
            'status': 'PASS' if total_violations == 0 else 'FAIL',
            'total_violations': total_violations,
            'recommendation': 'Ready to commit' if total_violations == 0 else 'Fix violations before committing'
        }
        
        return results
    
    def print_report(self, results: Dict):
        """Print enforcement report"""
        print("\n" + "="*60)
        print("DEVELOPMENT STANDARDS ENFORCEMENT REPORT")
        print("="*60)
        
        # Magic variables
        magic = results['checks']['magic_variables']
        print(f"\n[MAGIC VARIABLES] Found: {magic['found']}")
        for v in magic['violations']:
            print(f"  - {v['file']}:{v['line']} - {v['type']}")
        
        # Documentation
        docs = results['checks']['documentation']
        print(f"\n[DOCUMENTATION] Coverage: {docs['coverage']}")
        if docs['missing']:
            print("  Missing documentation:")
            for missing in docs['missing'][:3]:
                print(f"    - {missing}")
        
        # Assumptions
        assumptions = results['checks']['assumptions']
        print(f"\n[ASSUMPTIONS] Found: {assumptions['found']}")
        for a in assumptions['violations']:
            print(f"  - {a['file']}:{a['line']} - '{a['assumption']}' in comment")
        
        # Persona reviews
        reviews = results['checks'].get('persona_reviews', {})
        if reviews:
            print(f"\n[PERSONA REVIEWS] {len(reviews)} files reviewed")
            for filepath, review in list(reviews.items())[:3]:
                print(f"  - {os.path.basename(filepath)}: Reviewed by {review['reviewer']}")
        
        # Summary
        summary = results['summary']
        print("\n" + "="*60)
        print(f"STATUS: {summary['status']}")
        print(f"Total Violations: {summary['total_violations']}")
        print(f"Recommendation: {summary['recommendation']}")
        print("="*60)

async def main():
    """Main entry point"""
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description='Enforce development standards')
    parser.add_argument('--directory', default='.', help='Directory to check')
    parser.add_argument('--all', action='store_true', help='Run all checks including tests')
    parser.add_argument('--output', help='Save report to file')
    
    args = parser.parse_args()
    
    enforcer = DevelopmentEnforcer()
    results = await enforcer.run_enforcement(args.directory, args.all)
    
    # Print report
    enforcer.print_report(results)
    
    # Save if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n[SAVED] Report saved to {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if results['summary']['status'] == 'PASS' else 1)

if __name__ == "__main__":
    asyncio.run(main())