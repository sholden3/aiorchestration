#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows Compatibility Test Script for VRO Crisis Orchestrator

Tests all functionality without Unicode characters to ensure Windows compatibility.
"""

import sys
import os

def test_windows_compatibility():
    """Test all VRO Crisis Orchestrator functionality on Windows"""
    
    print("*** WINDOWS COMPATIBILITY TEST ***")
    print("Python version:", sys.version)
    print("Platform:", sys.platform)
    print("Encoding:", sys.getdefaultencoding())
    print("")
    
    try:
        # Test 1: Import the orchestrator
        print("1. Testing import...")
        from vro_crisis_orchestrator import VRO_CRISIS_ORCHESTRATOR, enhance_claude_prompt
        print("   PASS: Successfully imported VRO_CRISIS_ORCHESTRATOR")
        
        # Test 2: Test crisis detection
        print("\n2. Testing crisis detection...")
        test_input = "Harbor Freight delivery system is returning NULL for all shipments due to circular dependency in timing calculations"
        analysis = VRO_CRISIS_ORCHESTRATOR.analyze_vro_request(test_input)
        
        if analysis.crisis_mode:
            print("   PASS: Crisis mode detected correctly")
            print(f"   Crisis Category: {analysis.vro_crisis_category}")
            print(f"   Required Personas: {analysis.required_personas}")
        else:
            print("   FAIL: Crisis mode not detected")
            return False
        
        # Test 3: Test prompt enhancement
        print("\n3. Testing prompt enhancement...")
        enhanced = enhance_claude_prompt(test_input)
        
        if "VRO CRISIS ORCHESTRATION" in enhanced:
            print("   PASS: Prompt enhanced successfully")
            print(f"   Enhanced prompt length: {len(enhanced)} characters")
        else:
            print("   FAIL: Prompt enhancement failed")
            return False
        
        # Test 4: Test management decision creation
        print("\n4. Testing management decision creation...")
        decision_id = VRO_CRISIS_ORCHESTRATOR.create_management_decision(
            decision_type="Test Decision",
            business_impact="Test Impact",
            timeline_pressure="Test Timeline",
            personas_consulted=["test_persona"],
            persona_recommendations={"test": "test recommendation"}
        )
        
        if decision_id:
            print(f"   PASS: Decision created with ID: {decision_id}")
        else:
            print("   FAIL: Decision creation failed")
            return False
        
        # Test 5: Test dashboard generation
        print("\n5. Testing dashboard generation...")
        dashboard = VRO_CRISIS_ORCHESTRATOR.get_management_dashboard()
        
        if isinstance(dashboard, dict) and "pending_decisions" in dashboard:
            print("   PASS: Dashboard generated successfully")
            print(f"   Pending decisions: {dashboard['pending_decisions']['total']}")
        else:
            print("   FAIL: Dashboard generation failed")
            return False
        
        # Test 6: Test file I/O with proper encoding
        print("\n6. Testing file I/O...")
        VRO_CRISIS_ORCHESTRATOR.save_decisions()
        VRO_CRISIS_ORCHESTRATOR.load_decisions()
        print("   PASS: File I/O operations completed successfully")
        
        # Test 7: Test testing data integration
        print("\n7. Testing data integration...")
        test_data = VRO_CRISIS_ORCHESTRATOR.integrate_testing_data("test_scenario")
        
        if isinstance(test_data, dict):
            print("   PASS: Testing data integration successful")
            print(f"   Available data types: {len(test_data.get('available_data', {}))}")
        else:
            print("   FAIL: Testing data integration failed")
            return False
        
        print("\n*** ALL TESTS PASSED - WINDOWS COMPATIBILITY CONFIRMED ***")
        return True
        
    except UnicodeError as e:
        print(f"   FAIL: Unicode error: {e}")
        return False
    except ImportError as e:
        print(f"   FAIL: Import error: {e}")
        return False
    except Exception as e:
        print(f"   FAIL: Unexpected error: {e}")
        return False

def test_crisis_orchestration_example():
    """Test a complete crisis orchestration example"""
    
    print("\n*** CRISIS ORCHESTRATION EXAMPLE ***")
    
    # Example crisis scenario
    crisis_scenario = """
    Harbor Freight and Home Depot delivery systems are completely down.
    All VRO timing calculations are returning NULL values.
    Circular dependencies in the routing algorithms are causing infinite loops.
    We have a complete business shutdown - no deliveries are possible.
    This needs immediate resolution as it's affecting thousands of customers.
    """
    
    print("Crisis Scenario:")
    print(crisis_scenario)
    
    try:
        from vro_crisis_orchestrator import enhance_claude_prompt
        
        # Generate the enhanced prompt
        enhanced_prompt = enhance_claude_prompt(crisis_scenario)
        
        print("\nEnhanced Prompt Generated:")
        print("=" * 50)
        print(enhanced_prompt)
        print("=" * 50)
        
        print("\n*** CRISIS ORCHESTRATION EXAMPLE COMPLETED ***")
        return True
        
    except Exception as e:
        print(f"ERROR in crisis orchestration example: {e}")
        return False

def create_minimal_config():
    """Create minimal configuration files for testing"""
    
    print("\n*** CREATING MINIMAL CONFIGURATION ***")
    
    # Create persona_config directory
    config_dir = "./persona_config"
    os.makedirs(config_dir, exist_ok=True)
    
    # Create testing_data directory
    testing_dir = "./testing_data"
    os.makedirs(testing_dir, exist_ok=True)
    
    print(f"Created configuration directory: {config_dir}")
    print(f"Created testing data directory: {testing_dir}")
    
    # Create a simple test data file
    test_data = {
        "harbor_freight_scenarios": [
            {"route_id": "HF001", "status": "NULL_RETURN", "error": "circular_dependency"},
            {"route_id": "HF002", "status": "NULL_RETURN", "error": "timing_calculation_failure"}
        ]
    }
    
    import json
    test_file_path = os.path.join(testing_dir, "harbor_freight_routes.json")
    with open(test_file_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2)
    
    print(f"Created test data file: {test_file_path}")
    
    return True

if __name__ == "__main__":
    print("VRO Crisis Orchestrator - Windows Compatibility Test")
    print("=" * 60)
    
    # Create minimal config
    create_minimal_config()
    
    # Run main compatibility test
    success = test_windows_compatibility()
    
    if success:
        # Run example orchestration
        test_crisis_orchestration_example()
        
        print("\n*** WINDOWS TESTING COMPLETE - SYSTEM READY ***")
        print("\nNext steps:")
        print("1. Save the vro_crisis_orchestrator.py file")
        print("2. Run: python vro_crisis_orchestrator.py")
        print("3. Test with your actual VRO crisis scenario")
        print("4. Use enhance_claude_prompt() function in your workflow")
    else:
        print("\n*** TESTING FAILED - CHECK ERRORS ABOVE ***")
        sys.exit(1)
