#!/usr/bin/env python
"""
Enhanced Three-Persona Governance Enforcer v4.0
Integrates intelligent automation, predictive analytics, and adaptive learning
"""

import os
import sys
import asyncio
import json
import re
import subprocess
import hashlib
import ast
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
from enum import Enum

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from persona_manager import PersonaManager, PersonaType
from rules_enforcement import RulesEnforcementEngine
from cache_manager import IntelligentCache
from config import Config

class GovernanceLevel(Enum):
    """Adaptive governance strictness levels"""
    STRICT = "strict"       # New team members, critical systems
    BALANCED = "balanced"   # Mixed experience team
    STREAMLINED = "streamlined"  # Senior team, stable systems
    ADAPTIVE = "adaptive"   # Self-adjusting based on metrics

class EnhancedGovernanceEnforcer:
    """
    V4.0 Governance System with:
    - Intelligent automation
    - Predictive analytics
    - Adaptive learning
    - Streamlined workflows
    """
    
    def __init__(self, level: GovernanceLevel = GovernanceLevel.ADAPTIVE):
        self.config = Config()
        self.persona_manager = PersonaManager()
        self.rules_engine = RulesEnforcementEngine()
        self.cache = IntelligentCache()
        self.governance_level = level
        
        # V4.0 Features
        self.evidence_cache = {}
        self.challenge_history = []
        self.learning_metrics = {
            'assumption_patterns': {},
            'violation_trends': [],
            'team_velocity': []
        }
        self.predictive_model = self._initialize_predictive_model()
        
    def _initialize_predictive_model(self) -> Dict:
        """Initialize predictive analytics for governance"""
        return {
            'risk_indicators': [],
            'compliance_trends': [],
            'fatigue_indicators': [],
            'effectiveness_metrics': {}
        }
    
    # ==================== SMART EVIDENCE COLLECTION ====================
    
    async def auto_collect_evidence(self, files: List[str]) -> Dict:
        """
        Automatically collect appropriate evidence based on file types
        30-second execution target
        """
        evidence = {
            'timestamp': datetime.now().isoformat(),
            'files_analyzed': len(files),
            'evidence_collected': {}
        }
        
        # Parallel evidence collection for speed
        tasks = []
        for filepath in files:
            if filepath.endswith('.py'):
                tasks.append(self._collect_python_evidence(filepath))
            elif filepath.endswith(('.yaml', '.yml')):
                tasks.append(self._collect_yaml_evidence(filepath))
            elif filepath.endswith('.json'):
                tasks.append(self._collect_json_evidence(filepath))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if not isinstance(result, Exception):
                    evidence['evidence_collected'][files[i]] = result
        
        return evidence
    
    async def _collect_python_evidence(self, filepath: str) -> Dict:
        """Collect evidence from Python files"""
        evidence = {
            'type': 'python',
            'metrics': {},
            'quality_issues': [],
            'governance_compliance': True
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Performance metrics
            import ast
            tree = ast.parse(content)
            evidence['metrics'] = {
                'functions': len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                'classes': len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                'lines': len(lines),
                'complexity': self._calculate_complexity(tree)
            }
            
            # Quality checks
            evidence['quality_issues'] = await self._scan_quality_issues(content, filepath)
            
            # Governance compliance
            evidence['governance_compliance'] = len(evidence['quality_issues']) == 0
            
        except Exception as e:
            evidence['error'] = str(e)
            evidence['governance_compliance'] = False
        
        return evidence
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity
    
    # ==================== INTELLIGENT CHALLENGE SYSTEM ====================
    
    async def generate_persona_challenges(self, changes: Dict) -> Dict:
        """
        Generate intelligent cross-persona challenges
        Based on change analysis and historical patterns
        """
        challenges = {
            'generated_at': datetime.now().isoformat(),
            'sarah_challenges': [],
            'marcus_challenges': [],
            'emily_challenges': []
        }
        
        # Analyze changes to determine challenge focus
        for filepath, evidence in changes.items():
            if 'ai' in filepath.lower() or 'claude' in filepath.lower():
                # Sarah focuses on AI integration
                challenges['sarah_challenges'].append({
                    'target': 'marcus',
                    'challenge': f"Verify performance impact of AI changes in {filepath}",
                    'evidence_required': ['benchmark', 'profiling'],
                    'priority': 'high'
                })
                challenges['sarah_challenges'].append({
                    'target': 'emily',
                    'challenge': f"Validate user experience for AI features in {filepath}",
                    'evidence_required': ['ui_test', 'accessibility'],
                    'priority': 'medium'
                })
            
            if 'cache' in filepath.lower() or 'database' in filepath.lower():
                # Marcus focuses on system performance
                challenges['marcus_challenges'].append({
                    'target': 'sarah',
                    'challenge': f"Demonstrate AI operations handle cache/db changes in {filepath}",
                    'evidence_required': ['integration_test', 'fallback_test'],
                    'priority': 'high'
                })
                challenges['marcus_challenges'].append({
                    'target': 'emily',
                    'challenge': f"Show user impact of performance changes in {filepath}",
                    'evidence_required': ['response_time', 'error_handling'],
                    'priority': 'medium'
                })
            
            if 'ui' in filepath.lower() or 'frontend' in filepath.lower():
                # Emily focuses on user experience
                challenges['emily_challenges'].append({
                    'target': 'sarah',
                    'challenge': f"Verify AI features are user-friendly in {filepath}",
                    'evidence_required': ['usability_test', 'clarity_check'],
                    'priority': 'high'
                })
                challenges['emily_challenges'].append({
                    'target': 'marcus',
                    'challenge': f"Ensure UI performance meets standards in {filepath}",
                    'evidence_required': ['load_time', 'responsiveness'],
                    'priority': 'medium'
                })
        
        # Apply adaptive learning to optimize challenges
        challenges = self._optimize_challenges_with_learning(challenges)
        
        return challenges
    
    def _optimize_challenges_with_learning(self, challenges: Dict) -> Dict:
        """Use historical data to optimize challenge generation"""
        # Reduce repetitive challenges
        for persona in ['sarah_challenges', 'marcus_challenges', 'emily_challenges']:
            unique_challenges = []
            seen = set()
            
            for challenge in challenges[persona]:
                challenge_key = f"{challenge['target']}:{challenge['challenge'][:30]}"
                if challenge_key not in seen:
                    seen.add(challenge_key)
                    unique_challenges.append(challenge)
            
            challenges[persona] = unique_challenges
        
        return challenges
    
    # ==================== ASSUMPTION DETECTION ====================
    
    async def rapid_assumption_scan(self, content: str, filepath: str = "") -> List[Dict]:
        """
        AI-powered assumption detection with pattern matching
        Enhanced with learning from past detections
        """
        assumptions = []
        
        # Base assumption patterns
        assumption_patterns = [
            (r'\b(should|probably|likely|assume|expect)\s+\w+', 'uncertainty'),
            (r'#\s*(TODO|FIXME|HACK|XXX)', 'incomplete'),
            (r'(magic|hardcode|temporary|quick\s+fix)', 'technical_debt'),
            (r'(I\s+think|might\s+be|seems\s+like)', 'opinion')
        ]
        
        # Add learned patterns from history
        if 'assumption_patterns' in self.learning_metrics:
            for pattern, category in self.learning_metrics['assumption_patterns'].items():
                assumption_patterns.append((pattern, category))
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            for pattern, category in assumption_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    assumptions.append({
                        'file': filepath,
                        'line': i,
                        'category': category,
                        'content': line.strip()[:100],
                        'pattern': pattern
                    })
        
        # Update learning metrics
        self._update_assumption_learning(assumptions)
        
        return assumptions
    
    def _update_assumption_learning(self, assumptions: List[Dict]):
        """Learn from detected assumptions to improve future detection"""
        for assumption in assumptions:
            pattern = assumption['pattern']
            if pattern in self.learning_metrics['assumption_patterns']:
                self.learning_metrics['assumption_patterns'][pattern] += 1
            else:
                self.learning_metrics['assumption_patterns'][pattern] = 1
    
    # ==================== PREDICTIVE ANALYTICS ====================
    
    def predict_governance_risks(self) -> Dict:
        """
        Predict potential governance failures before they occur
        Uses historical data and trend analysis
        """
        predictions = {
            'risk_level': 'low',
            'risk_areas': [],
            'recommendations': []
        }
        
        # Analyze violation trends
        if len(self.learning_metrics['violation_trends']) > 5:
            recent_violations = self.learning_metrics['violation_trends'][-5:]
            violation_rate = sum(recent_violations) / len(recent_violations)
            
            if violation_rate > 0.3:
                predictions['risk_level'] = 'high'
                predictions['risk_areas'].append('Increasing violation trend')
                predictions['recommendations'].append('Increase automation and training')
            elif violation_rate > 0.1:
                predictions['risk_level'] = 'medium'
                predictions['risk_areas'].append('Moderate violation rate')
                predictions['recommendations'].append('Review common violation patterns')
        
        # Check for compliance fatigue
        if self._detect_compliance_fatigue():
            predictions['risk_level'] = 'high'
            predictions['risk_areas'].append('Compliance fatigue detected')
            predictions['recommendations'].append('Streamline governance processes')
        
        # Predict assumption cascades
        if self._predict_assumption_cascade():
            predictions['risk_level'] = 'critical'
            predictions['risk_areas'].append('Assumption cascade risk')
            predictions['recommendations'].append('Immediate validation required')
        
        return predictions
    
    def _detect_compliance_fatigue(self) -> bool:
        """Detect if team is experiencing governance fatigue"""
        if not self.challenge_history:
            return False
        
        # Check if challenge resolution time is increasing
        recent_challenges = self.challenge_history[-10:]
        if len(recent_challenges) < 5:
            return False
        
        resolution_times = [c.get('resolution_time', 0) for c in recent_challenges]
        avg_early = sum(resolution_times[:5]) / 5
        avg_recent = sum(resolution_times[5:]) / 5
        
        return avg_recent > avg_early * 1.5  # 50% increase indicates fatigue
    
    def _predict_assumption_cascade(self) -> bool:
        """Predict if assumptions might cascade into failures"""
        assumption_count = sum(self.learning_metrics['assumption_patterns'].values())
        return assumption_count > 20  # Threshold for cascade risk
    
    # ==================== ADAPTIVE GOVERNANCE ====================
    
    def adapt_governance_level(self, team_metrics: Dict) -> GovernanceLevel:
        """
        Dynamically adjust governance strictness based on team performance
        """
        if self.governance_level != GovernanceLevel.ADAPTIVE:
            return self.governance_level
        
        score = 0
        
        # Factor in violation rate
        if 'violation_rate' in team_metrics:
            if team_metrics['violation_rate'] < 0.05:
                score += 2  # Very low violations
            elif team_metrics['violation_rate'] < 0.1:
                score += 1  # Low violations
            else:
                score -= 1  # High violations
        
        # Factor in test coverage
        if 'test_coverage' in team_metrics:
            if team_metrics['test_coverage'] > 80:
                score += 1
            elif team_metrics['test_coverage'] < 60:
                score -= 1
        
        # Factor in team experience
        if 'avg_experience_years' in team_metrics:
            if team_metrics['avg_experience_years'] > 5:
                score += 1
            elif team_metrics['avg_experience_years'] < 2:
                score -= 1
        
        # Determine governance level
        if score >= 3:
            return GovernanceLevel.STREAMLINED
        elif score >= 0:
            return GovernanceLevel.BALANCED
        else:
            return GovernanceLevel.STRICT
    
    # ==================== SMART VALIDATION ====================
    
    async def validate_with_evidence(self, challenge: Dict, response: Dict) -> Dict:
        """
        Validate challenge responses with required evidence
        30-second validation target
        """
        validation = {
            'challenge_id': challenge.get('id', 'unknown'),
            'validated': False,
            'evidence_provided': [],
            'evidence_missing': [],
            'recommendations': []
        }
        
        required_evidence = challenge.get('evidence_required', [])
        provided_evidence = response.get('evidence', {})
        
        for evidence_type in required_evidence:
            if evidence_type in provided_evidence:
                # Validate evidence quality
                if self._validate_evidence_quality(evidence_type, provided_evidence[evidence_type]):
                    validation['evidence_provided'].append(evidence_type)
                else:
                    validation['evidence_missing'].append(evidence_type)
                    validation['recommendations'].append(f"Improve {evidence_type} evidence quality")
            else:
                validation['evidence_missing'].append(evidence_type)
                validation['recommendations'].append(f"Provide {evidence_type} evidence")
        
        validation['validated'] = len(validation['evidence_missing']) == 0
        
        # Update challenge history for learning
        self.challenge_history.append({
            'challenge': challenge,
            'response': response,
            'validation': validation,
            'timestamp': datetime.now().isoformat()
        })
        
        return validation
    
    def _validate_evidence_quality(self, evidence_type: str, evidence: Any) -> bool:
        """Check if provided evidence meets quality standards"""
        quality_checks = {
            'benchmark': lambda e: 'measurements' in e and 'baseline' in e,
            'test': lambda e: 'passed' in e and e['passed'] is True,
            'profiling': lambda e: 'performance_data' in e,
            'code_inspection': lambda e: 'findings' in e or 'issues' in e
        }
        
        if evidence_type in quality_checks:
            return quality_checks[evidence_type](evidence)
        
        return bool(evidence)  # Default: any evidence is acceptable
    
    # ==================== REPORTING ====================
    
    async def generate_governance_report(self, results: Dict) -> Dict:
        """Generate comprehensive governance report with predictions"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'governance_level': self.governance_level.value,
            'summary': {},
            'details': results,
            'predictions': self.predict_governance_risks(),
            'recommendations': []
        }
        
        # Calculate summary metrics
        total_files = results.get('files_analyzed', 0)
        violations = results.get('violations', [])
        assumptions = results.get('assumptions', [])
        
        report['summary'] = {
            'files_analyzed': total_files,
            'violations_found': len(violations),
            'assumptions_detected': len(assumptions),
            'governance_score': self._calculate_governance_score(results),
            'status': 'PASS' if len(violations) == 0 else 'FAIL'
        }
        
        # Generate recommendations based on adaptive learning
        if len(violations) > 0:
            report['recommendations'].append("Fix violations before committing")
        
        if len(assumptions) > 5:
            report['recommendations'].append("Review and validate assumptions")
        
        if report['predictions']['risk_level'] in ['high', 'critical']:
            report['recommendations'].extend(report['predictions']['recommendations'])
        
        return report
    
    def _calculate_governance_score(self, results: Dict) -> float:
        """Calculate overall governance compliance score"""
        score = 100.0
        
        # Deduct for violations
        violations = results.get('violations', [])
        score -= len(violations) * 5
        
        # Deduct for assumptions
        assumptions = results.get('assumptions', [])
        score -= len(assumptions) * 2
        
        # Deduct for missing evidence
        evidence = results.get('evidence_collected', {})
        if not evidence:
            score -= 10
        
        return max(0, min(100, score))
    
    # ==================== MAIN ENFORCEMENT ====================
    
    async def enforce_governance(self, files: List[str]) -> Dict:
        """
        Main governance enforcement with all v4.0 features
        Target: < 30 seconds for typical commit
        """
        print("[GOVERNANCE] Starting enhanced enforcement...")
        
        results = {
            'files_analyzed': files,
            'violations': [],
            'assumptions': [],
            'challenges': {},
            'evidence_collected': {},
            'governance_report': {}
        }
        
        # Parallel execution for speed
        tasks = [
            self.auto_collect_evidence(files),
            self._scan_for_violations(files),
            self._detect_assumptions_batch(files)
        ]
        
        evidence, violations, assumptions = await asyncio.gather(*tasks)
        
        results['evidence_collected'] = evidence
        results['violations'] = violations
        results['assumptions'] = assumptions
        
        # Generate intelligent challenges
        results['challenges'] = await self.generate_persona_challenges(
            evidence.get('evidence_collected', {})
        )
        
        # Generate report with predictions
        results['governance_report'] = await self.generate_governance_report(results)
        
        # Adaptive learning update
        self._update_learning_metrics(results)
        
        return results
    
    async def _scan_for_violations(self, files: List[str]) -> List[Dict]:
        """Scan for governance violations"""
        violations = []
        
        for filepath in files:
            if not os.path.exists(filepath):
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Check for magic variables line by line
                magic_patterns = [
                    (r'\b(localhost|127\.0\.0\.1)\b', 'hardcoded_host'),
                    (r'\b(3000|8000|5432)\b', 'hardcoded_port'),
                    (r'(api_key|secret|password)\s*=\s*["\'][\w]+["\']', 'hardcoded_credential')
                ]
                
                for line_num, line in enumerate(lines, 1):
                    # Skip lines that are setting environment variables or config defaults
                    if any(skip in line for skip in ['os.environ[', 'getenv(', 'Field(', '# Default', '# Fallback']):
                        continue
                        
                    for pattern, violation_type in magic_patterns:
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            violations.append({
                                'file': filepath,
                                'line': line_num,
                                'type': violation_type,
                                'content': match.group(0)
                            })
                        
            except Exception as e:
                print(f"[WARN] Could not scan {filepath}: {e}")
        
        return violations
    
    async def _detect_assumptions_batch(self, files: List[str]) -> List[Dict]:
        """Detect assumptions in batch of files"""
        all_assumptions = []
        
        for filepath in files:
            if not os.path.exists(filepath):
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                assumptions = await self.rapid_assumption_scan(content, filepath)
                all_assumptions.extend(assumptions)
                
            except Exception as e:
                print(f"[WARN] Could not scan {filepath}: {e}")
        
        return all_assumptions
    
    async def _scan_quality_issues(self, content: str, filepath: str) -> List[Dict]:
        """Scan for code quality issues"""
        issues = []
        
        # Check for missing docstrings
        import ast
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        issues.append({
                            'type': 'missing_docstring',
                            'line': node.lineno,
                            'name': node.name
                        })
        except Exception as e:
            print(f"[WARNING] Could not analyze {file_path}: {e}")
        
        return issues
    
    def _update_learning_metrics(self, results: Dict):
        """Update learning metrics for continuous improvement"""
        # Track violation trends
        violation_count = len(results.get('violations', []))
        self.learning_metrics['violation_trends'].append(violation_count)
        
        # Keep only recent history
        if len(self.learning_metrics['violation_trends']) > 100:
            self.learning_metrics['violation_trends'] = self.learning_metrics['violation_trends'][-100:]
        
        # Track team velocity (files changed per enforcement)
        self.learning_metrics['team_velocity'].append(len(results.get('files_analyzed', [])))
    
    def print_report(self, results: Dict):
        """Print formatted governance report"""
        report = results.get('governance_report', {})
        
        print("\n" + "="*60)
        print("ENHANCED GOVERNANCE ENFORCEMENT REPORT v4.0")
        print("="*60)
        
        # Summary
        summary = report.get('summary', {})
        print(f"\nGovernance Level: {self.governance_level.value.upper()}")
        print(f"Files Analyzed: {summary.get('files_analyzed', 0)}")
        print(f"Governance Score: {summary.get('governance_score', 0):.1f}%")
        print(f"Status: {summary.get('status', 'UNKNOWN')}")
        
        # Violations
        violations = results.get('violations', [])
        if violations:
            print(f"\n[VIOLATIONS] Found {len(violations)} issues:")
            for v in violations[:5]:
                print(f"  - {v['file']}:{v['line']} - {v['type']}")
        
        # Assumptions
        assumptions = results.get('assumptions', [])
        if assumptions:
            print(f"\n[ASSUMPTIONS] Detected {len(assumptions)} assumptions:")
            for a in assumptions[:5]:
                print(f"  - {a['file']}:{a['line']} - {a['category']}")
        
        # Challenges
        challenges = results.get('challenges', {})
        total_challenges = sum(len(c) for c in challenges.values())
        if total_challenges > 0:
            print(f"\n[CHALLENGES] Generated {total_challenges} cross-persona challenges")
        
        # Predictions
        predictions = report.get('predictions', {})
        if predictions.get('risk_level') != 'low':
            print(f"\n[PREDICTIONS] Risk Level: {predictions['risk_level'].upper()}")
            for risk in predictions.get('risk_areas', []):
                print(f"  - {risk}")
        
        # Recommendations
        recommendations = report.get('recommendations', [])
        if recommendations:
            print("\n[RECOMMENDATIONS]")
            for rec in recommendations:
                print(f"  - {rec}")
        
        print("="*60)


async def main():
    """Main entry point with CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Governance Enforcer v4.0')
    parser.add_argument('files', nargs='*', help='Files to check')
    parser.add_argument('--level', choices=['strict', 'balanced', 'streamlined', 'adaptive'],
                       default='adaptive', help='Governance strictness level')
    parser.add_argument('--quick', action='store_true', help='Quick mode (30 seconds)')
    parser.add_argument('--report', help='Save report to JSON file')
    
    args = parser.parse_args()
    
    # Get files to check
    if not args.files:
        # Get changed files from git
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            args.files = [f for f in result.stdout.strip().split('\n') if f]
    
    if not args.files:
        print("[INFO] No files to check")
        sys.exit(0)
    
    # Initialize enforcer
    level = GovernanceLevel[args.level.upper()]
    enforcer = EnhancedGovernanceEnforcer(level)
    
    # Run enforcement
    start_time = datetime.now()
    results = await enforcer.enforce_governance(args.files)
    duration = (datetime.now() - start_time).total_seconds()
    
    # Print report
    enforcer.print_report(results)
    print(f"\n[TIME] Governance check completed in {duration:.1f} seconds")
    
    # Save report if requested
    if args.report:
        # Create a safe version for JSON serialization
        safe_results = {
            'governance_report': results.get('governance_report', {}),
            'violations': results.get('violations', []),
            'assumptions': results.get('assumptions', []),
            'files_analyzed': results.get('files_analyzed', []),
            'challenges_count': sum(len(c) for c in results.get('challenges', {}).values())
        }
        with open(args.report, 'w') as f:
            json.dump(safe_results, f, indent=2, default=str)
        print(f"[SAVED] Report saved to {args.report}")
    
    # Exit code based on status
    status = results.get('governance_report', {}).get('summary', {}).get('status')
    sys.exit(0 if status == 'PASS' else 1)


if __name__ == "__main__":
    asyncio.run(main())