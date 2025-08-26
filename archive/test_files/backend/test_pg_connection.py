#!/usr/bin/env python3
"""Test PostgreSQL connection with new credentials"""

import asyncio
import asyncpg

async def test_connection():
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='root',
            database='postgres'
        )
        version = await conn.fetchval('SELECT version()')
        print("SUCCESS: Connected successfully!")
        print(f"PostgreSQL version: {version}")
        await conn.close()
        return True
    except Exception as e:
        print(f"ERROR: Connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())