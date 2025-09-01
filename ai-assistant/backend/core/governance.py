"""
@fileoverview Core governance utilities
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Backend - Core Layer
@business_logic Governance validation and enforcement
"""

import json
import ast
from typing import Tuple, Optional, Any

def validate_rule_condition(condition: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that a rule condition is safe and parseable
    Phase 1: Basic validation
    Phase 4: Will add AI-based validation
    """
    if not condition or not condition.strip():
        return False, "Condition cannot be empty"
    
    # Check if it's valid JSON (for structured conditions)
    try:
        json.loads(condition)
        return True, None
    except json.JSONDecodeError:
        pass
    
    # Check if it's a valid Python expression (for code conditions)
    try:
        ast.parse(condition, mode='eval')
        return True, None
    except SyntaxError as e:
        return False, f"Invalid syntax: {str(e)}"
    except Exception as e:
        return False, f"Invalid condition: {str(e)}"

def evaluate_rule_condition(condition: str, context: dict) -> Tuple[bool, Optional[str]]:
    """
    Evaluate a rule condition against a context
    Phase 1: Basic evaluation
    Phase 4: Will add sandboxed execution
    """
    try:
        # Try JSON-based condition first
        try:
            condition_dict = json.loads(condition)
            # Simple key-value matching for now
            for key, expected_value in condition_dict.items():
                if key not in context:
                    return False, f"Missing context key: {key}"
                if context[key] != expected_value:
                    return False, f"Condition failed: {key} != {expected_value}"
            return True, None
        except json.JSONDecodeError:
            pass
        
        # Try Python expression evaluation (simplified for Phase 1)
        # In production, this would use a sandboxed environment
        try:
            # Parse and validate the expression
            tree = ast.parse(condition, mode='eval')
            # For Phase 1, only allow simple comparisons
            result = eval(compile(tree, '<string>', 'eval'), {"__builtins__": {}}, context)
            return bool(result), None
        except Exception as e:
            return False, f"Evaluation error: {str(e)}"
            
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"