#!/usr/bin/env python3
"""
Test script to validate the orchestration system with assumption fighting
"""

import requests
import json
import time

def test_orchestrated_endpoint():
    """Test the orchestrated endpoint with persona assumption fighting"""
    
    url = "http://localhost:8001/ai/orchestrated"
    
    # Create a test request that will trigger assumption fighting
    test_request = {
        "prompt": "Should we migrate our monolithic application to microservices architecture? Consider performance, maintainability, and team expertise.",
        "persona": "technical_architect",
        "context": {
            "current_architecture": "monolithic",
            "team_size": 5,
            "experience_level": "intermediate",
            "current_issues": ["slow deployments", "difficulty scaling specific features"],
            "budget": "limited"
        },
        "use_cache": False
    }
    
    print("=" * 60)
    print("Testing Orchestrated AI with Assumption Fighting")
    print("=" * 60)
    print(f"\nRequest:")
    print(json.dumps(test_request, indent=2))
    print("\nSending request to orchestration engine...")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=test_request, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        elapsed_time = time.time() - start_time
        
        print(f"\n✓ Response received in {elapsed_time:.2f} seconds")
        print("-" * 60)
        print("\nResult:")
        print(f"Success: {result.get('success')}")
        print(f"Persona Used: {result.get('persona_used')}")
        print(f"Execution Time: {result.get('execution_time_ms')} ms")
        print(f"\nResponse Content:")
        print("-" * 40)
        print(result.get('response', 'No response content'))
        
        if result.get('error'):
            print(f"\n⚠ Error: {result['error']}")
        
        print("\n" + "=" * 60)
        
        # Check orchestration status after request
        status_response = requests.get("http://localhost:8001/orchestration/status")
        status = status_response.json()
        
        print("\nOrchestration Status After Request:")
        print(f"Tasks Completed: {status['tasks']['completed']}")
        print(f"Tasks Failed: {status['tasks']['failed']}")
        print(f"Total Tokens Used: {status['performance']['total_tokens_used']}")
        
    except requests.exceptions.Timeout:
        print("⚠ Request timed out after 60 seconds")
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

def test_regular_endpoint():
    """Test the regular endpoint for comparison"""
    
    url = "http://localhost:8001/ai/execute"
    
    test_request = {
        "prompt": "What are the benefits of microservices?",
        "persona": None,
        "context": {},
        "use_cache": True
    }
    
    print("\n" + "=" * 60)
    print("Testing Regular AI Endpoint (for comparison)")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=test_request, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Cached: {result.get('cached')}")
        print(f"Execution Time: {result.get('execution_time_ms')} ms")
        
    except Exception as e:
        print(f"Regular endpoint error: {e}")

if __name__ == "__main__":
    # Test the orchestrated endpoint with persona assumption fighting
    test_orchestrated_endpoint()
    
    # Test regular endpoint for comparison
    test_regular_endpoint()
    
    print("\n✓ Test completed")