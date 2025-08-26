#!/usr/bin/env python3
"""Create database schema step by step"""

import asyncio
import asyncpg

async def create_schema():
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='root',
            database='ai_assistant'
        )
        
        print("Connected to database")
        
        # Drop tables
        print("Dropping existing tables...")
        await conn.execute("DROP TABLE IF EXISTS rules CASCADE")
        await conn.execute("DROP TABLE IF EXISTS best_practices CASCADE")
        await conn.execute("DROP TABLE IF EXISTS templates CASCADE")
        await conn.execute("DROP TABLE IF EXISTS categories CASCADE")
        
        # Create categories table
        print("Creating categories table...")
        await conn.execute("""
        CREATE TABLE categories (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Insert categories
        print("Inserting categories...")
        await conn.execute("""
        INSERT INTO categories (id, name, description) VALUES
        ('security', 'Security', 'Security best practices and rules'),
        ('performance', 'Performance', 'Performance optimization rules'),
        ('architecture', 'Architecture', 'Architectural guidelines'),
        ('testing', 'Testing', 'Testing standards and practices'),
        ('general', 'General', 'General development practices')
        """)
        
        # Create rules table
        print("Creating rules table...")
        await conn.execute("""
        CREATE TABLE rules (
            rule_id VARCHAR(50) PRIMARY KEY,
            category VARCHAR(50),
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            severity VARCHAR(20) NOT NULL,
            enforcement VARCHAR(20) NOT NULL,
            examples TEXT,
            anti_patterns TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT true
        )
        """)
        
        # Create best_practices table
        print("Creating best_practices table...")
        await conn.execute("""
        CREATE TABLE best_practices (
            practice_id VARCHAR(50) PRIMARY KEY,
            category VARCHAR(50),
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            benefits TEXT,
            implementation_guide TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT true,
            is_required BOOLEAN DEFAULT false
        )
        """)
        
        # Create templates table
        print("Creating templates table...")
        await conn.execute("""
        CREATE TABLE templates (
            template_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            category VARCHAR(50),
            template_content TEXT NOT NULL,
            variables TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT true
        )
        """)
        
        print("Schema created successfully!")
        await conn.close()
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(create_schema())