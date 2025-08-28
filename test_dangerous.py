# Test file with dangerous patterns
# This should trigger governance warnings

def delete_all_data():
    """DANGER: This will delete everything"""
    password = "hardcoded123"  # BAD: hardcoded password
    api_key = "sk-1234567890abcdef"  # BAD: exposed API key
    
    # TODO_HACK: This is a temporary workaround
    # FIXME_LATER: Will fix this properly later
    
    # Quick fix to bypass validation
    disable_validation = True
    
    return "Data deleted"