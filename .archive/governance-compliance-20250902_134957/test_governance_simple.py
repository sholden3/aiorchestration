#!/usr/bin/env python3
"""
Simple governance test
Tests the governance validation system

@author Sam Martinez v3.2.0 - Testing Lead & Quality Assurance
@architecture Test script for governance validation system
@business_logic Validates governance engine functionality
"""

from governance.core.enhanced_governance_engine import MagicVariableDetector
from governance.validators.domain_validators import SecurityValidator, DatabaseValidator

def test_governance():
    """Test governance detection"""
    
    # Test magic variable detection
    print("Testing Magic Variable Detection...")
    detector = MagicVariableDetector()
    
    test_code = """
timeout = 99999
max_retries = 5000
port = 8080
"""
    
    issues = detector.detect(test_code, "test.py")
    print(f"  Found {len(issues)} magic variable issues")
    for issue in issues:
        print(f"    - Line {issue.get('line')}: {issue.get('message')}")
    
    # Test security validation
    print("\nTesting Security Validation...")
    sec_validator = SecurityValidator()
    
    dangerous_code = """
password = "admin123"
api_key = "sk-1234567890"
eval(user_input)
"""
    
    result = sec_validator.validate(dangerous_code, "test.py")
    print(f"  Found {len(result.issues)} security issues")
    for issue in result.issues[:3]:
        print(f"    - {issue.get('type', 'unknown')}: {issue.get('message', 'no message')}")
    
    # Test database validation
    print("\nTesting Database Validation...")
    db_validator = DatabaseValidator()
    
    sql_code = """
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
"""
    
    result = db_validator.validate(sql_code, "test.py")
    print(f"  Found {len(result.issues)} database issues")
    for issue in result.issues[:3]:
        print(f"    - {issue.get('type', 'unknown')}: {issue.get('message', 'no message')}")
    
    print("\nGovernance validation complete!")
    return True


if __name__ == "__main__":
    test_governance()