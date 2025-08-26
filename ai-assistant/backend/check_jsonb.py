#!/usr/bin/env python3
"""Check JSONB data in database"""

import asyncio
import asyncpg
import json

async def check():
    conn = await asyncpg.connect('postgresql://postgres:root@localhost:5432/ai_assistant')
    
    # Check data type
    row = await conn.fetchrow(
        'SELECT benefits, anti_patterns FROM best_practices WHERE practice_id = $1', 
        'BP-013'
    )
    
    print(f"benefits type: {type(row['benefits'])}")
    print(f"benefits value: {row['benefits'][:100] if row['benefits'] else 'None'}...")
    
    # Check if it's JSON string or actual list
    if isinstance(row['benefits'], str):
        print("Data is stored as string, needs proper JSONB conversion")
        try:
            parsed = json.loads(row['benefits'])
            print(f"Can parse to: {type(parsed)} with {len(parsed)} items")
        except:
            print("Cannot parse as JSON")
    else:
        print(f"Data is stored as: {type(row['benefits'])}")
    
    await conn.close()

asyncio.run(check())