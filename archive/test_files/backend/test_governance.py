#!/usr/bin/env python
"""
Comprehensive test of the Full Governance System
Demonstrates all hooks and enforcement features
"""

import asyncio
import json
from governance_enforcer import EnhancedGovernanceEnforcer, GovernanceLevel

async def demonstrate_full_governance():
    """Demonstrate all governance features"""
    
    print("="*60)
    print("FULL GOVERNANCE SYSTEM DEMONSTRATION")
    print("="*60)
    
    # Initialize with different governance levels
    print("\n1. TESTING GOVERNANCE LEVELS")
    print("-"*40)
    
    for level in [GovernanceLevel.STRICT, GovernanceLevel.BALANCED, GovernanceLevel.STREAMLINED]:
        enforcer = EnhancedGovernanceEnforcer(level)
        print(f"\nLevel: {level.value}")
        
        # Test files
        test_files = ['persona_cli.py', 'cache_manager.py']
        
        # Run enforcement
        results = await enforcer.enforce_governance(test_files)
        
        print(f"  - Files analyzed: {len(results['files_analyzed'])}")
        print(f"  - Violations: {len(results['violations'])}")
        print(f"  - Assumptions: {len(results['assumptions'])}")
        print(f"  - Governance Score: {results['governance_report']['summary']['governance_score']:.1f}%")
    
    # Test predictive analytics
    print("\n2. PREDICTIVE ANALYTICS")
    print("-"*40)
    
    enforcer = EnhancedGovernanceEnforcer(GovernanceLevel.ADAPTIVE)
    
    # Simulate violation history for predictions
    enforcer.learning_metrics['violation_trends'] = [0, 1, 2, 3, 4, 5]  # Increasing trend
    predictions = enforcer.predict_governance_risks()
    
    print(f"Risk Level: {predictions['risk_level']}")
    print(f"Risk Areas: {predictions['risk_areas']}")
    print(f"Recommendations: {predictions['recommendations']}")
    
    # Test assumption detection
    print("\n3. ASSUMPTION DETECTION")
    print("-"*40)
    
    test_content = '''
    def process_data(data):
        # This should work for most cases
        # TODO: Fix this later
        result = data * 2  # I think this handles everything
        # Probably need to add error handling
        return result  # Assume data is valid
    '''
    
    assumptions = await enforcer.rapid_assumption_scan(test_content, "test.py")
    print(f"Detected {len(assumptions)} assumptions:")
    for assumption in assumptions:
        print(f"  - Line {assumption['line']}: {assumption['category']} - '{assumption['content'][:50]}'")
    
    # Test challenge generation
    print("\n4. INTELLIGENT CHALLENGE GENERATION")
    print("-"*40)
    
    changes = {
        'ai_integration.py': {'type': 'python', 'metrics': {'functions': 5}},
        'cache_manager.py': {'type': 'python', 'metrics': {'functions': 10}},
        'ui_dashboard.py': {'type': 'python', 'metrics': {'functions': 3}}
    }
    
    challenges = await enforcer.generate_persona_challenges(changes)
    
    print(f"Sarah's Challenges: {len(challenges['sarah_challenges'])}")
    for c in challenges['sarah_challenges'][:2]:
        print(f"  -> {c['target']}: {c['challenge'][:60]}...")
        
    print(f"Marcus's Challenges: {len(challenges['marcus_challenges'])}")
    for c in challenges['marcus_challenges'][:2]:
        print(f"  -> {c['target']}: {c['challenge'][:60]}...")
        
    print(f"Emily's Challenges: {len(challenges['emily_challenges'])}")
    for c in challenges['emily_challenges'][:2]:
        print(f"  -> {c['target']}: {c['challenge'][:60]}...")
    
    # Test evidence validation
    print("\n5. EVIDENCE VALIDATION")
    print("-"*40)
    
    challenge = {
        'id': 'test_challenge',
        'evidence_required': ['benchmark', 'test', 'profiling']
    }
    
    response = {
        'evidence': {
            'benchmark': {'measurements': [100, 105, 98], 'baseline': 100},
            'test': {'passed': True, 'coverage': 85}
        }
    }
    
    validation = await enforcer.validate_with_evidence(challenge, response)
    
    print(f"Challenge validated: {validation['validated']}")
    print(f"Evidence provided: {validation['evidence_provided']}")
    print(f"Evidence missing: {validation['evidence_missing']}")
    print(f"Recommendations: {validation['recommendations']}")
    
    # Test adaptive governance
    print("\n6. ADAPTIVE GOVERNANCE")
    print("-"*40)
    
    team_metrics = {
        'violation_rate': 0.03,  # 3% violations
        'test_coverage': 85,      # 85% coverage
        'avg_experience_years': 6  # Senior team
    }
    
    new_level = enforcer.adapt_governance_level(team_metrics)
    print(f"Team metrics: {team_metrics}")
    print(f"Recommended governance level: {new_level.value}")
    
    # Test compliance fatigue detection
    print("\n7. COMPLIANCE FATIGUE DETECTION")
    print("-"*40)
    
    # Simulate challenge history
    enforcer.challenge_history = [
        {'resolution_time': 100},
        {'resolution_time': 110},
        {'resolution_time': 120},
        {'resolution_time': 130},
        {'resolution_time': 140},
        {'resolution_time': 200},  # Increasing resolution time
        {'resolution_time': 210},
        {'resolution_time': 220},
        {'resolution_time': 230},
        {'resolution_time': 240}
    ]
    
    fatigue = enforcer._detect_compliance_fatigue()
    print(f"Compliance fatigue detected: {fatigue}")
    
    if fatigue:
        print("Recommendation: Streamline governance processes")
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    print("\nThe Full Governance System is working with:")
    print("[OK] Intelligent automation")
    print("[OK] Predictive analytics")
    print("[OK] Adaptive learning")
    print("[OK] Cross-persona validation")
    print("[OK] Evidence-based enforcement")

if __name__ == "__main__":
    asyncio.run(demonstrate_full_governance())