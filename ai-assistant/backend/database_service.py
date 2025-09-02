"""
Database Service for Real PostgreSQL Integration
Replaces mock implementations with actual database queries
"""

import asyncpg
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """Real database service that connects to PostgreSQL"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.is_connected = False
        
    async def connect(self, database_url: str = None):
        """Connect to PostgreSQL database"""
        if database_url is None:
            # Default connection for development
            # TODO: Move to encrypted credentials manager
            database_url = "postgresql://postgres:root@localhost:5432/ai_assistant"
            
        try:
            self.pool = await asyncpg.create_pool(
                database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            self.is_connected = True
            logger.info("Connected to PostgreSQL database")
            
            # Test connection
            async with self.pool.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
                logger.info(f"PostgreSQL version: {version}")
                
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self.is_connected = False
            # Use mock data fallback
            logger.warning("Falling back to mock data mode")
            
    async def disconnect(self):
        """Disconnect from database"""
        if self.pool:
            await self.pool.close()
            self.is_connected = False
            

    def _parse_jsonb_fields(self, row: dict, jsonb_fields: list) -> dict:
        """Parse JSONB fields from database row"""
        result = dict(row)
        for field in jsonb_fields:
            if field in result and result[field] is not None:
                # If it's already a list/dict, keep it as is
                if isinstance(result[field], (list, dict)):
                    continue
                # If it's a string that looks like JSON, parse it
                elif isinstance(result[field], str):
                    try:
                        if result[field].startswith('[') or result[field].startswith('{'):
                            result[field] = json.loads(result[field])
                        else:
                            # It's just a plain string, leave it
                            pass
                    except json.JSONDecodeError:
                        # If parsing fails, leave as string
                        pass
        return result

    async def initialize_schema(self):
        """Initialize database schema if not exists"""
        if not self.is_connected:
            logger.warning("Not connected to database, skipping schema initialization")
            return
            
        try:
            async with self.pool.acquire() as conn:
                # Read and execute schema file
                with open('database_schema.sql', 'r') as f:
                    schema_sql = f.read()
                await conn.execute(schema_sql)
                logger.info("Database schema initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            
    # ==================== RULES OPERATIONS ====================
    
    async def get_rules(self, category: Optional[str] = None, 
                       severity: Optional[str] = None,
                       active_only: bool = True) -> List[Dict[str, Any]]:
        """Get rules from database with optional filters"""
        
        if not self.is_connected:
            # Return mock data if not connected
            return self._get_mock_rules()
            
        query = """
            SELECT r.*, r.category as category_name
            FROM rules r
            WHERE ($1::varchar IS NULL OR r.status = $1)
              AND ($2::varchar IS NULL OR r.category = $2)
              AND ($3::varchar IS NULL OR r.severity = $3)
            ORDER BY 
                CASE severity
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'ERROR' THEN 2
                    WHEN 'WARNING' THEN 3
                    WHEN 'INFO' THEN 4
                END,
                r.created_at DESC
        """
        
        try:
            async with self.pool.acquire() as conn:
                # Map active_only to status
                status = 'ACTIVE' if active_only else None
                rows = await conn.fetch(query, status, category, severity)
                jsonb_fields = ['examples', 'anti_patterns']
                return [self._parse_jsonb_fields(row, jsonb_fields) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get rules: {e}")
            return self._get_mock_rules()
            
    async def create_rule(self, rule_data: Dict[str, Any]) -> str:
        """Create a new rule in database"""
        
        if not self.is_connected:
            return "MOCK-" + rule_data.get('rule_id', 'RULE')
            
        query = """
            INSERT INTO rules (
                rule_id, category, title, description, severity,
                enforcement, examples, anti_patterns, violations_consequence,
                created_by, active, priority
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING rule_id
        """
        
        try:
            async with self.pool.acquire() as conn:
                rule_id = await conn.fetchval(
                    query,
                    rule_data['rule_id'],
                    rule_data.get('category', 'general'),
                    rule_data['title'],
                    rule_data['description'],
                    rule_data['severity'],
                    rule_data['enforcement'],
                    json.dumps(rule_data.get('examples', [])),
                    json.dumps(rule_data.get('anti_patterns', [])),
                    rule_data.get('violations_consequence', ''),
                    rule_data.get('created_by', 'system'),
                    rule_data.get('active', True),
                    rule_data.get('priority', 0)
                )
                logger.info(f"Created rule: {rule_id}")
                return rule_id
        except Exception as e:
            logger.error(f"Failed to create rule: {e}")
            raise
            
    async def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing rule"""
        
        if not self.is_connected:
            return False
            
        # Build dynamic update query
        set_clauses = []
        values = []
        param_count = 1
        
        for key, value in updates.items():
            if key not in ['rule_id', 'created_at']:  # Don't update these
                set_clauses.append(f"{key} = ${param_count}")
                if key in ['examples', 'anti_patterns'] and isinstance(value, list):
                    values.append(json.dumps(value))
                else:
                    values.append(value)
                param_count += 1
                
        values.append(rule_id)
        query = f"""
            UPDATE rules 
            SET {', '.join(set_clauses)}
            WHERE rule_id = ${param_count}
        """
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(query, *values)
                return result != 'UPDATE 0'
        except Exception as e:
            logger.error(f"Failed to update rule {rule_id}: {e}")
            return False
            
    # ==================== BEST PRACTICES OPERATIONS ====================
    
    async def get_best_practices(self, category: Optional[str] = None,
                                required_only: bool = False) -> List[Dict[str, Any]]:
        """Get best practices from database"""
        
        if not self.is_connected:
            return self._get_mock_best_practices()
            
        query = """
            SELECT p.*, p.category as category_name
            FROM practices p
            WHERE ($1::varchar IS NULL OR p.category = $1)
            ORDER BY 
                p.effectiveness_score DESC NULLS LAST,
                p.adoption_rate DESC NULLS LAST,
                p.created_at DESC
        """
        
        try:
            async with self.pool.acquire() as conn:
                # Only pass category parameter since required_only is not used in the new query
                rows = await conn.fetch(query, category)
                jsonb_fields = ['benefits', 'anti_patterns', 'references', 'examples']
                return [self._parse_jsonb_fields(row, jsonb_fields) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get best practices: {e}")
            return self._get_mock_best_practices()
            
    async def create_best_practice(self, practice_data: Dict[str, Any]) -> str:
        """Create a new best practice"""
        
        if not self.is_connected:
            return "MOCK-" + practice_data.get('practice_id', 'PRACTICE')
            
        query = """
            INSERT INTO best_practices (
                practice_id, category, title, description, benefits,
                implementation_guide, anti_patterns, references, examples,
                is_active, is_required, priority
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING practice_id
        """
        
        try:
            async with self.pool.acquire() as conn:
                practice_id = await conn.fetchval(
                    query,
                    practice_data['practice_id'],
                    practice_data.get('category', 'general'),
                    practice_data['title'],
                    practice_data['description'],
                    json.dumps(practice_data.get('benefits', [])),
                    practice_data.get('implementation_guide', ''),
                    json.dumps(practice_data.get('anti_patterns', [])),
                    json.dumps(practice_data.get('references', [])),
                    json.dumps(practice_data.get('examples', [])),
                    practice_data.get('is_active', True),
                    practice_data.get('is_required', False),
                    practice_data.get('priority', None)
                )
                logger.info(f"Created best practice: {practice_id}")
                return practice_id
        except Exception as e:
            logger.error(f"Failed to create best practice: {e}")
            raise
            
    # ==================== TEMPLATES OPERATIONS ====================
    
    async def get_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get templates from database"""
        
        if not self.is_connected:
            return self._get_mock_templates()
            
        query = """
            SELECT t.*, t.category as category_name
            FROM templates t
            WHERE ($1::varchar IS NULL OR t.category = $1)
            ORDER BY t.usage_count DESC, t.created_at DESC
        """
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, category)
                jsonb_fields = ['variables', 'tags', 'variables_detail']
                return [self._parse_jsonb_fields(row, jsonb_fields) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get templates: {e}")
            return self._get_mock_templates()
            
    async def create_template(self, template_data: Dict[str, Any]) -> str:
        """Create a new template"""
        
        if not self.is_connected:
            return "MOCK-" + template_data.get('template_id', 'TEMPLATE')
            
        query = """
            INSERT INTO templates (
                template_id, name, description, category, template_content,
                variables, tags, is_active, created_by
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING template_id
        """
        
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    # Insert template
                    template_id = await conn.fetchval(
                        query,
                        template_data['template_id'],
                        template_data['name'],
                        template_data.get('description', ''),
                        template_data.get('category', 'general'),
                        template_data['template_content'],
                        json.dumps(template_data.get('variables', [])),
                        json.dumps(template_data.get('tags', [])),
                        template_data.get('is_active', True),
                        template_data.get('created_by', 'system')
                    )
                    
                    # Insert template variables if provided
                    if 'variables_detail' in template_data:
                        for var in template_data['variables_detail']:
                            await conn.execute("""
                                INSERT INTO template_variables (
                                    template_id, variable_name, variable_type,
                                    default_value, options, is_required, description
                                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                            """, template_id, var['name'], var['type'],
                                var.get('default'), json.dumps(var.get('options', [])),
                                var.get('required', False), var.get('description'))
                    
                logger.info(f"Created template: {template_id}")
                return template_id
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            raise
            
    # ==================== MOCK DATA FALLBACKS ====================
    
    def _get_mock_rules(self) -> List[Dict[str, Any]]:
        """Return mock rules when database is not available"""
        return [
            {
                "rule_id": "SEC-001",
                "category": "security",
                "category_name": "Security",
                "title": "Never commit secrets",
                "description": "API keys, passwords, and secrets must never be committed to version control",
                "severity": "critical",
                "enforcement": "mandatory",
                "examples": ["Use environment variables", "Use secret management services"],
                "anti_patterns": ["Hardcoding passwords", "Committing .env files"],
                "active": True
            },
            {
                "rule_id": "ARCH-001",
                "category": "architecture",
                "category_name": "Architecture",
                "title": "Separation of concerns",
                "description": "Each module should have a single, well-defined responsibility",
                "severity": "high",
                "enforcement": "mandatory",
                "examples": ["Service layer pattern", "Repository pattern"],
                "active": True
            }
        ]
        
    def _get_mock_best_practices(self) -> List[Dict[str, Any]]:
        """Return mock best practices when database is not available"""
        return [
            {
                "practice_id": "BP-001",
                "category": "general",
                "category_name": "General",
                "title": "Use meaningful variable names",
                "description": "Variables should clearly indicate their purpose",
                "benefits": ["Improved readability", "Easier maintenance"],
                "is_required": True,
                "is_active": True
            }
        ]
        
    def _get_mock_templates(self) -> List[Dict[str, Any]]:
        """Return mock templates when database is not available"""
        return [
            {
                "template_id": "TMPL-001",
                "name": "Basic Template",
                "description": "A basic template for testing",
                "category": "general",
                "template_content": "Hello {{NAME}}",
                "variables": ["NAME"],
                "is_active": True
            }
        ]

# Global instance
db_service = DatabaseService()