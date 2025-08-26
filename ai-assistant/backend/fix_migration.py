#!/usr/bin/env python3
"""Fix database migration by adding categories first"""

import asyncio
import asyncpg

async def fix_migration():
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='root',
            database='ai_assistant'
        )
        
        print("Connected to database")
        
        # First, create basic schema manually
        await conn.execute("""
        -- Drop existing tables if they exist
        DROP TABLE IF EXISTS rule_violations CASCADE;
        DROP TABLE IF EXISTS template_variables CASCADE;
        DROP TABLE IF EXISTS templates CASCADE;
        DROP TABLE IF EXISTS best_practices CASCADE;
        DROP TABLE IF EXISTS rules CASCADE;
        DROP TABLE IF EXISTS categories CASCADE;
        """)
        
        # Create categories table
        await conn.execute("""
        CREATE TABLE categories (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            type VARCHAR(50) NOT NULL CHECK (type IN ('rule', 'practice', 'template', 'all')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Insert default categories
        await conn.execute("""
        INSERT INTO categories (id, name, description, type) VALUES
        ('security', 'Security', 'Security best practices and rules', 'all'),
        ('performance', 'Performance', 'Performance optimization rules', 'all'),
        ('architecture', 'Architecture', 'Architectural guidelines', 'all'),
        ('testing', 'Testing', 'Testing standards and practices', 'all'),
        ('general', 'General', 'General development practices', 'all'),
        ('requirements-gathering', 'Requirements Gathering', 'Requirements and specifications', 'all');
        """)
        
        # Create rules table
        await conn.execute("""
        CREATE TABLE rules (
            rule_id VARCHAR(50) PRIMARY KEY,
            category VARCHAR(50),
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
            enforcement VARCHAR(20) NOT NULL CHECK (enforcement IN ('mandatory', 'recommended', 'optional')),
            examples JSONB DEFAULT '[]'::jsonb,
            anti_patterns JSONB DEFAULT '[]'::jsonb,
            violations_consequence TEXT,
            created_by VARCHAR(100) NOT NULL DEFAULT 'system',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT true,
            priority INTEGER DEFAULT 0 CHECK (priority >= 0)
        );
        """)
        
        # Create best_practices table
        await conn.execute("""
        CREATE TABLE best_practices (
            practice_id VARCHAR(50) PRIMARY KEY,
            category VARCHAR(50),
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            benefits JSONB DEFAULT '[]'::jsonb,
            implementation_guide TEXT,
            anti_patterns JSONB DEFAULT '[]'::jsonb,
            references JSONB DEFAULT '[]'::jsonb,
            examples JSONB DEFAULT '[]'::jsonb,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT true,
            is_required BOOLEAN DEFAULT false,
            priority VARCHAR(20)
        );
        """)
        
        # Create templates table
        await conn.execute("""
        CREATE TABLE templates (
            template_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            category VARCHAR(50),
            template_content TEXT NOT NULL,
            variables JSONB DEFAULT '[]'::jsonb,
            tags JSONB DEFAULT '[]'::jsonb,
            usage_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT true,
            created_by VARCHAR(100) DEFAULT 'system'
        );
        """)
        
        print("Schema created successfully")
        await conn.close()
        return True
    except Exception as e:
        print(f"ERROR: Failed to create schema: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(fix_migration())