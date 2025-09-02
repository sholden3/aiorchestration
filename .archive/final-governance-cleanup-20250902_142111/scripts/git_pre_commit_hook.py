#!/usr/bin/env python3
"""
@fileoverview Git pre-commit hook for enforcing governance rules on commits
@author Dr. Sarah Chen v1.0 - 2025-08-29
@architecture Backend - Git integration hook
@responsibility Validate commits against governance rules before allowing them
@dependencies subprocess, json, pathlib, governance.core modules
@integration_points Git hooks, governance engine, smart rules
@testing_strategy Integration tests with git operations, unit tests for validation
@governance Enforces governance at the git commit boundary

Business Logic Summary:
- Intercept git commits for validation
- Apply governance rules to changed files
- Check for dangerous patterns
- Validate documentation requirements
- Block non-compliant commits

Architecture Integration:
- Integrates with git hook system
- Uses governance engine for validation
- Applies smart rules to changes
- Returns exit codes to git
- Logs validation results

Sarah's Framework Check:
- What breaks first: Large commits with many files timeout
- How we know: Hook execution time monitoring
- Plan B: Batch file processing with progress indication
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Add governance module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from governance.core.engine import GovernanceEngine
from governance.core.context import GovernanceContext
from governance.rules.smart_rules import SmartRules, RuleEnhancer


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
        'file_count': len(files),
        'file_types': set(),
        'file_contents': []  # Store file content for pattern analysis
    }
    
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
        
        # Read file contents if it's a code file
        if file.endswith(('.py', '.js', '.ts', '.java', '.c', '.cpp')):
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    analysis['file_contents'].append(content)
            except Exception:
                pass  # Skip files we can't read
    
    analysis['file_types'] = list(analysis['file_types'])
    return analysis


def main():
    """Main hook logic"""
    print("\n" + "=" * 60)
    print("GOVERNANCE PRE-COMMIT HOOK")
    print("=" * 60)
    
    # Get git information
    git_info = get_git_info()
    
    print(f"User: {git_info['user']}")
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
    print(f"  - Config changes: {analysis['config_changes']}")
    print(f"  - Governance changes: {analysis['governance_changes']}")
    
    # Initialize governance engine
    engine = GovernanceEngine()
    
    # Add context-specific rules
    if analysis['governance_changes']:
        engine.add_rule("requires_review", "governance_modification")
    
    if analysis['config_changes']:
        engine.add_rule("requires_review", "configuration_change")
    
    # Check risky time
    smart_rules = SmartRules()
    if smart_rules.is_risky_time():
        print(f"\n[WARNING] Risky time detected!")
        if smart_rules.is_friday_afternoon():
            print("  - It's Friday afternoon - consider waiting until Monday")
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
            'file_contents': '\n'.join(analysis.get('file_contents', []))  # Include file contents for pattern checking
        }
    )
    
    # Check for dangerous patterns in payload (including file contents)
    dangerous = smart_rules.contains_dangerous_patterns(context.payload)
    if dangerous:
        print(f"\n[WARNING] Dangerous patterns detected: {', '.join(dangerous)}")
    
    secrets = smart_rules.check_for_secrets(context.payload)
    if secrets:
        print(f"\n[CRITICAL] Potential secrets detected!")
        print("  Check your changes for hardcoded passwords, keys, or tokens")
    
    # Evaluate with governance
    print("\n" + "-" * 40)
    print("Governance Evaluation:")
    print("-" * 40)
    
    result = engine.evaluate(context)
    
    # Enhance with smart rules
    enhancer = RuleEnhancer()
    result = enhancer.enhance_evaluation(context, result)
    
    # Display result
    print(f"Decision: {result.decision.upper()}")
    print(f"Confidence: {result.confidence:.0%}")
    
    if result.reason:
        print(f"Reason: {result.reason}")
    
    if result.evidence:
        print(f"Evidence: {', '.join(result.evidence)}")
    
    if hasattr(result, 'warnings') and result.warnings:
        print(f"\nWarnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
    
    if hasattr(result, 'recommendations') and result.recommendations:
        print(f"\nRecommendations:")
        for rec in result.recommendations:
            print(f"  - {rec}")
    
    # Show risk score if available
    if hasattr(result, 'metadata') and 'risk_score' in result.metadata:
        risk_score = result.metadata['risk_score']
        risk_level = "LOW" if risk_score < 0.3 else "MEDIUM" if risk_score < 0.7 else "HIGH"
        print(f"\nRisk Score: {risk_score:.2f} ({risk_level})")
    
    # Log the evaluation
    log_file = Path(".governance/logs/git_hooks.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'user': git_info['user'],
        'branch': git_info['branch'],
        'files': git_info['files'],
        'decision': result.decision,
        'confidence': result.confidence,
        'risk_score': result.metadata.get('risk_score', 0) if hasattr(result, 'metadata') else 0
    }
    
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    print("\n" + "=" * 60)
    
    # Make decision
    if result.is_rejected():
        print("[COMMIT BLOCKED] Governance check failed")
        print("Fix the issues above and try again")
        sys.exit(1)
    elif result.decision == "review":
        print("[REVIEW REQUIRED] Commit needs review")
        print("To proceed anyway: git commit --no-verify")
        sys.exit(1)
    else:
        print("[COMMIT APPROVED] Proceeding with commit")
        sys.exit(0)


if __name__ == "__main__":
    import os
    
    # Allow bypass with environment variable
    if os.environ.get('GOVERNANCE_BYPASS') == 'true':
        print("[GOVERNANCE BYPASSED] Proceeding without checks")
        sys.exit(0)
    
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] Governance hook failed: {e}")
        print("To bypass: GOVERNANCE_BYPASS=true git commit")
        sys.exit(1)