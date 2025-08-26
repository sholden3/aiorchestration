#!/usr/bin/env python3
"""Simple test for orchestration system"""

import requests
import json

# First check health
health = requests.get("http://localhost:8001/health").json()
print("Service Health:", health["status"])

# Check orchestration status
status = requests.get("http://localhost:8001/orchestration/status").json()
print("\nOrchestration Status:")
print(f"  Running: {status['is_running']}")
print(f"  Agents: {status['agents']['total']} total, {status['agents']['active']} active")
print(f"  Governance: {status['governance_active']}")
print(f"  Persona Orchestration: {status['persona_orchestration_active']}")

# Test orchestrated endpoint
print("\nTesting Orchestrated Endpoint...")
test_request = {
    "prompt": "What are the pros and cons of microservices?",
    "persona": "architect",
    "context": {"team_size": 5},
    "use_cache": False
}

try:
    response = requests.post("http://localhost:8001/ai/orchestrated", 
                            json=test_request, 
                            timeout=30)
    result = response.json()
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Success: {result.get('success')}")
    if result.get('success'):
        print(f"Response Length: {len(result.get('response', ''))}")
        print(f"Execution Time: {result.get('execution_time_ms')} ms")
    else:
        print(f"Error: {result.get('error')}")
        
except Exception as e:
    print(f"Error: {e}")

print("\nDone!")