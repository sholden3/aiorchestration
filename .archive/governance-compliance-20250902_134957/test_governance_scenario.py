#!/usr/bin/env python3
"""
Test file with intentional governance violations
This file is used to test the governance system

@author Sam Martinez v3.2.0 - Testing Lead & Quality Assurance
@architecture Test scenario file for governance validation testing
@business_logic Contains intentional violations to verify governance detection
"""

# VIOLATION: Magic number without context
timeout = 99999

# VIOLATION: Hardcoded password
password = "admin123"

# VIOLATION: SQL injection vulnerability
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)

# VIOLATION: Dangerous eval usage
def execute_code(code_string):
    eval(code_string)

# VIOLATION: No error handling
def risky_operation():
    data = open('file.txt').read()
    process(data)

# VIOLATION: Performance issue - N+1 query
def get_all_users_with_posts():
    users = db.query("SELECT * FROM users")
    for user in users:
        user.posts = db.query(f"SELECT * FROM posts WHERE user_id = {user.id}")
    return users

# VIOLATION: No TTL on cache
def cache_data(key, value):
    cache.set(key, value)  # Missing TTL

# VIOLATION: XSS vulnerability
def render_html(user_input):
    return f"<div>{user_input}</div>"  # Unescaped user input

print("This test file has multiple governance violations!")