#!/usr/bin/env python3
"""Check current database schema"""

import asyncio
import asyncpg

async def check_schema():
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='root',
            database='ai_assistant'
        )
        
        print("Connected to database\n")
        
        # Get all tables
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        print("=== EXISTING TABLES ===")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # Check each table's columns
        for table in tables:
            table_name = table['table_name']
            print(f"\n=== TABLE: {table_name} ===")
            
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = $1
                ORDER BY ordinal_position;
            """, table_name)
            
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                print(f"  {col['column_name']}: {col['data_type']} {nullable}{default}")
        
        # Check for specific issues
        print("\n=== CHECKING KNOWN ISSUES ===")
        
        # Check if priority column exists in best_practices
        priority_exists = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'best_practices' AND column_name = 'priority'
        """)
        print(f"1. best_practices.priority column exists: {priority_exists > 0}")
        
        # Check if template_variables table exists
        template_vars_exists = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name = 'template_variables'
        """)
        print(f"2. template_variables table exists: {template_vars_exists > 0}")
        
        # Check data types for JSON columns
        json_columns = await conn.fetch("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public' 
            AND column_name IN ('examples', 'anti_patterns', 'benefits', 'references', 'variables', 'tags')
            ORDER BY table_name, column_name;
        """)
        
        print("\n3. JSON column data types:")
        for col in json_columns:
            print(f"   {col['table_name']}.{col['column_name']}: {col['data_type']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_schema())