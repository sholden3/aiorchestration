#!/usr/bin/env python3
"""Test to demonstrate persona assumption fighting"""

import requests
import json
import time

def test_controversial_topic():
    """Test with a topic that should trigger assumption debates"""
    
    print("="*60)
    print("TESTING PERSONA ORCHESTRATION WITH ASSUMPTION FIGHTING")
    print("="*60)
    
    # Create a controversial request that will trigger debates
    test_request = {
        "prompt": """
        Should we replace our entire development team with AI agents? 
        Consider: productivity, cost, innovation, team morale, and long-term sustainability.
        The company has 50 developers and a limited budget.
        """,
        "persona": "strategic_advisor",
        "context": {
            "company_size": "medium",
            "industry": "software",
            "developers": 50,
            "budget": "limited",
            "timeline": "6 months"
        },
        "use_cache": False
    }
    
    print("\nRequest Topic: AI replacing human developers")
    print("This should trigger debates between personas about:")
    print("- Technical feasibility assumptions")
    print("- Economic impact assumptions")
    print("- Human factor assumptions")
    print("-"*60)
    
    start_time = time.time()
    
    try:
        print("\nSending to orchestration engine...")
        response = requests.post(
            "http://localhost:8001/ai/orchestrated",
            json=test_request,
            timeout=60
        )
        
        elapsed_time = time.time() - start_time
        result = response.json()
        
        print(f"\nResponse received in {elapsed_time:.2f} seconds")
        print("-"*60)
        
        if result.get('success'):
            print("\nORCHESTRATION SUCCESSFUL!")
            print(f"Consensus Decision Length: {len(result.get('response', ''))}")
            print(f"Execution Time: {result.get('execution_time_ms')} ms")
            
            # Show the actual decision
            print("\n--- CONSENSUS DECISION ---")
            print(result.get('response', 'No response'))[:500] + "..." if len(result.get('response', '')) > 500 else result.get('response', 'No response')
            
        else:
            print(f"\nError: {result.get('error')}")
            
    except Exception as e:
        print(f"\nError occurred: {e}")
    
    print("\n" + "="*60)
    
    # Check orchestration status
    status = requests.get("http://localhost:8001/orchestration/status").json()
    print("\nPost-Request Orchestration Metrics:")
    print(f"  Tasks Completed: {status['tasks']['completed']}")
    print(f"  Tasks Failed: {status['tasks']['failed']}")
    print(f"  Agents Used: {status['agents']['busy']} busy, {status['agents']['idle']} idle")

if __name__ == "__main__":
    test_controversial_topic()
    print("\nTest completed!")