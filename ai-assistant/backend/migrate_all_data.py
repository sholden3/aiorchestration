#!/usr/bin/env python3
"""Migrate all best practices and templates from JSON to database"""

import asyncio
import asyncpg
import json
from pathlib import Path
from datetime import datetime

class DataMigrator:
    def __init__(self):
        self.conn = None
        self.stats = {
            'practices_added': 0,
            'practices_skipped': 0,
            'templates_added': 0,
            'templates_skipped': 0,
            'categories_added': 0,
            'errors': []
        }
    
    async def connect(self):
        """Connect to database"""
        try:
            self.conn = await asyncpg.connect(
                host='localhost',
                port=5432,
                user='postgres',
                password='root',
                database='ai_assistant'
            )
            print("Connected to database")
            return True
        except Exception as e:
            print(f"ERROR: Failed to connect: {e}")
            return False
    
    async def ensure_categories(self):
        """Ensure all required categories exist"""
        print("\n=== ENSURING CATEGORIES ===")
        
        categories = [
            ('security', 'Security', 'Security best practices and vulnerabilities'),
            ('performance', 'Performance', 'Performance optimization and monitoring'),
            ('architecture', 'Architecture', 'System design and architecture patterns'),
            ('testing', 'Testing', 'Testing strategies and methodologies'),
            ('general', 'General', 'General development practices'),
            ('requirements-gathering', 'Requirements Gathering', 'Requirements analysis and documentation')
        ]
        
        for cat_id, name, description in categories:
            try:
                exists = await self.conn.fetchval(
                    "SELECT 1 FROM categories WHERE id = $1",
                    cat_id
                )
                
                if not exists:
                    await self.conn.execute("""
                        INSERT INTO categories (id, name, description)
                        VALUES ($1, $2, $3)
                    """, cat_id, name, description)
                    self.stats['categories_added'] += 1
                    print(f"  Added category: {name}")
                else:
                    print(f"  Category exists: {name}")
            except Exception as e:
                self.stats['errors'].append(f"Category {cat_id}: {e}")
                print(f"  ERROR adding {cat_id}: {e}")
    
    async def migrate_best_practices(self):
        """Migrate best practices from JSON file"""
        print("\n=== MIGRATING BEST PRACTICES ===")
        
        json_file = Path('best-practices-data.json')
        if not json_file.exists():
            print("  ERROR: best-practices-data.json not found")
            return
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        practices = data.get('best_practices', [])
        print(f"  Found {len(practices)} best practices to migrate")
        
        for practice in practices:
            try:
                # Check if already exists
                exists = await self.conn.fetchval(
                    "SELECT 1 FROM best_practices WHERE practice_id = $1",
                    practice['practice_id']
                )
                
                if exists:
                    self.stats['practices_skipped'] += 1
                    print(f"  SKIP: {practice['practice_id']} already exists")
                    continue
                
                # Insert the practice
                await self.conn.execute("""
                    INSERT INTO best_practices (
                        practice_id, category, title, description,
                        benefits, implementation_guide, anti_patterns,
                        "references", examples, is_active, is_required, priority
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """,
                    practice['practice_id'],
                    practice.get('category', 'general'),
                    practice['title'],
                    practice['description'],
                    json.dumps(practice.get('benefits', [])),
                    practice.get('implementation_guide', ''),
                    json.dumps(practice.get('anti_patterns', [])),
                    json.dumps(practice.get('references', [])),
                    json.dumps(practice.get('examples', [])),
                    practice.get('is_active', True),
                    practice.get('is_required', False),
                    practice.get('priority')
                )
                
                self.stats['practices_added'] += 1
                print(f"  OK: Added {practice['practice_id']} - {practice['title']}")
                
            except Exception as e:
                self.stats['errors'].append(f"Practice {practice.get('practice_id')}: {e}")
                print(f"  ERROR: {practice.get('practice_id')}: {str(e)[:50]}")
    
    async def migrate_templates(self):
        """Migrate templates from JSON file"""
        print("\n=== MIGRATING TEMPLATES ===")
        
        json_file = Path('templates-data.json')
        if not json_file.exists():
            print("  ERROR: templates-data.json not found")
            return
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        templates = data.get('templates', [])
        print(f"  Found {len(templates)} templates to migrate")
        
        for template in templates:
            try:
                # Check if already exists
                exists = await self.conn.fetchval(
                    "SELECT 1 FROM templates WHERE template_id = $1",
                    template['template_id']
                )
                
                if exists:
                    self.stats['templates_skipped'] += 1
                    print(f"  SKIP: {template['template_id']} already exists")
                    continue
                
                # Insert the template
                await self.conn.execute("""
                    INSERT INTO templates (
                        template_id, name, description, category,
                        template_content, variables, tags, is_active, created_by
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                    template['template_id'],
                    template['name'],
                    template.get('description', ''),
                    template.get('category', 'general'),
                    template['template_content'],
                    json.dumps(template.get('variables', [])),
                    json.dumps(template.get('tags', [])),
                    template.get('is_active', True),
                    template.get('created_by', 'system')
                )
                
                self.stats['templates_added'] += 1
                print(f"  OK: Added {template['template_id']} - {template['name']}")
                
                # Add template variables if specified
                if 'variables' in template and template['variables']:
                    for var_name in template['variables']:
                        try:
                            await self.conn.execute("""
                                INSERT INTO template_variables (
                                    template_id, variable_name, variable_type,
                                    is_required, description
                                ) VALUES ($1, $2, $3, $4, $5)
                                ON CONFLICT (template_id, variable_name) DO NOTHING
                            """,
                                template['template_id'],
                                var_name,
                                'text',
                                False,
                                f"Variable for {template['name']}"
                            )
                        except Exception as ve:
                            print(f"    Warning: Variable {var_name}: {ve}")
                
            except Exception as e:
                self.stats['errors'].append(f"Template {template.get('template_id')}: {e}")
                print(f"  ERROR: {template.get('template_id')}: {str(e)[:50]}")
    
    async def verify_migration(self):
        """Verify the migration was successful"""
        print("\n=== VERIFYING MIGRATION ===")
        
        # Count records
        counts = {
            'categories': await self.conn.fetchval("SELECT COUNT(*) FROM categories"),
            'best_practices': await self.conn.fetchval("SELECT COUNT(*) FROM best_practices"),
            'templates': await self.conn.fetchval("SELECT COUNT(*) FROM templates"),
            'template_variables': await self.conn.fetchval("SELECT COUNT(*) FROM template_variables")
        }
        
        print("\nDatabase Record Counts:")
        for table, count in counts.items():
            print(f"  {table}: {count} records")
        
        # Check specific categories
        print("\nBest Practices by Category:")
        category_counts = await self.conn.fetch("""
            SELECT c.name, COUNT(bp.practice_id) as count
            FROM categories c
            LEFT JOIN best_practices bp ON c.id = bp.category
            GROUP BY c.name
            ORDER BY count DESC
        """)
        
        for row in category_counts:
            print(f"  {row['name']}: {row['count']} practices")
        
        print("\nTemplates by Category:")
        template_counts = await self.conn.fetch("""
            SELECT c.name, COUNT(t.template_id) as count
            FROM categories c
            LEFT JOIN templates t ON c.id = t.category
            GROUP BY c.name
            ORDER BY count DESC
        """)
        
        for row in template_counts:
            print(f"  {row['name']}: {row['count']} templates")
    
    async def run_migration(self):
        """Run the complete migration"""
        print("=" * 60)
        print("DATA MIGRATION TO POSTGRESQL")
        print("=" * 60)
        
        if not await self.connect():
            return False
        
        try:
            # Run migrations
            await self.ensure_categories()
            await self.migrate_best_practices()
            await self.migrate_templates()
            await self.verify_migration()
            
            # Print summary
            print("\n" + "=" * 60)
            print("MIGRATION SUMMARY")
            print("=" * 60)
            print(f"Categories added: {self.stats['categories_added']}")
            print(f"Best practices added: {self.stats['practices_added']}")
            print(f"Best practices skipped: {self.stats['practices_skipped']}")
            print(f"Templates added: {self.stats['templates_added']}")
            print(f"Templates skipped: {self.stats['templates_skipped']}")
            
            if self.stats['errors']:
                print(f"\nErrors encountered: {len(self.stats['errors'])}")
                for error in self.stats['errors'][:5]:
                    print(f"  - {error}")
            else:
                print("\nNo errors encountered!")
            
            return len(self.stats['errors']) == 0
            
        except Exception as e:
            print(f"\nFATAL ERROR: {e}")
            return False
        finally:
            await self.conn.close()

async def main():
    migrator = DataMigrator()
    success = await migrator.run_migration()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)