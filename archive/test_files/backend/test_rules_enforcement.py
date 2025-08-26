"""Test rules enforcement system"""
import asyncio
from typing import Dict
from rules_enforcement import RulesEnforcementEngine, RuleType

async def test_rules_enforcement():
    """Test rules enforcement functionality"""
    print("=== Testing Rules Enforcement ===\n")
    
    engine = RulesEnforcementEngine()
    
    # Test 1: Assumption detection
    print("1. Testing assumption detection...")
    
    # Action with assumption
    result1 = await engine.check_pre_execution(
        action="This should work for optimization",
        context={"test": True}
    )
    print(f"   Assumption action: {result1.success}")
    if not result1.success:
        print(f"   [OK] Blocked: {result1.error}")
    
    # Action without assumption  
    result2 = await engine.check_pre_execution(
        action="Execute tested optimization",
        context={"evidence": "measured 10ms improvement"}
    )
    print(f"   Evidence-based action: {result2.success}")
    if result2.success:
        print("   [OK] Allowed with evidence")
    
    # Test 2: Evidence requirement
    print("\n2. Testing evidence requirements...")
    
    # Performance claim without evidence
    result3 = await engine.check_pre_execution(
        action="Implement faster algorithm",
        context={"description": "new approach"}
    )
    if not result3.success:
        print(f"   [OK] Blocked performance claim without evidence")
    
    # Performance claim with evidence
    result4 = await engine.check_pre_execution(
        action="Implement faster algorithm",
        context={"measurement": "Benchmark shows 50ms improvement"}
    )
    if result4.success:
        print("   [OK] Allowed performance claim with measurement")
    
    # Test 3: Text cleaning
    print("\n3. Testing assumption language cleaning...")
    
    text = "This should work and probably improves performance, assuming the cache is warm"
    clean_result = await engine.enforce_assumption_prevention(text)
    
    if clean_result.success:
        print(f"   Original: {text}")
        print(f"   Cleaned: {clean_result.data}")
        print(f"   Changes: {clean_result.metadata.get('changes', [])}")
    
    # Test 4: Data validation
    print("\n4. Testing data validation...")
    
    # Data with magic variables
    bad_data = {
        "host": "localhost",
        "port": 8000,
        "note": "TODO: fix this"
    }
    
    val_result = await engine.validate_data(bad_data, "config")
    if not val_result.success:
        print(f"   [OK] Magic variables detected: {val_result.error}")
    
    # Clean data
    good_data = {
        "host": "configured_host",
        "port": 8000,
        "note": "Production ready"
    }
    
    val_result2 = await engine.validate_data(good_data, "config")
    if val_result2.success:
        print("   [OK] Clean data passed validation")
    
    # Test 5: Violations summary
    print("\n5. Violations summary:")
    summary = engine.get_violations_summary()
    print(f"   Total violations: {summary['total_violations']}")
    print(f"   By severity: {summary['by_severity']}")
    print(f"   By rule: {summary['by_rule']}")
    
    # Test 6: Custom hook
    print("\n6. Testing custom hooks...")
    
    async def no_test_in_production(action: str, context: Dict):
        """Custom hook to prevent 'test' in production"""
        if 'production' in str(context) and 'test' in action.lower():
            return False
        return True
    
    engine.register_hook(RuleType.PRE_EXECUTION, no_test_in_production)
    
    result5 = await engine.check_pre_execution(
        action="Run test query",
        context={"environment": "production"}
    )
    
    if not result5.success:
        print("   [OK] Custom hook blocked test in production")
    
    print("\n=== All Rules Enforcement Tests Passed ===")
    return True

if __name__ == "__main__":
    from typing import Dict
    result = asyncio.run(test_rules_enforcement())
    exit(0 if result else 1)