#!/usr/bin/env python3
"""Verify data integrity after migration"""

import asyncio
import asyncpg
import json
import requests

class DataIntegrityVerifier:
    def __init__(self):
        self.conn = None
        self.api_base = "http://localhost:8001"
        self.issues = []
        self.checks_passed = 0
        self.checks_failed = 0
    
    async def connect(self):
        """Connect to database"""
        self.conn = await asyncpg.connect(
            'postgresql://postgres:root@localhost:5432/ai_assistant'
        )
    
    async def check_jsonb_columns(self):
        """Verify all JSONB columns are properly stored"""
        print("\n=== CHECKING JSONB DATA INTEGRITY ===")
        
        # Check best practices JSONB fields
        practices = await self.conn.fetch("""
            SELECT practice_id, benefits, anti_patterns, "references", examples
            FROM best_practices
        """)
        
        for practice in practices:
            for field in ['benefits', 'anti_patterns', 'references', 'examples']:
                value = practice[field]
                if value is not None:
                    if isinstance(value, str):
                        # AsyncPG returns JSONB as strings - try to parse to verify it's valid JSON
                        try:
                            parsed = json.loads(value)
                            if isinstance(parsed, (list, dict)):
                                self.checks_passed += 1  # Valid JSON data
                            else:
                                self.issues.append(f"Practice {practice['practice_id']}.{field} is not array/object JSON")
                                self.checks_failed += 1
                        except json.JSONDecodeError:
                            self.issues.append(f"Practice {practice['practice_id']}.{field} is not valid JSON")
                            self.checks_failed += 1
                    elif isinstance(value, (list, dict)):
                        self.checks_passed += 1
                    else:
                        self.issues.append(f"Practice {practice['practice_id']}.{field} unexpected type: {type(value)}")
                        self.checks_failed += 1
        
        print(f"  Checked {len(practices)} best practices JSONB fields")
        
        # Check templates JSONB fields
        templates = await self.conn.fetch("""
            SELECT template_id, variables, tags
            FROM templates
        """)
        
        for template in templates:
            for field in ['variables', 'tags']:
                value = template[field]
                if value is not None:
                    if isinstance(value, str):
                        # AsyncPG returns JSONB as strings - try to parse to verify it's valid JSON
                        try:
                            parsed = json.loads(value)
                            if isinstance(parsed, (list, dict)):
                                self.checks_passed += 1  # Valid JSON data
                            else:
                                self.issues.append(f"Template {template['template_id']}.{field} is not array/object JSON")
                                self.checks_failed += 1
                        except json.JSONDecodeError:
                            self.issues.append(f"Template {template['template_id']}.{field} is not valid JSON")
                            self.checks_failed += 1
                    elif isinstance(value, (list, dict)):
                        self.checks_passed += 1
        
        print(f"  Checked {len(templates)} templates JSONB fields")
    
    async def check_foreign_keys(self):
        """Verify all foreign key relationships"""
        print("\n=== CHECKING FOREIGN KEY INTEGRITY ===")
        
        # Check rules category references
        orphaned_rules = await self.conn.fetch("""
            SELECT r.rule_id, r.category
            FROM rules r
            LEFT JOIN categories c ON r.category = c.id
            WHERE r.category IS NOT NULL AND c.id IS NULL
        """)
        
        if orphaned_rules:
            for rule in orphaned_rules:
                self.issues.append(f"Rule {rule['rule_id']} references non-existent category {rule['category']}")
                self.checks_failed += 1
        else:
            print("  [OK] All rules have valid category references")
            self.checks_passed += 1
        
        # Check template_variables references
        orphaned_vars = await self.conn.fetch("""
            SELECT tv.template_id, COUNT(*) as count
            FROM template_variables tv
            LEFT JOIN templates t ON tv.template_id = t.template_id
            WHERE t.template_id IS NULL
            GROUP BY tv.template_id
        """)
        
        if orphaned_vars:
            for var in orphaned_vars:
                self.issues.append(f"Template variables for non-existent template {var['template_id']}")
                self.checks_failed += 1
        else:
            print("  [OK] All template variables have valid template references")
            self.checks_passed += 1
    
    def check_api_responses(self):
        """Verify API responses match database"""
        print("\n=== CHECKING API RESPONSES ===")
        
        # Test rules API
        response = requests.get(f"{self.api_base}/api/rules/")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"  [OK] Rules API: {data['count']} rules")
                self.checks_passed += 1
                
                # Check JSON parsing
                if data['rules']:
                    rule = data['rules'][0]
                    if isinstance(rule.get('examples'), list):
                        print("  [OK] Rules JSON fields properly parsed")
                        self.checks_passed += 1
                    else:
                        self.issues.append("Rules JSON fields not parsed correctly")
                        self.checks_failed += 1
        else:
            self.issues.append(f"Rules API failed: {response.status_code}")
            self.checks_failed += 1
        
        # Test filtering
        response = requests.get(f"{self.api_base}/api/rules/?severity=critical")
        if response.status_code == 200:
            data = response.json()
            critical_count = data['count']
            print(f"  [OK] Severity filter working: {critical_count} critical rules")
            self.checks_passed += 1
        
        # Test statistics endpoints
        for endpoint in ['/api/rules/stats', '/api/practices/stats', '/api/templates/stats']:
            response = requests.get(f"{self.api_base}{endpoint}")
            if response.status_code == 200:
                print(f"  [OK] {endpoint} working")
                self.checks_passed += 1
            else:
                self.issues.append(f"{endpoint} failed: {response.status_code}")
                self.checks_failed += 1
    
    async def check_data_completeness(self):
        """Verify all expected data is present"""
        print("\n=== CHECKING DATA COMPLETENESS ===")
        
        # Expected minimums
        expectations = {
            'categories': 5,
            'rules': 3,
            'best_practices': 20,
            'templates': 25,
            'template_variables': 100
        }
        
        for table, expected_min in expectations.items():
            count = await self.conn.fetchval(f"SELECT COUNT(*) FROM {table}")
            if count >= expected_min:
                print(f"  [OK] {table}: {count} records (>= {expected_min})")
                self.checks_passed += 1
            else:
                self.issues.append(f"{table} has {count} records, expected >= {expected_min}")
                self.checks_failed += 1
        
        # Check priority distribution in best practices
        priority_counts = await self.conn.fetch("""
            SELECT priority, COUNT(*) as count
            FROM best_practices
            GROUP BY priority
            ORDER BY priority
        """)
        
        print("\n  Priority Distribution:")
        for row in priority_counts:
            priority = row['priority'] or 'None'
            print(f"    {priority}: {row['count']} practices")
    
    async def check_required_practices(self):
        """Verify critical required practices exist"""
        print("\n=== CHECKING REQUIRED PRACTICES ===")
        
        critical_practices = [
            ('Input Validation', 'security'),
            ('Secrets Management', 'security'),
            ('Code Reviews', 'general'),
            ('Health Checks', 'architecture')
        ]
        
        for title_part, category in critical_practices:
            exists = await self.conn.fetchval("""
                SELECT COUNT(*)
                FROM best_practices
                WHERE title ILIKE $1 AND category = $2
            """, f'%{title_part}%', category)
            
            if exists:
                print(f"  [OK] Found: {title_part} in {category}")
                self.checks_passed += 1
            else:
                self.issues.append(f"Missing critical practice: {title_part} in {category}")
                self.checks_failed += 1
    
    async def run_verification(self):
        """Run all verification checks"""
        print("=" * 60)
        print("DATA INTEGRITY VERIFICATION")
        print("=" * 60)
        
        await self.connect()
        
        try:
            # Run all checks
            await self.check_jsonb_columns()
            await self.check_foreign_keys()
            self.check_api_responses()
            await self.check_data_completeness()
            await self.check_required_practices()
            
            # Summary
            print("\n" + "=" * 60)
            print("VERIFICATION SUMMARY")
            print("=" * 60)
            print(f"Checks Passed: {self.checks_passed}")
            print(f"Checks Failed: {self.checks_failed}")
            
            if self.issues:
                print(f"\nIssues Found ({len(self.issues)}):")
                for issue in self.issues[:10]:
                    print(f"  - {issue}")
                if len(self.issues) > 10:
                    print(f"  ... and {len(self.issues) - 10} more")
            else:
                print("\nALL CHECKS PASSED! Data integrity verified.")
            
            return len(self.issues) == 0
            
        finally:
            await self.conn.close()

async def main():
    verifier = DataIntegrityVerifier()
    success = await verifier.run_verification()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)