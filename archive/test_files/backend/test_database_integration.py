#!/usr/bin/env python3
"""Comprehensive database integration tests"""

import asyncio
import asyncpg
import json
import requests
from typing import List, Dict, Any
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8001"
DB_URL = "postgresql://postgres:root@localhost:5432/ai_assistant"

class TestDatabaseIntegration:
    def __init__(self):
        self.conn = None
        self.errors = []
        self.successes = []
    
    async def connect(self):
        """Connect to database"""
        try:
            self.conn = await asyncpg.connect(DB_URL)
            return True
        except Exception as e:
            self.errors.append(f"Database connection failed: {e}")
            return False
    
    async def test_database_schema(self):
        """Test database schema completeness"""
        print("\n=== TESTING DATABASE SCHEMA ===")
        
        required_tables = ['categories', 'rules', 'best_practices', 'templates', 'template_variables']
        
        for table in required_tables:
            exists = await self.conn.fetchval(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = $1)",
                table
            )
            if exists:
                self.successes.append(f"Table '{table}' exists")
                print(f"  [OK] Table '{table}' exists")
            else:
                self.errors.append(f"Table '{table}' missing")
                print(f"  [X] Table '{table}' missing")
        
        # Check JSONB columns
        jsonb_checks = [
            ('rules', 'examples'),
            ('rules', 'anti_patterns'),
            ('best_practices', 'benefits'),
            ('best_practices', 'anti_patterns'),
            ('best_practices', 'references'),
            ('best_practices', 'examples'),
            ('templates', 'variables'),
            ('templates', 'tags')
        ]
        
        for table, column in jsonb_checks:
            data_type = await self.conn.fetchval(
                """SELECT data_type FROM information_schema.columns 
                   WHERE table_name = $1 AND column_name = $2""",
                table, column
            )
            if data_type == 'jsonb':
                self.successes.append(f"{table}.{column} is JSONB")
                print(f"  [OK] {table}.{column} is JSONB")
            else:
                self.errors.append(f"{table}.{column} is {data_type}, should be JSONB")
                print(f"  [X] {table}.{column} is {data_type}, should be JSONB")
    
    def test_api_endpoints(self):
        """Test all API endpoints"""
        print("\n=== TESTING API ENDPOINTS ===")
        
        endpoints = [
            ('/api/rules/', 'Rules API'),
            ('/api/practices/', 'Best Practices API'),
            ('/api/templates/', 'Templates API'),
            ('/api/rules/stats', 'Rules Statistics'),
            ('/api/practices/stats', 'Practices Statistics'),
            ('/api/templates/stats', 'Templates Statistics')
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        self.successes.append(f"{name} working")
                        print(f"  [OK] {name}: {response.status_code} - {data.get('count', 'N/A')} items")
                    else:
                        self.errors.append(f"{name} returned success=false")
                        print(f"  [X] {name}: success=false")
                else:
                    self.errors.append(f"{name} returned {response.status_code}")
                    print(f"  [X] {name}: {response.status_code}")
            except Exception as e:
                self.errors.append(f"{name} failed: {e}")
                print(f"  [X] {name}: {str(e)[:50]}")
    
    def test_json_parsing(self):
        """Test JSON field parsing"""
        print("\n=== TESTING JSON PARSING ===")
        
        # Test rules endpoint
        response = requests.get(f"{API_BASE_URL}/api/rules/")
        if response.status_code == 200:
            data = response.json()
            if data.get('rules'):
                rule = data['rules'][0]
                
                # Check if JSON fields are properly parsed
                json_fields = ['examples', 'anti_patterns']
                for field in json_fields:
                    value = rule.get(field)
                    if isinstance(value, list):
                        self.successes.append(f"Rules.{field} is properly parsed as list")
                        print(f"  [OK] Rules.{field} is list with {len(value)} items")
                    elif isinstance(value, str):
                        self.errors.append(f"Rules.{field} is still a string")
                        print(f"  [X] Rules.{field} is string: {value[:30]}...")
                    else:
                        print(f"  [?] Rules.{field} is {type(value)}")
        
        # Test practices endpoint
        response = requests.get(f"{API_BASE_URL}/api/practices/")
        if response.status_code == 200:
            data = response.json()
            if data.get('practices'):
                practice = data['practices'][0]
                
                json_fields = ['benefits', 'anti_patterns', 'references', 'examples']
                for field in json_fields:
                    value = practice.get(field)
                    if isinstance(value, list):
                        self.successes.append(f"Practices.{field} is properly parsed as list")
                        print(f"  [OK] Practices.{field} is list with {len(value)} items")
                    elif isinstance(value, str):
                        self.errors.append(f"Practices.{field} is still a string")
                        print(f"  [X] Practices.{field} is string: {value[:30]}...")
    
    async def test_data_integrity(self):
        """Test data integrity and foreign keys"""
        print("\n=== TESTING DATA INTEGRITY ===")
        
        # Check if all categories referenced in tables exist
        orphaned = await self.conn.fetch("""
            SELECT DISTINCT r.category 
            FROM rules r 
            LEFT JOIN categories c ON r.category = c.id 
            WHERE c.id IS NULL AND r.category IS NOT NULL
        """)
        
        if not orphaned:
            self.successes.append("No orphaned rules")
            print("  [OK] No orphaned rules (all categories exist)")
        else:
            self.errors.append(f"{len(orphaned)} orphaned rules")
            print(f"  [X] {len(orphaned)} rules reference non-existent categories")
        
        # Check data counts
        counts = {
            'categories': await self.conn.fetchval("SELECT COUNT(*) FROM categories"),
            'rules': await self.conn.fetchval("SELECT COUNT(*) FROM rules"),
            'best_practices': await self.conn.fetchval("SELECT COUNT(*) FROM best_practices"),
            'templates': await self.conn.fetchval("SELECT COUNT(*) FROM templates")
        }
        
        print("\n  Data Counts:")
        for table, count in counts.items():
            print(f"    {table}: {count} records")
            if count > 0:
                self.successes.append(f"{table} has data")
            else:
                self.errors.append(f"{table} is empty")
    
    def test_api_filters(self):
        """Test API filtering capabilities"""
        print("\n=== TESTING API FILTERS ===")
        
        # Test category filter
        response = requests.get(f"{API_BASE_URL}/api/rules/?category=security")
        if response.status_code == 200:
            data = response.json()
            security_rules = data.get('count', 0)
            print(f"  [OK] Category filter: {security_rules} security rules")
            self.successes.append("Category filter working")
        
        # Test severity filter
        response = requests.get(f"{API_BASE_URL}/api/rules/?severity=critical")
        if response.status_code == 200:
            data = response.json()
            critical_rules = data.get('count', 0)
            print(f"  [OK] Severity filter: {critical_rules} critical rules")
            self.successes.append("Severity filter working")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("=" * 50)
        print("DATABASE INTEGRATION TEST SUITE")
        print("=" * 50)
        
        # Connect to database
        if not await self.connect():
            print("\n[FATAL] Cannot connect to database")
            return
        
        # Run tests
        await self.test_database_schema()
        self.test_api_endpoints()
        self.test_json_parsing()
        await self.test_data_integrity()
        self.test_api_filters()
        
        # Close connection
        await self.conn.close()
        
        # Summary
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        print(f"Successes: {len(self.successes)}")
        print(f"Errors: {len(self.errors)}")
        
        if self.errors:
            print("\nErrors found:")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("\nALL TESTS PASSED!")
        
        return len(self.errors) == 0

async def main():
    tester = TestDatabaseIntegration()
    success = await tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)