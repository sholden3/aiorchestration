#!/usr/bin/env python3
"""Test the new API endpoints"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_personas_api():
    """Test persona management APIs"""
    print("="*60)
    print("TESTING PERSONA APIs")
    print("="*60)
    
    # Get all personas
    response = requests.get(f"{BASE_URL}/personas/")
    personas = response.json()
    print("\nAvailable Personas:")
    for persona in personas["personas"]:
        print(f"  - {persona['name']} ({persona['role']})")
        print(f"    Expertise: {', '.join(persona['expertise_areas'])}")
        print(f"    Decision Style: {persona['decision_style']}")
    
    # Get specific persona details
    response = requests.get(f"{BASE_URL}/personas/sarah_chen")
    if response.status_code == 200:
        details = response.json()
        print(f"\nDetailed info for {details['name']}:")
        print(f"  Strengths: {', '.join(details['strengths'])}")
        print(f"  Weaknesses: {', '.join(details['weaknesses'])}")

def test_agents_api():
    """Test AI agent management APIs"""
    print("\n" + "="*60)
    print("TESTING AGENT APIs")
    print("="*60)
    
    # Get all agents
    response = requests.get(f"{BASE_URL}/agents/")
    agents = response.json()
    print(f"\nTotal Agents: {agents['total']}")
    print(f"Active: {agents['active']}, Offline: {agents['offline']}")
    
    for agent in agents["agents"]:
        print(f"\n  Agent: {agent['agent_id']}")
        print(f"    Type: {agent['agent_type']}")
        print(f"    Status: {agent['status']}")
        print(f"    Success Rate: {agent['performance_metrics']['success_rate']}")

def test_rules_api():
    """Test rules and best practices APIs"""
    print("\n" + "="*60)
    print("TESTING RULES APIs")
    print("="*60)
    
    # Get all rules
    response = requests.get(f"{BASE_URL}/rules/")
    rules = response.json()
    print("\nActive Rules:")
    for rule in rules["rules"]:
        print(f"  [{rule['rule_id']}] {rule['title']}")
        print(f"    Category: {rule['category']}")
        print(f"    Severity: {rule['severity']}")
        print(f"    Enforcement: {rule['enforcement']}")
    
    # Get best practices
    response = requests.get(f"{BASE_URL}/rules/best-practices")
    practices = response.json()
    print("\nBest Practices:")
    for practice in practices["practices"]:
        print(f"  - {practice['title']} ({practice['domain']})")

def test_assumptions_api():
    """Test assumption management APIs"""
    print("\n" + "="*60)
    print("TESTING ASSUMPTIONS APIs")
    print("="*60)
    
    # Get all assumptions
    response = requests.get(f"{BASE_URL}/assumptions/")
    assumptions = response.json()
    print("\nCurrent Assumptions:")
    for assumption in assumptions["assumptions"]:
        print(f"  [{assumption['assumption_id']}] {assumption['statement']}")
        print(f"    Confidence: {assumption['confidence_level']}")
        print(f"    Validated: {assumption['validated']}")
        print(f"    Impact if wrong: {assumption['impact_if_wrong']}")

def test_governance_api():
    """Test governance APIs"""
    print("\n" + "="*60)
    print("TESTING GOVERNANCE APIs")
    print("="*60)
    
    # Get governance decisions
    response = requests.get(f"{BASE_URL}/governance/decisions")
    decisions = response.json()
    print("\nRecent Governance Decisions:")
    for decision in decisions["decisions"]:
        print(f"  [{decision['decision_id']}] {decision['request_type']}")
        print(f"    Decision: {decision['decision']}")
        print(f"    Consensus: {decision['consensus_level']}")
        print(f"    Votes: {json.dumps(decision['voting_record'], indent=6)}")
    
    # Check consensus on a topic
    response = requests.get(f"{BASE_URL}/governance/consensus-level?topic=microservices")
    consensus = response.json()
    print(f"\nConsensus on '{consensus['topic']}':")
    print(f"  Level: {consensus['consensus_level']}")
    print(f"  Agreeing: {', '.join(consensus['agreeing_personas'])}")
    print(f"  Disagreeing: {', '.join(consensus['disagreeing_personas'])}")

if __name__ == "__main__":
    try:
        test_personas_api()
        test_agents_api()
        test_rules_api()
        test_assumptions_api()
        test_governance_api()
        
        print("\n" + "="*60)
        print("ALL API TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        # Show API documentation link
        print(f"\nFull API documentation available at:")
        print(f"  {BASE_URL}/docs")
        print(f"  {BASE_URL}/openapi.json")
        
    except Exception as e:
        print(f"\nError: {e}")