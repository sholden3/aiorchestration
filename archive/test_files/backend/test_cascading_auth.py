"""
Integration tests for cascading authentication
Tests the priority order: Environment Variable -> Config File -> CLI Fallback
Evidence-Based Testing with Measured Results
"""

import asyncio
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import logging

from claude_unified_integration import ClaudeUnifiedIntegration
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestScenario:
    """Test scenario for authentication cascade"""
    
    def __init__(self, name: str, env_var: str = None, config_key: str = None):
        self.name = name
        self.env_var = env_var
        self.config_key = config_key
        self.result = None
        self.mode_detected = None

async def test_cascading_authentication():
    """Test all authentication cascade scenarios"""
    print("=== Testing Cascading Authentication ===\n")
    print("Priority Order: ENV VAR -> CONFIG -> CLI\n")
    
    # Test scenarios
    scenarios = [
        TestScenario("Scenario 1: ENV VAR Present", env_var="test-env-key"),
        TestScenario("Scenario 2: CONFIG Only", config_key="test-config-key"),
        TestScenario("Scenario 3: CLI Fallback"),
        TestScenario("Scenario 4: ENV VAR Override", env_var="override-key", config_key="config-key")
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\n{scenario.name}")
        print("-" * 40)
        
        # Setup environment
        original_env = os.environ.get('ANTHROPIC_API_KEY')
        
        try:
            # Configure environment variable if specified
            if scenario.env_var:
                os.environ['ANTHROPIC_API_KEY'] = scenario.env_var
                print(f"  ENV VAR set: {scenario.env_var[:10]}...")
            else:
                if 'ANTHROPIC_API_KEY' in os.environ:
                    del os.environ['ANTHROPIC_API_KEY']
                print("  ENV VAR: Not set")
            
            # Create config with API key if specified
            config = None
            if scenario.config_key:
                # Create a config instance and set the API key
                config = Config()
                config.ai.anthropic_api_key = scenario.config_key
                print(f"  CONFIG set: {scenario.config_key[:10]}...")
            else:
                print("  CONFIG: Not set")
            
            # Initialize unified integration
            integration = ClaudeUnifiedIntegration(config)
            
            # Determine expected result
            if scenario.env_var:
                expected_key = scenario.env_var
                expected_mode = "SDK with ENV VAR"
            elif scenario.config_key:
                expected_key = scenario.config_key
                expected_mode = "SDK with CONFIG"
            else:
                expected_key = None
                expected_mode = "CLI fallback"
            
            # Verify API key detection
            actual_key = integration.api_key
            actual_mode = str(integration.method).split('.')[-1].upper()
            
            # Check results
            if expected_key:
                if actual_key == expected_key:
                    print(f"  [OK] Correct API key detected: {actual_key[:10]}...")
                    print(f"  [OK] Mode: {actual_mode}")
                    scenario.result = "PASS"
                else:
                    print(f"  [FAIL] Wrong key: expected {expected_key[:10]}..., got {actual_key[:10] if actual_key else 'None'}")
                    scenario.result = "FAIL"
            else:
                if actual_key is None and actual_mode == "CLI":
                    print(f"  [OK] CLI fallback activated (no API key)")
                    print(f"  [OK] Mode: {actual_mode}")
                    scenario.result = "PASS"
                else:
                    print(f"  [FAIL] Expected CLI fallback, got {actual_mode}")
                    scenario.result = "FAIL"
            
            scenario.mode_detected = actual_mode
            results.append(scenario)
            
        finally:
            # Restore original environment
            if original_env:
                os.environ['ANTHROPIC_API_KEY'] = original_env
            elif 'ANTHROPIC_API_KEY' in os.environ:
                del os.environ['ANTHROPIC_API_KEY']
    
    # Summary
    print("\n\n=== Test Summary ===")
    print("-" * 40)
    
    passed = sum(1 for s in results if s.result == "PASS")
    failed = sum(1 for s in results if s.result == "FAIL")
    
    print(f"Total scenarios: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    print("\nDetailed Results:")
    for scenario in results:
        status = "[OK]" if scenario.result == "PASS" else "[FAIL]"
        print(f"  {status} {scenario.name}: {scenario.mode_detected}")
    
    if failed == 0:
        print("\n=== All Cascading Authentication Tests Passed ===")
        return True
    else:
        print(f"\n=== {failed} Tests Failed ===")
        return False

async def main():
    """Run integration tests"""
    print("=" * 50)
    print("CASCADING AUTHENTICATION INTEGRATION TESTS")
    print("=" * 50)
    
    # Run test suite
    auth_passed = await test_cascading_authentication()
    
    return auth_passed

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
