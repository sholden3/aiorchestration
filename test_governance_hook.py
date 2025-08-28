"""
Test file without proper documentation headers
This should be caught by governance
"""

def insecure_function():
    password = "hardcoded_password_123"  # Security violation!
    return password

# No tests provided - should trigger warning