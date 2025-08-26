#!/usr/bin/env python3
"""Fix JSONB data that was stored as strings"""

import asyncio
import asyncpg
import json

async def fix_jsonb_data():
    conn = await asyncpg.connect('postgresql://postgres:root@localhost:5432/ai_assistant')
    
    print("=== FIXING JSONB DATA ===")
    
    # Fix best_practices JSONB columns
    print("\nFixing best_practices table...")
    
    # Since the data is already strings but needs to be proper JSONB,
    # we can use PostgreSQL's casting to fix it
    try:
        result = await conn.execute("""
            UPDATE best_practices 
            SET 
                benefits = benefits::jsonb,
                anti_patterns = anti_patterns::jsonb,
                "references" = "references"::jsonb,
                examples = examples::jsonb
            WHERE 
                benefits IS NOT NULL 
                AND anti_patterns IS NOT NULL
        """)
        print(f"Fixed best_practices: {result}")
    except Exception as e:
        print(f"Error fixing best_practices: {e}")
        # Try alternative approach - the data might already be JSONB but stored as text
        # Let's check the actual data type
    
    # Check what we're dealing with
    row = await conn.fetchrow("""
        SELECT 
            pg_typeof(benefits) as benefits_type,
            pg_typeof(anti_patterns) as anti_patterns_type,
            pg_typeof("references") as references_type,
            pg_typeof(examples) as examples_type
        FROM best_practices 
        LIMIT 1
    """)
    
    print("\nCurrent column types:")
    for key, value in row.items():
        print(f"  {key}: {value}")
    
    # Fix templates JSONB columns
    print("\nFixing templates table...")
    try:
        result = await conn.execute("""
            UPDATE templates 
            SET 
                variables = variables::jsonb,
                tags = tags::jsonb
            WHERE 
                variables IS NOT NULL 
                AND tags IS NOT NULL
        """)
        print(f"Fixed templates: {result}")
    except Exception as e:
        print(f"Error fixing templates: {e}")
    
    # Verify the fix by checking a sample
    print("\n=== VERIFYING FIX ===")
    row = await conn.fetchrow("""
        SELECT 
            practice_id,
            benefits,
            pg_typeof(benefits) as benefits_type
        FROM best_practices 
        WHERE practice_id = 'BP-013'
    """)
    
    if row:
        print(f"Practice: {row['practice_id']}")
        print(f"Benefits type in DB: {row['benefits_type']}")
        print(f"Benefits type in Python: {type(row['benefits'])}")
        if isinstance(row['benefits'], list):
            print(f"SUCCESS: Data is now proper JSONB list with {len(row['benefits'])} items")
            print(f"Sample value: {row['benefits']}")
        elif isinstance(row['benefits'], str):
            print(f"Still a string, trying to parse...")
            try:
                parsed = json.loads(row['benefits'])
                print(f"Can parse to {type(parsed)} with {len(parsed)} items: {parsed}")
            except:
                print("Cannot parse as JSON")
        else:
            print(f"Unexpected type: {type(row['benefits'])}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_jsonb_data())