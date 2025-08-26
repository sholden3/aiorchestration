#!/usr/bin/env python3
"""Fix JSON parsing in database service"""

import json

# Read the current database_service.py
with open('database_service.py', 'r') as f:
    content = f.read()

# Add a helper function to parse JSONB fields
helper_function = '''
    def _parse_jsonb_fields(self, row: dict, jsonb_fields: list) -> dict:
        """Parse JSONB fields from database row"""
        result = dict(row)
        for field in jsonb_fields:
            if field in result and result[field] is not None:
                # If it's already a list/dict, keep it as is
                if isinstance(result[field], (list, dict)):
                    continue
                # If it's a string that looks like JSON, parse it
                elif isinstance(result[field], str):
                    try:
                        if result[field].startswith('[') or result[field].startswith('{'):
                            result[field] = json.loads(result[field])
                        else:
                            # It's just a plain string, leave it
                            pass
                    except json.JSONDecodeError:
                        # If parsing fails, leave as string
                        pass
        return result
'''

# Find where to insert the helper function (after __init__)
import_pos = content.find('import json')
if import_pos == -1:
    # Add json import at the top
    import_section = "import asyncpg\nfrom typing import List, Dict, Any, Optional\nimport json\nfrom datetime import datetime"
    content = content.replace("import asyncpg\nfrom typing import List, Dict, Any, Optional", import_section)

# Find the class definition and add the helper after disconnect
disconnect_end = content.find('    async def disconnect(self):\n        """Disconnect from database"""\n        if self.pool:\n            await self.pool.close()\n            self.is_connected = False')
if disconnect_end != -1:
    # Find the end of disconnect method
    next_method = content.find('\n    async def', disconnect_end + 1)
    if next_method != -1:
        content = content[:next_method] + '\n' + helper_function + content[next_method:]

# Now update the get_rules method
old_get_rules = '''                rows = await conn.fetch(query, active_only, category, severity)
                return [dict(row) for row in rows]'''

new_get_rules = '''                rows = await conn.fetch(query, active_only, category, severity)
                jsonb_fields = ['examples', 'anti_patterns']
                return [self._parse_jsonb_fields(row, jsonb_fields) for row in rows]'''

content = content.replace(old_get_rules, new_get_rules)

# Update get_best_practices method
old_get_practices = '''                rows = await conn.fetch(query, category, required_only)
                return [dict(row) for row in rows]'''

new_get_practices = '''                rows = await conn.fetch(query, category, required_only)
                jsonb_fields = ['benefits', 'anti_patterns', 'references', 'examples']
                return [self._parse_jsonb_fields(row, jsonb_fields) for row in rows]'''

content = content.replace(old_get_practices, new_get_practices)

# Update get_templates method
old_get_templates = '''                rows = await conn.fetch(query, category)
                return [dict(row) for row in rows]'''

new_get_templates = '''                rows = await conn.fetch(query, category)
                jsonb_fields = ['variables', 'tags', 'variables_detail']
                return [self._parse_jsonb_fields(row, jsonb_fields) for row in rows]'''

content = content.replace(old_get_templates, new_get_templates)

# Write the updated file
with open('database_service.py', 'w') as f:
    f.write(content)

print("Fixed JSON parsing in database_service.py")
print("Added _parse_jsonb_fields helper method")
print("Updated get_rules, get_best_practices, and get_templates methods")