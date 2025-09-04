"""
@fileoverview Working API tests
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Testing - API Layer
@business_logic Validate CRUD operations work correctly
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that imports work"""
    from api import rules, practices, templates, sessions
    from database.models import Rule, Practice, Template, Session
    assert rules is not None
    assert Practice is not None

def test_database_models():
    """Test database model creation"""
    from database.models import Rule, RuleSeverity, RuleStatus
    
    rule = Rule(
        name="test",
        condition="test",
        action="test",
        severity=RuleSeverity.INFO,
        status=RuleStatus.DRAFT
    )
    
    assert rule.name == "test"
    assert rule.severity == RuleSeverity.INFO

def test_governance_validation():
    """Test governance validation works"""
    from core.governance import validate_rule_condition
    
    # Valid JSON condition
    valid, error = validate_rule_condition('{"key": "value"}')
    assert valid == True
    assert error is None
    
    # Invalid condition
    valid, error = validate_rule_condition('invalid json {')
    assert valid == False
    assert "Invalid" in error

def test_template_engine():
    """Test template rendering engine"""
    from core.template_engine import render_template, validate_template_variables
    
    # Simple rendering
    template = "Hello {{name}}!"
    variables = {"name": "World"}
    result = render_template(template, variables)
    assert result == "Hello World!"
    
    # Array iteration
    template = "{{#each items}}* {{this}}\n{{/each}}"
    variables = {"items": ["One", "Two", "Three"]}
    result = render_template(template, variables)
    assert "* One" in result
    assert "* Two" in result
    assert "* Three" in result
    
    # Variable validation
    template_vars = {
        "name": {"type": "string", "required": True},
        "age": {"type": "number", "required": False}
    }
    
    # Valid variables
    valid, errors = validate_template_variables(template_vars, {"name": "Alice", "age": 25})
    assert valid == True
    assert len(errors) == 0
    
    # Missing required
    valid, errors = validate_template_variables(template_vars, {"age": 25})
    assert valid == False
    assert "Required variable 'name' is missing" in errors[0]

def test_auth_placeholder():
    """Test auth placeholder returns system user"""
    import asyncio
    from core.auth import get_current_user
    
    async def test():
        user = await get_current_user()
        assert user["id"] == "system"
        assert user["role"] == "admin"
        assert user["phase"] == "1"
    
    asyncio.run(test())

def test_practice_effectiveness():
    """Test practice effectiveness calculation"""
    from database.models import Practice
    
    practice = Practice(
        name="Test",
        category="test",
        description="Test"
    )
    
    # No votes
    assert practice.calculate_effectiveness() == 0.5
    
    # With votes
    practice.votes_up = 7
    practice.votes_down = 3
    assert practice.calculate_effectiveness() == 0.7

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])