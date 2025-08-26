#!/usr/bin/env python3
"""Fix all database schema issues"""

import asyncio
import asyncpg

async def fix_schema():
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='root',
            database='ai_assistant'
        )
        
        print("Connected to database\n")
        print("=== FIXING SCHEMA ISSUES ===\n")
        
        # 1. Add missing priority column to best_practices
        print("1. Adding priority column to best_practices...")
        try:
            await conn.execute("""
                ALTER TABLE best_practices 
                ADD COLUMN priority VARCHAR(20)
            """)
            print("   [OK] Added priority column")
        except Exception as e:
            if "already exists" in str(e):
                print("   - Priority column already exists")
            else:
                print(f"   [X] Error: {e}")
        
        # 2. Add missing columns that API expects
        print("\n2. Adding missing columns to tables...")
        
        # Add anti_patterns to best_practices
        try:
            await conn.execute("""
                ALTER TABLE best_practices 
                ADD COLUMN anti_patterns TEXT
            """)
            print("   [OK] Added anti_patterns to best_practices")
        except Exception as e:
            if "already exists" in str(e):
                print("   - anti_patterns already exists")
            else:
                print(f"   [X] Error: {e}")
        
        # Add references to best_practices
        try:
            await conn.execute("""
                ALTER TABLE best_practices 
                ADD COLUMN references TEXT
            """)
            print("   [OK] Added references to best_practices")
        except Exception as e:
            if "already exists" in str(e):
                print("   - references already exists")
            else:
                print(f"   [X] Error: {e}")
        
        # Add examples to best_practices
        try:
            await conn.execute("""
                ALTER TABLE best_practices 
                ADD COLUMN examples TEXT
            """)
            print("   [OK] Added examples to best_practices")
        except Exception as e:
            if "already exists" in str(e):
                print("   - examples already exists")
            else:
                print(f"   [X] Error: {e}")
        
        # Add updated_at columns
        try:
            await conn.execute("""
                ALTER TABLE best_practices 
                ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            print("   [OK] Added updated_at to best_practices")
        except Exception as e:
            if "already exists" in str(e):
                print("   - updated_at already exists in best_practices")
        
        # Add tags to templates
        try:
            await conn.execute("""
                ALTER TABLE templates 
                ADD COLUMN tags TEXT
            """)
            print("   [OK] Added tags to templates")
        except Exception as e:
            if "already exists" in str(e):
                print("   - tags already exists")
        
        # Add usage_count to templates
        try:
            await conn.execute("""
                ALTER TABLE templates 
                ADD COLUMN usage_count INTEGER DEFAULT 0
            """)
            print("   [OK] Added usage_count to templates")
        except Exception as e:
            if "already exists" in str(e):
                print("   - usage_count already exists")
        
        # Add updated_at to templates
        try:
            await conn.execute("""
                ALTER TABLE templates 
                ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            print("   [OK] Added updated_at to templates")
        except Exception as e:
            if "already exists" in str(e):
                print("   - updated_at already exists")
        
        # Add created_by to templates
        try:
            await conn.execute("""
                ALTER TABLE templates 
                ADD COLUMN created_by VARCHAR(100) DEFAULT 'system'
            """)
            print("   [OK] Added created_by to templates")
        except Exception as e:
            if "already exists" in str(e):
                print("   - created_by already exists")
        
        # 3. Create template_variables table
        print("\n3. Creating template_variables table...")
        try:
            await conn.execute("""
                CREATE TABLE template_variables (
                    id SERIAL PRIMARY KEY,
                    template_id VARCHAR(50) REFERENCES templates(template_id) ON DELETE CASCADE,
                    variable_name VARCHAR(100) NOT NULL,
                    variable_type VARCHAR(50) DEFAULT 'text',
                    default_value TEXT,
                    options TEXT,
                    is_required BOOLEAN DEFAULT false,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(template_id, variable_name)
                )
            """)
            print("   [OK] Created template_variables table")
        except Exception as e:
            if "already exists" in str(e):
                print("   - template_variables table already exists")
            else:
                print(f"   [X] Error: {e}")
        
        # 4. Convert TEXT columns to JSONB for proper JSON handling
        print("\n4. Converting TEXT columns to JSONB...")
        
        # Note: PostgreSQL doesn't allow direct conversion from TEXT to JSONB
        # We need to create new columns, copy data, drop old, rename new
        
        json_conversions = [
            ('rules', 'examples'),
            ('rules', 'anti_patterns'),
            ('best_practices', 'benefits'),
            ('best_practices', 'anti_patterns'),
            ('best_practices', 'references'),
            ('best_practices', 'examples'),
            ('templates', 'variables'),
            ('templates', 'tags')
        ]
        
        for table, column in json_conversions:
            try:
                # Check if column exists and is TEXT
                col_type = await conn.fetchval("""
                    SELECT data_type 
                    FROM information_schema.columns 
                    WHERE table_name = $1 AND column_name = $2
                """, table, column)
                
                if col_type == 'text':
                    print(f"   Converting {table}.{column} from TEXT to JSONB...")
                    
                    # Add temporary JSONB column
                    await conn.execute(f"""
                        ALTER TABLE {table} 
                        ADD COLUMN {column}_jsonb JSONB
                    """)
                    
                    # Copy and convert data
                    await conn.execute(f"""
                        UPDATE {table} 
                        SET {column}_jsonb = 
                            CASE 
                                WHEN {column} IS NULL OR {column} = '' THEN '[]'::jsonb
                                WHEN {column}::text LIKE '[%' OR {column}::text LIKE '{{%' THEN {column}::jsonb
                                ELSE to_jsonb({column}::text)
                            END
                    """)
                    
                    # Drop old column
                    await conn.execute(f"""
                        ALTER TABLE {table} DROP COLUMN {column}
                    """)
                    
                    # Rename new column
                    await conn.execute(f"""
                        ALTER TABLE {table} 
                        RENAME COLUMN {column}_jsonb TO {column}
                    """)
                    
                    print(f"     [OK] Converted {table}.{column}")
                elif col_type == 'jsonb':
                    print(f"     - {table}.{column} already JSONB")
                elif col_type is None:
                    print(f"     - {table}.{column} doesn't exist")
                    
            except Exception as e:
                print(f"     [X] Error converting {table}.{column}: {e}")
        
        # 5. Add missing indexes for performance
        print("\n5. Adding indexes...")
        
        indexes = [
            ('idx_rules_category', 'rules', 'category'),
            ('idx_rules_severity', 'rules', 'severity'),
            ('idx_best_practices_category', 'best_practices', 'category'),
            ('idx_templates_category', 'templates', 'category')
        ]
        
        for idx_name, table, column in indexes:
            try:
                await conn.execute(f"""
                    CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})
                """)
                print(f"   [OK] Created index {idx_name}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"   - Index {idx_name} already exists")
                else:
                    print(f"   [X] Error creating {idx_name}: {e}")
        
        print("\n=== SCHEMA FIXES COMPLETE ===")
        
        # Verify the fixes
        print("\n=== VERIFICATION ===")
        
        # Check if priority column exists now
        priority_exists = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'best_practices' AND column_name = 'priority'
        """)
        print(f"[OK] best_practices.priority exists: {priority_exists > 0}")
        
        # Check if template_variables exists
        template_vars_exists = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name = 'template_variables'
        """)
        print(f"[OK] template_variables table exists: {template_vars_exists > 0}")
        
        # Check JSON columns are JSONB
        json_cols = await conn.fetch("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE column_name IN ('examples', 'anti_patterns', 'benefits', 'references', 'variables', 'tags')
            AND table_schema = 'public'
            ORDER BY table_name, column_name
        """)
        
        print("\n[OK] JSON columns data types:")
        for col in json_cols:
            is_jsonb = "[OK]" if col['data_type'] == 'jsonb' else "[X]"
            print(f"  {is_jsonb} {col['table_name']}.{col['column_name']}: {col['data_type']}")
        
        await conn.close()
        print("\nSchema fixes complete!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_schema())