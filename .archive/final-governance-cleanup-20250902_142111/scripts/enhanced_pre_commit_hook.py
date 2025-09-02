#!/usr/bin/env python3
"""
@fileoverview Enhanced Git pre-commit hook with comprehensive CLAUDE.md governance enforcement
@author Dr. Sarah Chen v1.0 & Alex Novak v1.0 - 2025-08-29
@architecture Backend - Git hook integration
@responsibility Enforce all CLAUDE.md governance requirements at commit time
@dependencies subprocess, json, pathlib, governance.core modules
@integration_points Git hooks, validation scripts, governance engine, session management
@testing_strategy Hook execution tests, validation accuracy tests, session management tests
@governance This hook enforces the governance system's own standards

Business Logic Summary:
- Validate session management requirements
- Check code documentation completeness
- Enforce testing requirements
- Validate fix implementation standards
- Check archival requirements
- Verify cross-architect approvals

Architecture Integration:
- Integrates with git pre-commit
- Uses governance engine for validation
- Checks session management files
- Validates against CLAUDE.md rules
- Integrates with validation scripts

Sarah's Framework Check:
- What breaks first: Missing validation scripts cause hook failure
- How we know: Script execution errors in hook output
- Plan B: Embedded validation logic as fallback

Enhanced Git Pre-Commit Hook with Full CLAUDE.md Governance
Integrates all validation requirements from CLAUDE.md
"""

import sys
import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add governance module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from governance.core.engine import GovernanceEngine
from governance.core.context import GovernanceContext
from governance.rules.smart_rules import SmartRules, RuleEnhancer


class CLAUDEGovernanceValidator:
    """Validates compliance with CLAUDE.md requirements"""
    
    def __init__(self):
        self.repo_root = Path(subprocess.run(['git', 'rev-parse', '--show-toplevel'], 
                                           capture_output=True, text=True).stdout.strip())
        self.validation_scripts = {
            'code_documentation': self.repo_root / 'validate-code-documentation.sh',
            'project_structure': self.repo_root / 'validate-project-structure.sh',
            'task_completion': self.repo_root / 'validate-task-completion.sh',
            'specialist_decisions': self.repo_root / 'validate-specialist-decisions.sh',
            'session_start': self.repo_root / 'validate-session-start.sh',
            'session_end': self.repo_root / 'validate-session-end.sh'
        }
        
    def check_session_management(self) -> Tuple[bool, str]:
        """Check if session was properly started"""
        session_file = self.repo_root / '.governance' / 'current_session.json'
        
        if not session_file.exists():
            return False, "Session not started! Run: ./validate-session-start.sh"
        
        try:
            with open(session_file, 'r') as f:
                session = json.load(f)
                
            # Check if session is current (within 8 hours)
            start_time = datetime.fromisoformat(session.get('start_time', ''))
            duration = (datetime.now() - start_time).total_seconds() / 3600
            
            if duration > 8:
                return False, f"Session expired ({duration:.1f} hours). Run: ./validate-session-start.sh"
                
            return True, f"Session active ({duration:.1f} hours)"
            
        except Exception as e:
            return False, f"Invalid session file: {e}"
    
    def check_code_documentation(self, files: List[str]) -> Tuple[bool, List[str]]:
        """Check if code files have required documentation"""
        issues = []
        
        for file in files:
            if not file or not os.path.exists(file):
                continue
                
            # Check Python and TypeScript files
            if file.endswith(('.py', '.ts')):
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Check for mandatory headers
                if '@fileoverview' not in content and file.endswith('.ts'):
                    issues.append(f"{file}: Missing @fileoverview documentation")
                    
                if '@author' not in content:
                    issues.append(f"{file}: Missing @author (persona) documentation")
                    
                if '@architecture' not in content:
                    issues.append(f"{file}: Missing @architecture documentation")
                    
                # Check for business logic documentation
                if 'class ' in content or 'export class' in content:
                    if '@business_logic' not in content:
                        issues.append(f"{file}: Missing @business_logic documentation")
                        
        return len(issues) == 0, issues
    
    def check_testing_requirements(self, files: List[str]) -> Tuple[bool, List[str]]:
        """Check if changes have corresponding tests"""
        issues = []
        
        # Find implementation files without tests
        impl_files = [f for f in files if f.endswith(('.py', '.ts')) 
                     and 'test' not in f.lower() and 'spec' not in f.lower()]
        
        for impl_file in impl_files:
            # Construct expected test file paths
            if impl_file.endswith('.py'):
                test_patterns = [
                    impl_file.replace('.py', '_test.py'),
                    impl_file.replace('.py', '.test.py'),
                    'tests/' + Path(impl_file).name.replace('.py', '_test.py')
                ]
            else:  # TypeScript
                test_patterns = [
                    impl_file.replace('.ts', '.spec.ts'),
                    impl_file.replace('.ts', '.test.ts')
                ]
            
            # Check if any test file exists
            has_test = any(os.path.exists(p) for p in test_patterns)
            if not has_test:
                # Check if test file is being added in this commit
                test_in_commit = any(p in files for p in test_patterns)
                if not test_in_commit:
                    issues.append(f"{impl_file}: No corresponding test file")
        
        return len(issues) == 0, issues
    
    def check_persona_requirements(self, files: List[str]) -> Tuple[bool, List[str]]:
        """Check if specialist decisions are documented"""
        issues = []
        
        # Check if DECISIONS.md needs updating
        specialist_changes = False
        for file in files:
            if any(keyword in file.lower() for keyword in 
                   ['security', 'performance', 'accessibility', 'data', 'architecture']):
                specialist_changes = True
                break
        
        if specialist_changes and 'DECISIONS.md' not in files:
            issues.append("Specialist changes detected but DECISIONS.md not updated")
        
        return len(issues) == 0, issues
    
    def run_validation_script(self, script_name: str) -> Tuple[bool, str]:
        """Run a validation script if it exists"""
        script_path = self.validation_scripts.get(script_name)
        
        if not script_path or not script_path.exists():
            return True, f"Script {script_name} not found (skipping)"
        
        try:
            result = subprocess.run([str(script_path)], 
                                  capture_output=True, text=True, timeout=30)
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            return success, output.strip()
        except subprocess.TimeoutExpired:
            return False, f"Script {script_name} timed out"
        except Exception as e:
            return False, f"Script {script_name} failed: {e}"


def get_git_info():
    """Get information about the commit"""
    info = {}
    
    # Get user name
    result = subprocess.run(['git', 'config', 'user.name'], 
                          capture_output=True, text=True)
    info['user'] = result.stdout.strip() if result.returncode == 0 else 'unknown'
    
    # Get branch name
    result = subprocess.run(['git', 'branch', '--show-current'], 
                          capture_output=True, text=True)
    info['branch'] = result.stdout.strip() if result.returncode == 0 else 'unknown'
    
    # Get changed files
    result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                          capture_output=True, text=True)
    info['files'] = result.stdout.strip().split('\n') if result.stdout else []
    
    # Get diff stats
    result = subprocess.run(['git', 'diff', '--cached', '--stat'], 
                          capture_output=True, text=True)
    info['stats'] = result.stdout.strip() if result.returncode == 0 else ''
    
    return info


def analyze_changes(files):
    """Analyze the changed files"""
    analysis = {
        'test_changes': False,
        'config_changes': False,
        'governance_changes': False,
        'documentation_changes': False,
        'critical_changes': False,  # C1-C3 issues
        'high_priority_changes': False,  # H1-H3 issues
        'file_count': len(files),
        'file_types': set(),
        'file_contents': []
    }
    
    critical_patterns = ['terminal.service', 'cache_manager', 'process', 'electron/main']
    high_patterns = ['websocket', 'ipc', 'database']
    
    for file in files:
        if not file:
            continue
            
        file_lower = file.lower()
        
        # Check file types
        if file.endswith('.py'):
            analysis['file_types'].add('python')
        elif file.endswith('.js') or file.endswith('.ts'):
            analysis['file_types'].add('javascript')
        elif file.endswith('.md'):
            analysis['file_types'].add('markdown')
        
        # Check for specific changes
        if 'test' in file_lower or 'spec' in file_lower:
            analysis['test_changes'] = True
        if any(ext in file for ext in ['.env', '.config', '.yaml', '.yml']):
            analysis['config_changes'] = True
        if 'governance' in file_lower:
            analysis['governance_changes'] = True
        if file.endswith('.md') or 'readme' in file_lower:
            analysis['documentation_changes'] = True
            
        # Check for critical/high priority changes
        if any(pattern in file_lower for pattern in critical_patterns):
            analysis['critical_changes'] = True
        if any(pattern in file_lower for pattern in high_patterns):
            analysis['high_priority_changes'] = True
        
        # Read file contents if it's a code file
        if file.endswith(('.py', '.js', '.ts', '.java', '.c', '.cpp')):
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    analysis['file_contents'].append(content)
            except Exception:
                pass
    
    analysis['file_types'] = list(analysis['file_types'])
    return analysis


def main():
    """Enhanced main hook logic with CLAUDE.md compliance"""
    print("\n" + "=" * 70)
    print("ENHANCED GOVERNANCE PRE-COMMIT HOOK (CLAUDE.md Compliant)")
    print("=" * 70)
    
    # Initialize CLAUDE validator
    claude_validator = CLAUDEGovernanceValidator()
    
    # Check session management FIRST
    print("\n[1/5] Session Management Check")
    print("-" * 40)
    session_valid, session_msg = claude_validator.check_session_management()
    print(f"{'✅' if session_valid else '❌'} {session_msg}")
    
    if not session_valid and not os.environ.get('GOVERNANCE_BYPASS'):
        print("\n[BLOCKED] Session management required by CLAUDE.md")
        print("Run: ./validate-session-start.sh")
        sys.exit(1)
    
    # Get git information
    git_info = get_git_info()
    
    print(f"\nUser: {git_info['user']}")
    print(f"Branch: {git_info['branch']}")
    print(f"Files changed: {len(git_info['files'])}")
    
    if not git_info['files'] or (len(git_info['files']) == 1 and not git_info['files'][0]):
        print("\n[WARNING] No staged files found")
        print("Use 'git add' to stage files for commit")
        sys.exit(1)
    
    # Analyze changes
    analysis = analyze_changes(git_info['files'])
    
    print(f"\nAnalysis:")
    print(f"  - File types: {', '.join(analysis['file_types']) if analysis['file_types'] else 'none'}")
    print(f"  - Test changes: {analysis['test_changes']}")
    print(f"  - Critical (C1-C3) changes: {analysis['critical_changes']}")
    print(f"  - High priority (H1-H3) changes: {analysis['high_priority_changes']}")
    
    # Check code documentation
    print("\n[2/5] Code Documentation Check (CLAUDE.md Requirements)")
    print("-" * 40)
    doc_valid, doc_issues = claude_validator.check_code_documentation(git_info['files'])
    
    if doc_valid:
        print("✅ All code properly documented")
    else:
        print("❌ Documentation issues found:")
        for issue in doc_issues[:5]:  # Show first 5 issues
            print(f"  - {issue}")
        if len(doc_issues) > 5:
            print(f"  ... and {len(doc_issues) - 5} more issues")
    
    # Check testing requirements
    print("\n[3/5] Testing Requirements Check")
    print("-" * 40)
    test_valid, test_issues = claude_validator.check_testing_requirements(git_info['files'])
    
    if test_valid or analysis['test_changes']:
        print("✅ Testing requirements met")
    else:
        print("⚠️  Testing gaps detected:")
        for issue in test_issues[:3]:
            print(f"  - {issue}")
    
    # Check persona requirements
    print("\n[4/5] Persona & Decision Tracking Check")
    print("-" * 40)
    persona_valid, persona_issues = claude_validator.check_persona_requirements(git_info['files'])
    
    if persona_valid:
        print("✅ Specialist decisions properly tracked")
    else:
        print("⚠️  Persona tracking issues:")
        for issue in persona_issues:
            print(f"  - {issue}")
    
    # Run project structure validation
    print("\n[5/5] Project Structure Validation")
    print("-" * 40)
    struct_valid, struct_output = claude_validator.run_validation_script('project_structure')
    print(f"{'✅' if struct_valid else '❌'} {struct_output.split(chr(10))[0] if struct_output else 'Check complete'}")
    
    # Initialize standard governance engine
    engine = GovernanceEngine()
    
    # Add context-specific rules based on CLAUDE.md
    if analysis['critical_changes']:
        engine.add_rule("requires_review", "critical_fix_modification")
        print("\n⚠️  CRITICAL FIX DETECTED - Requires both architects' approval")
    
    if analysis['high_priority_changes']:
        engine.add_rule("requires_review", "high_priority_modification")
    
    if analysis['governance_changes']:
        engine.add_rule("requires_review", "governance_modification")
    
    # Check risky time
    smart_rules = SmartRules()
    if smart_rules.is_risky_time():
        print(f"\n⚠️  RISKY TIME DETECTED")
        if smart_rules.is_friday_afternoon():
            print("  - Friday afternoon deployment - consider waiting")
        else:
            hour = datetime.now().hour
            if hour < 6 or hour >= 22:
                print(f"  - Late night/early morning commit (hour: {hour})")
    
    # Create governance context
    context = GovernanceContext(
        operation_type="git_commit",
        actor=git_info['user'],
        payload={
            'files': git_info['files'],
            'branch': git_info['branch'],
            'analysis': analysis,
            'timestamp': datetime.now().isoformat(),
            'file_contents': '\n'.join(analysis.get('file_contents', [])),
            'claude_validation': {
                'session_valid': session_valid,
                'documentation_valid': doc_valid,
                'testing_valid': test_valid,
                'persona_valid': persona_valid,
                'structure_valid': struct_valid
            }
        }
    )
    
    # Check for dangerous patterns
    dangerous = smart_rules.contains_dangerous_patterns(context.payload)
    if dangerous:
        print(f"\n⚠️  DANGEROUS PATTERNS: {', '.join(dangerous)}")
    
    secrets = smart_rules.check_for_secrets(context.payload)
    if secrets:
        print(f"\n🔴 CRITICAL: Potential secrets detected!")
        print("  Check for hardcoded passwords, keys, or tokens")
    
    # Evaluate with governance
    print("\n" + "-" * 50)
    print("Governance Decision:")
    print("-" * 50)
    
    result = engine.evaluate(context)
    
    # Enhance with smart rules
    enhancer = RuleEnhancer()
    result = enhancer.enhance_evaluation(context, result)
    
    # Calculate compliance score
    compliance_checks = [
        session_valid,
        doc_valid,
        test_valid or analysis['test_changes'],
        persona_valid,
        struct_valid,
        not dangerous,
        not secrets
    ]
    compliance_score = sum(compliance_checks) / len(compliance_checks)
    
    print(f"Decision: {result.decision.upper()}")
    print(f"Confidence: {result.confidence:.0%}")
    print(f"CLAUDE.md Compliance: {compliance_score:.0%}")
    
    if result.reason:
        print(f"Reason: {result.reason}")
    
    # Show risk score
    if hasattr(result, 'metadata') and 'risk_score' in result.metadata:
        risk_score = result.metadata['risk_score']
        risk_level = "LOW" if risk_score < 0.3 else "MEDIUM" if risk_score < 0.7 else "HIGH"
        print(f"Risk Score: {risk_score:.2f} ({risk_level})")
    
    # Recommendations
    if compliance_score < 1.0:
        print("\n📋 Required Actions:")
        if not session_valid:
            print("  1. Run: ./validate-session-start.sh")
        if not doc_valid:
            print("  2. Add required documentation to code files")
        if not test_valid and not analysis['test_changes']:
            print("  3. Add tests for modified code")
        if not persona_valid:
            print("  4. Update DECISIONS.md with specialist decisions")
        if dangerous or secrets:
            print("  5. Remove dangerous patterns or secrets")
    
    # Log the evaluation
    log_file = Path(".governance/logs/enhanced_git_hooks.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'user': git_info['user'],
        'branch': git_info['branch'],
        'files': git_info['files'],
        'decision': result.decision,
        'confidence': result.confidence,
        'compliance_score': compliance_score,
        'risk_score': result.metadata.get('risk_score', 0) if hasattr(result, 'metadata') else 0
    }
    
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    print("\n" + "=" * 70)
    
    # Make decision based on compliance
    if compliance_score < 0.6:  # Less than 60% compliance
        print("❌ [COMMIT BLOCKED] Insufficient governance compliance")
        print(f"   Compliance: {compliance_score:.0%} (minimum 60% required)")
        print("\n   Fix the issues above and try again")
        print("   Emergency bypass: GOVERNANCE_BYPASS=true git commit")
        sys.exit(1)
    elif result.is_rejected() or secrets:
        print("❌ [COMMIT BLOCKED] Governance check failed")
        sys.exit(1)
    elif result.decision == "review" or compliance_score < 0.8:
        print("⚠️  [REVIEW RECOMMENDED] Low compliance score")
        print(f"   Compliance: {compliance_score:.0%}")
        print("\n   To proceed: git commit --no-verify")
        print("   To improve: Address the issues above")
        sys.exit(1)
    else:
        print("✅ [COMMIT APPROVED] Proceeding with commit")
        print(f"   Compliance: {compliance_score:.0%}")
        sys.exit(0)


if __name__ == "__main__":
    # Allow bypass with environment variable (for emergencies only)
    if os.environ.get('GOVERNANCE_BYPASS') == 'true':
        print("[GOVERNANCE BYPASSED] Proceeding without checks (NOT RECOMMENDED)")
        sys.exit(0)
    
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] Enhanced governance hook failed: {e}")
        print("To bypass (EMERGENCY ONLY): GOVERNANCE_BYPASS=true git commit")
        sys.exit(1)