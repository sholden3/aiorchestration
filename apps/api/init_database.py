"""
Initialize database tables for AI Assistant
"""

import asyncio
import asyncpg
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_database():
    """Initialize all database tables"""
    
    conn = None
    try:
        # Connect to the database
        conn = await asyncpg.connect(
            'postgresql://postgres:root@localhost:5432/ai_assistant'
        )
        logger.info("Connected to ai_assistant database")
        
        # Create rules table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS rules (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(100),
                severity VARCHAR(50),
                status VARCHAR(50),
                condition TEXT,
                action TEXT,
                tags TEXT[],
                metadata JSONB,
                author VARCHAR(100),
                version INTEGER DEFAULT 1,
                enforcement_count INTEGER DEFAULT 0,
                violation_count INTEGER DEFAULT 0,
                effectiveness_score FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("✓ Rules table created/verified")
        
        # Create practices table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS practices (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(100),
                implementation_guide TEXT,
                benefits TEXT[],
                challenges TEXT[],
                examples TEXT[],
                metrics JSONB,
                tags TEXT[],
                author VARCHAR(100),
                effectiveness_score FLOAT,
                adoption_rate FLOAT,
                votes_up INTEGER DEFAULT 0,
                votes_down INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("✓ Practices table created/verified")
        
        # Create templates table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(50),
                category VARCHAR(100),
                template_content TEXT,
                description TEXT,
                example_usage JSONB,
                variables JSONB,
                validation_rules JSONB,
                tags TEXT[],
                author VARCHAR(100),
                version INTEGER DEFAULT 1,
                parent_id INTEGER,
                usage_count INTEGER DEFAULT 0,
                success_rate FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("✓ Templates table created/verified")
        
        # Create cache table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS cache_entries (
                id SERIAL PRIMARY KEY,
                key VARCHAR(255) UNIQUE NOT NULL,
                value JSONB,
                tier VARCHAR(20),
                hits INTEGER DEFAULT 0,
                misses INTEGER DEFAULT 0,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')
        logger.info("✓ Cache table created/verified")
        
        # Create audit log table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(100),
                entity_type VARCHAR(100),
                entity_id VARCHAR(100),
                user_id VARCHAR(100),
                action VARCHAR(100),
                details JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("✓ Audit log table created/verified")
        
        # Create indexes for better performance
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_rules_category ON rules(category);
            CREATE INDEX IF NOT EXISTS idx_rules_status ON rules(status);
            CREATE INDEX IF NOT EXISTS idx_practices_category ON practices(category);
            CREATE INDEX IF NOT EXISTS idx_templates_type ON templates(type);
            CREATE INDEX IF NOT EXISTS idx_cache_key ON cache_entries(key);
            CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_log(entity_type, entity_id);
        ''')
        logger.info("✓ Indexes created/verified")
        
        # Insert some sample data if tables are empty
        count = await conn.fetchval("SELECT COUNT(*) FROM rules")
        if count == 0:
            await conn.execute('''
                INSERT INTO rules (name, description, category, severity, status, condition, action)
                VALUES 
                ('Code Review Required', 'All code must be reviewed before merge', 'governance', 'HIGH', 'ACTIVE', 
                 'pull_request.created', 'require_review'),
                ('Test Coverage Minimum', 'Maintain 80% test coverage', 'quality', 'MEDIUM', 'ACTIVE',
                 'code.coverage < 80', 'block_merge'),
                ('Security Scan', 'Run security scan on dependencies', 'security', 'CRITICAL', 'ACTIVE',
                 'dependency.updated', 'run_security_scan')
            ''')
            logger.info("✓ Sample rules inserted")
        
        count = await conn.fetchval("SELECT COUNT(*) FROM practices")
        if count == 0:
            await conn.execute('''
                INSERT INTO practices (name, description, category, implementation_guide)
                VALUES 
                ('Test-Driven Development', 'Write tests before implementation', 'testing', 
                 'Write failing test, implement feature, refactor'),
                ('Code Documentation', 'Document all public APIs', 'documentation',
                 'Use JSDoc/PyDoc, include examples, document edge cases'),
                ('Continuous Integration', 'Automate build and test pipeline', 'devops',
                 'Set up CI/CD, automate tests, deploy on green builds')
            ''')
            logger.info("✓ Sample practices inserted")
        
        count = await conn.fetchval("SELECT COUNT(*) FROM templates")
        if count == 0:
            await conn.execute('''
                INSERT INTO templates (name, type, category, template_content, description, variables)
                VALUES 
                ('React Component', 'CODE', 'frontend', 
                 'import React from "react";\n\nconst {{name}} = () => {\n  return <div>{{content}}</div>;\n};\n\nexport default {{name}};',
                 'Basic React functional component', '{"name": "string", "content": "string"}'::jsonb),
                ('Python Class', 'CODE', 'backend',
                 'class {{name}}:\n    def __init__(self):\n        pass\n\n    def {{method}}(self):\n        """{{description}}"""\n        pass',
                 'Basic Python class template', '{"name": "string", "method": "string", "description": "string"}'::jsonb)
            ''')
            logger.info("✓ Sample templates inserted")
        
        logger.info("\n✅ Database initialization complete!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    success = asyncio.run(init_database())
    exit(0 if success else 1)