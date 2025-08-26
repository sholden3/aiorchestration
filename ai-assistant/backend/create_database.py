#!/usr/bin/env python3
"""Create ai_assistant database"""

import asyncio
import asyncpg

async def create_database():
    try:
        # Connect to default postgres database first
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='root',
            database='postgres'
        )
        
        # Check if ai_assistant database exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = 'ai_assistant'"
        )
        
        if exists:
            print("Database 'ai_assistant' already exists")
        else:
            # Create the database
            await conn.execute("CREATE DATABASE ai_assistant")
            print("Database 'ai_assistant' created successfully")
        
        await conn.close()
        return True
    except Exception as e:
        print(f"ERROR: Failed to create database: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(create_database())