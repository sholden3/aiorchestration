"""
@fileoverview Template rendering engine
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Backend - Core Layer
@business_logic Template variable substitution and validation
"""

import re
import json
from typing import Dict, Any, List, Tuple, Optional

def render_template(template_content: str, variables: Dict[str, Any]) -> str:
    """
    Render a template with variable substitution
    Phase 1: Simple variable replacement
    Phase 3: Will add Jinja2 or Handlebars support
    """
    rendered = template_content
    
    # Simple {{variable}} replacement
    for key, value in variables.items():
        # Handle different value types
        if isinstance(value, (list, dict)):
            value_str = json.dumps(value, indent=2)
        else:
            value_str = str(value)
        
        # Replace {{variable}} patterns
        pattern = r'\{\{' + re.escape(key) + r'\}\}'
        rendered = re.sub(pattern, value_str, rendered)
    
    # Handle array iterations (simplified for Phase 1)
    # {{#each items}}...{{/each}}
    each_pattern = r'\{\{#each\s+(\w+)\}\}(.*?)\{\{/each\}\}'
    
    def replace_each(match):
        var_name = match.group(1)
        content = match.group(2)
        
        if var_name in variables and isinstance(variables[var_name], list):
            result = []
            for item in variables[var_name]:
                item_content = content
                if isinstance(item, dict):
                    for k, v in item.items():
                        item_content = item_content.replace(f'{{{{this.{k}}}}}', str(v))
                else:
                    item_content = item_content.replace('{{this}}', str(item))
                result.append(item_content)
            return '\n'.join(result)
        return match.group(0)
    
    rendered = re.sub(each_pattern, replace_each, rendered, flags=re.DOTALL)
    
    return rendered

def validate_template_variables(
    template_variables: Dict[str, Any],
    provided_variables: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Validate that provided variables match template requirements
    """
    errors = []
    
    if not template_variables:
        return True, []
    
    for var_name, var_config in template_variables.items():
        if not isinstance(var_config, dict):
            continue
            
        # Check required variables
        if var_config.get('required', False) and var_name not in provided_variables:
            errors.append(f"Required variable '{var_name}' is missing")
            continue
        
        # Skip validation if variable not provided and not required
        if var_name not in provided_variables:
            continue
        
        value = provided_variables[var_name]
        
        # Type validation
        expected_type = var_config.get('type')
        if expected_type:
            if expected_type == 'string' and not isinstance(value, str):
                errors.append(f"Variable '{var_name}' must be a string")
            elif expected_type == 'number' and not isinstance(value, (int, float)):
                errors.append(f"Variable '{var_name}' must be a number")
            elif expected_type == 'boolean' and not isinstance(value, bool):
                errors.append(f"Variable '{var_name}' must be a boolean")
            elif expected_type == 'array' and not isinstance(value, list):
                errors.append(f"Variable '{var_name}' must be an array")
            elif expected_type == 'object' and not isinstance(value, dict):
                errors.append(f"Variable '{var_name}' must be an object")
    
    return len(errors) == 0, errors

def extract_template_variables(template_content: str) -> List[str]:
    """
    Extract all variable names from a template
    """
    variables = set()
    
    # Find {{variable}} patterns
    simple_pattern = r'\{\{([^}#/]+)\}\}'
    for match in re.finditer(simple_pattern, template_content):
        var_name = match.group(1).strip()
        # Clean up variable name (remove 'this.' prefix)
        if var_name.startswith('this.'):
            var_name = var_name[5:]
        variables.add(var_name)
    
    # Find {{#each variable}} patterns
    each_pattern = r'\{\{#each\s+(\w+)\}\}'
    for match in re.finditer(each_pattern, template_content):
        variables.add(match.group(1))
    
    return list(variables)