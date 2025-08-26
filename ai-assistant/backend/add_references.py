#!/usr/bin/env python3
"""Add references column"""

import asyncio
import asyncpg

async def add_references():
    conn = await asyncpg.connect('postgresql://postgres:root@localhost:5432/ai_assistant')
    try:
        await conn.execute("""
            ALTER TABLE best_practices 
            ADD COLUMN "references" JSONB DEFAULT '[]'
        """)
        print("Added references column")
    except Exception as e:
        if "already exists" in str(e):
            print("References column already exists")
        else:
            print(f"Error: {e}")
    await conn.close()

asyncio.run(add_references())