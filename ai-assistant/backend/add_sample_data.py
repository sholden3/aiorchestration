#!/usr/bin/env python3
"""Add sample data to database"""

import asyncio
import asyncpg
import json

async def add_sample_data():
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='root',
            database='ai_assistant'
        )
        
        print("Connected to database")
        
        # Add sample rules
        print("Adding sample rules...")
        rules = [
            ('SEC-001', 'security', 'Never commit secrets', 
             'API keys, passwords, and secrets must never be committed to version control',
             'critical', 'mandatory', 
             json.dumps(['Use environment variables', 'Use secret management services']),
             json.dumps(['Hardcoding passwords', 'Committing .env files'])),
            ('PERF-001', 'performance', 'Optimize database queries',
             'Use indexes and avoid N+1 queries', 'high', 'recommended',
             json.dumps(['Use select_related in Django', 'Create appropriate indexes']),
             json.dumps(['Queries in loops', 'Missing indexes on foreign keys'])),
            ('TEST-001', 'testing', 'Maintain test coverage above 80%',
             'All new code must have comprehensive test coverage', 'high', 'mandatory',
             json.dumps(['Unit tests for all functions', 'Integration tests for APIs']),
             json.dumps(['Untested code', 'Tests without assertions']))
        ]
        
        for rule in rules:
            await conn.execute("""
                INSERT INTO rules (rule_id, category, title, description, severity, enforcement, examples, anti_patterns)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, *rule)
        
        # Add sample best practices
        print("Adding sample best practices...")
        practices = [
            ('BP-001', 'general', 'Use meaningful variable names',
             'Variables should clearly indicate their purpose',
             json.dumps(['Improved readability', 'Easier maintenance']),
             'Choose descriptive names that explain the purpose and context of the variable'),
            ('BP-002', 'security', 'Validate all user input',
             'Never trust user input without proper validation and sanitization',
             json.dumps(['Prevent injection attacks', 'Data integrity', 'Security compliance']),
             'Use input validation libraries and sanitization functions for all external data')
        ]
        
        for practice in practices:
            await conn.execute("""
                INSERT INTO best_practices (practice_id, category, title, description, benefits, implementation_guide)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, *practice)
        
        # Add sample templates
        print("Adding sample templates...")
        templates = [
            ('TMPL-001', 'FastAPI Endpoint Template', 
             'Basic FastAPI endpoint with error handling and validation',
             'general', 
             '''@app.{{METHOD}}("/{{ENDPOINT}}")
async def {{FUNCTION_NAME}}({{PARAMS}}):
    """{{DESCRIPTION}}"""
    try:
        # Implementation here
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))''',
             json.dumps(['METHOD', 'ENDPOINT', 'FUNCTION_NAME', 'PARAMS', 'DESCRIPTION'])),
            ('TMPL-002', 'Database Model Template',
             'SQLAlchemy model template with common fields',
             'architecture',
             '''class {{MODEL_NAME}}(Base):
    __tablename__ = "{{TABLE_NAME}}"
    
    id = Column(Integer, primary_key=True, index=True)
    {{FIELDS}}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)''',
             json.dumps(['MODEL_NAME', 'TABLE_NAME', 'FIELDS']))
        ]
        
        for template in templates:
            await conn.execute("""
                INSERT INTO templates (template_id, name, description, category, template_content, variables)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, *template)
        
        print("Sample data added successfully!")
        await conn.close()
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(add_sample_data())