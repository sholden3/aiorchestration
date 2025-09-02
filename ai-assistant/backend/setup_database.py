"""
Database Setup Script for AI Assistant
Creates database and tables if they don't exist
"""

import asyncio
import asyncpg
import sys
import getpass
from pathlib import Path

async def create_database():
    """Create the ai_assistant database if it doesn't exist"""
    
    print("PostgreSQL Database Setup for AI Assistant")
    print("-" * 50)
    
    # Get credentials
    print("\nPlease enter PostgreSQL credentials:")
    username = input("Username (default: postgres): ").strip() or "postgres"
    password = getpass.getpass("Password: ")
    host = input("Host (default: localhost): ").strip() or "localhost"
    port = input("Port (default: 5432): ").strip() or "5432"
    
    # First connect to the default 'postgres' database
    try:
        print(f"\nConnecting to PostgreSQL as {username}@{host}:{port}...")
        
        # Connect to postgres database to create our database
        conn = await asyncpg.connect(
            host=host,
            port=int(port),
            user=username,
            password=password,
            database='postgres'
        )
        
        print("Connected successfully!")
        
        # Check if database exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = 'ai_assistant'"
        )
        
        if not exists:
            print("\nCreating database 'ai_assistant'...")
            await conn.execute('CREATE DATABASE ai_assistant')
            print("Database created successfully!")
        else:
            print("\nDatabase 'ai_assistant' already exists.")
        
        await conn.close()
        
        # Now connect to our database and create tables
        print("\nConnecting to ai_assistant database...")
        conn = await asyncpg.connect(
            host=host,
            port=int(port),
            user=username,
            password=password,
            database='ai_assistant'
        )
        
        # Create tables
        print("\nCreating tables...")
        
        # Rules table
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
        print("✓ Rules table created")
        
        # Practices table
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
        print("✓ Practices table created")
        
        # Templates table
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
        print("✓ Templates table created")
        
        # Cache table
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
        print("✓ Cache table created")
        
        # Audit log table
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
        print("✓ Audit log table created")
        
        await conn.close()
        
        # Save connection string to config
        connection_string = f"postgresql://{username}:{password}@{host}:{port}/ai_assistant"
        
        print("\n" + "=" * 50)
        print("Database setup completed successfully!")
        print("\nConnection string (add to your environment or config):")
        print(f"DATABASE_URL={connection_string}")
        
        # Optionally save to .env file
        save_env = input("\nSave to .env file? (y/n): ").strip().lower()
        if save_env == 'y':
            env_file = Path(__file__).parent / '.env'
            with open(env_file, 'a') as f:
                f.write(f"\nDATABASE_URL={connection_string}\n")
            print(f"Saved to {env_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure PostgreSQL service is running")
        print("2. Check your username and password")
        print("3. Ensure PostgreSQL is listening on the specified host/port")
        print("4. Check Windows Firewall settings")
        return False

if __name__ == "__main__":
    success = asyncio.run(create_database())
    sys.exit(0 if success else 1)