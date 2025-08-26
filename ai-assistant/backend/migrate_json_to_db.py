"""
Migration Script: Import JSON data to PostgreSQL
Migrates best practices and templates from JSON files to database
"""

import asyncio
import json
import asyncpg
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JSONToDBMigrator:
    """Migrate JSON files to PostgreSQL database"""
    
    def __init__(self, database_url: str = None):
        if database_url is None:
            self.database_url = "postgresql://postgres:root@localhost:5432/ai_assistant"
        else:
            self.database_url = database_url
        self.conn = None
        
    async def connect(self):
        """Connect to database"""
        try:
            self.conn = await asyncpg.connect(self.database_url)
            logger.info("Connected to database")
            
            # Test connection
            version = await self.conn.fetchval("SELECT version()")
            logger.info(f"PostgreSQL version: {version}")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            logger.info("Please ensure PostgreSQL is running and database 'ai_assistant' exists")
            logger.info("To create database: CREATE DATABASE ai_assistant;")
            raise
            
    async def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            await self.conn.close()
            
    async def initialize_schema(self):
        """Create tables if they don't exist"""
        schema_file = Path(__file__).parent / "database_schema.sql"
        
        if not schema_file.exists():
            logger.error(f"Schema file not found: {schema_file}")
            return False
            
        try:
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
                
            await self.conn.execute(schema_sql)
            logger.info("Database schema initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            return False
            
    async def migrate_best_practices(self):
        """Migrate best practices from JSON to database"""
        json_file = Path(__file__).parent.parent / "claude-code-best-practices.json"
        
        if not json_file.exists():
            # Try alternate location
            json_file = Path(__file__).parent.parent.parent / "best-practices-2025-08-12.json"
            
        if not json_file.exists():
            logger.warning(f"Best practices JSON file not found")
            return 0
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            practices = data if isinstance(data, list) else data.get('practices', [])
            
            count = 0
            for practice in practices:
                try:
                    # Check if practice already exists
                    exists = await self.conn.fetchval(
                        "SELECT 1 FROM best_practices WHERE practice_id = $1",
                        practice.get('id', f"BP-{count+1:03d}")
                    )
                    
                    if exists:
                        logger.info(f"Practice {practice.get('id')} already exists, skipping")
                        continue
                    
                    # Insert practice
                    await self.conn.execute("""
                        INSERT INTO best_practices (
                            practice_id, category, title, description,
                            benefits, implementation_guide, anti_patterns,
                            references, examples, is_active, is_required, priority
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                        ON CONFLICT (practice_id) DO NOTHING
                    """,
                        practice.get('id', f"BP-{count+1:03d}"),
                        practice.get('category', 'general'),
                        practice.get('title', 'Untitled'),
                        practice.get('description', ''),
                        json.dumps(practice.get('benefits', [])),
                        practice.get('implementation_guide', ''),
                        json.dumps(practice.get('antiPatterns', practice.get('anti_patterns', []))),
                        json.dumps(practice.get('references', [])),
                        json.dumps(practice.get('examples', [])),
                        practice.get('isActive', True),
                        practice.get('isRequired', False),
                        practice.get('priority')
                    )
                    count += 1
                    logger.info(f"Migrated best practice: {practice.get('title')}")
                    
                except Exception as e:
                    logger.error(f"Failed to migrate practice {practice.get('id')}: {e}")
                    
            logger.info(f"Migrated {count} best practices")
            return count
            
        except Exception as e:
            logger.error(f"Failed to read best practices JSON: {e}")
            return 0
            
    async def migrate_templates(self):
        """Migrate templates from JSON to database"""
        json_file = Path(__file__).parent.parent / "claude-code-templates.json"
        
        if not json_file.exists():
            # Try alternate location
            json_file = Path(__file__).parent.parent.parent / "claude-code-templates-2025-08-12.json"
            
        if not json_file.exists():
            logger.warning(f"Templates JSON file not found")
            return 0
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            templates = data if isinstance(data, list) else data.get('templates', [])
            
            count = 0
            for template in templates:
                try:
                    # Check if template already exists
                    exists = await self.conn.fetchval(
                        "SELECT 1 FROM templates WHERE template_id = $1",
                        template.get('id', f"TMPL-{count+1:03d}")
                    )
                    
                    if exists:
                        logger.info(f"Template {template.get('id')} already exists, skipping")
                        continue
                    
                    # Insert template
                    template_id = template.get('id', f"TMPL-{count+1:03d}")
                    await self.conn.execute("""
                        INSERT INTO templates (
                            template_id, name, description, category,
                            template_content, variables, tags, is_active
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        ON CONFLICT (template_id) DO NOTHING
                    """,
                        template_id,
                        template.get('name', 'Untitled Template'),
                        template.get('description', ''),
                        template.get('category', 'general'),
                        template.get('template', template.get('template_content', '')),
                        json.dumps(template.get('variables', [])),
                        json.dumps(template.get('tags', [])),
                        True
                    )
                    
                    # Insert template variables if detailed
                    if 'variables' in template and isinstance(template['variables'], list):
                        for var in template['variables']:
                            if isinstance(var, dict):
                                await self.conn.execute("""
                                    INSERT INTO template_variables (
                                        template_id, variable_name, variable_type,
                                        default_value, options, is_required, description
                                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                                    ON CONFLICT (template_id, variable_name) DO NOTHING
                                """,
                                    template_id,
                                    var.get('name', 'unnamed'),
                                    var.get('type', 'text'),
                                    var.get('default'),
                                    json.dumps(var.get('options', [])),
                                    var.get('required', False),
                                    var.get('description')
                                )
                    
                    count += 1
                    logger.info(f"Migrated template: {template.get('name')}")
                    
                except Exception as e:
                    logger.error(f"Failed to migrate template {template.get('id')}: {e}")
                    
            logger.info(f"Migrated {count} templates")
            return count
            
        except Exception as e:
            logger.error(f"Failed to read templates JSON: {e}")
            return 0
            
    async def add_sample_rules(self):
        """Add sample rules to demonstrate the system"""
        sample_rules = [
            {
                "rule_id": "SEC-001",
                "category": "security",
                "title": "Never commit secrets",
                "description": "API keys, passwords, and secrets must never be committed to version control",
                "severity": "critical",
                "enforcement": "mandatory",
                "examples": ["Use environment variables", "Use secret management services"],
                "anti_patterns": ["Hardcoding passwords", "Committing .env files"]
            },
            {
                "rule_id": "PERF-001",
                "category": "performance",
                "title": "Optimize database queries",
                "description": "Use indexes and avoid N+1 queries",
                "severity": "high",
                "enforcement": "recommended",
                "examples": ["Use select_related in Django", "Create appropriate indexes"],
                "anti_patterns": ["Queries in loops", "Missing indexes on foreign keys"]
            },
            {
                "rule_id": "TEST-001",
                "category": "testing",
                "title": "Maintain test coverage above 80%",
                "description": "All new code must have comprehensive test coverage",
                "severity": "high",
                "enforcement": "mandatory",
                "examples": ["Unit tests for all functions", "Integration tests for APIs"],
                "anti_patterns": ["Untested code", "Tests without assertions"]
            },
            {
                "rule_id": "GEN-001",
                "category": "general",
                "title": "Use meaningful variable names",
                "description": "Variables should clearly indicate their purpose",
                "severity": "medium",
                "enforcement": "recommended",
                "examples": ["user_email instead of e", "is_active instead of flag"],
                "anti_patterns": ["Single letter variables", "Ambiguous names"]
            },
            {
                "rule_id": "REQ-001",
                "category": "requirements-gathering",
                "title": "No boilerplate without requirements",
                "description": "Never generate generic placeholder code without specific requirements",
                "severity": "critical",
                "enforcement": "mandatory",
                "examples": ["Ask for clarification", "Gather specifications first"],
                "anti_patterns": ["TODO comments", "Generic CRUD without logic"]
            }
        ]
        
        count = 0
        for rule in sample_rules:
            try:
                # Check if rule already exists
                exists = await self.conn.fetchval(
                    "SELECT 1 FROM rules WHERE rule_id = $1",
                    rule['rule_id']
                )
                
                if exists:
                    logger.info(f"Rule {rule['rule_id']} already exists, skipping")
                    continue
                
                await self.conn.execute("""
                    INSERT INTO rules (
                        rule_id, category, title, description,
                        severity, enforcement, examples, anti_patterns,
                        active, created_by
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT (rule_id) DO NOTHING
                """,
                    rule['rule_id'],
                    rule['category'],
                    rule['title'],
                    rule['description'],
                    rule['severity'],
                    rule['enforcement'],
                    json.dumps(rule['examples']),
                    json.dumps(rule['anti_patterns']),
                    True,
                    'migration_script'
                )
                count += 1
                logger.info(f"Added sample rule: {rule['title']}")
                
            except Exception as e:
                logger.error(f"Failed to add rule {rule['rule_id']}: {e}")
                
        logger.info(f"Added {count} sample rules")
        return count
        
    async def run_migration(self):
        """Run the complete migration"""
        try:
            await self.connect()
            
            # Initialize schema
            logger.info("Initializing database schema...")
            success = await self.initialize_schema()
            
            if not success:
                logger.error("Failed to initialize schema, aborting migration")
                return
            
            # Migrate data
            logger.info("\n" + "="*50)
            logger.info("Starting data migration...")
            logger.info("="*50)
            
            # Add sample rules
            logger.info("\nAdding sample rules...")
            rules_count = await self.add_sample_rules()
            
            # Migrate best practices
            logger.info("\nMigrating best practices...")
            practices_count = await self.migrate_best_practices()
            
            # Migrate templates
            logger.info("\nMigrating templates...")
            templates_count = await self.migrate_templates()
            
            # Summary
            logger.info("\n" + "="*50)
            logger.info("MIGRATION SUMMARY")
            logger.info("="*50)
            logger.info(f"✓ Rules added: {rules_count}")
            logger.info(f"✓ Best practices migrated: {practices_count}")
            logger.info(f"✓ Templates migrated: {templates_count}")
            logger.info("\nMigration completed successfully!")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            
        finally:
            await self.disconnect()

async def main():
    """Main entry point"""
    migrator = JSONToDBMigrator()
    await migrator.run_migration()

if __name__ == "__main__":
    asyncio.run(main())